from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView
from django.urls import reverse_lazy
from django.http import HttpResponseForbidden
from django.db.models import Q, Count
from django.utils import timezone
from .models import TaskAssignment, TaskUpdate, Notification
from .forms import TaskAssignmentForm, TaskUpdateForm, TaskAcceptForm, TaskCompleteForm
from apps.requests.models import ServiceRequest
from apps.authentication.decorators import role_required

class TaskAssignmentListView(LoginRequiredMixin, ListView):
    """Vista para listar asignaciones"""
    model = TaskAssignment
    template_name = 'assignments/assignment_list.html'
    context_object_name = 'assignments'
    paginate_by = 15
    
    def get_queryset(self):
        queryset = TaskAssignment.objects.select_related(
            'request', 'assigned_to', 'assigned_by'
        )
        
        # Filtrar según el rol del usuario
        if self.request.user.role == 'TECHNICIAN':
            queryset = queryset.filter(assigned_to=self.request.user)
        elif self.request.user.role == 'CITIZEN':
            # Los ciudadanos no deberían acceder a esta vista
            queryset = queryset.none()
        
        # Filtros adicionales
        status_filter = self.request.GET.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-assigned_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.user.role == 'TECHNICIAN':
            my_assignments = TaskAssignment.objects.filter(assigned_to=self.request.user)
            context['stats'] = {
                'assigned': my_assignments.filter(status='ASSIGNED').count(),
                'in_progress': my_assignments.filter(status='IN_PROGRESS').count(),
                'completed': my_assignments.filter(status='COMPLETED').count(),
            }
        else:
            context['stats'] = {
                'assigned': TaskAssignment.objects.filter(status='ASSIGNED').count(),
                'in_progress': TaskAssignment.objects.filter(status='IN_PROGRESS').count(),
                'overdue': TaskAssignment.objects.filter(
                    estimated_completion__lt=timezone.now(),
                    status__in=['ASSIGNED', 'IN_PROGRESS']
                ).count(),
            }
        
        return context

class TaskAssignmentDetailView(LoginRequiredMixin, DetailView):
    """Vista para ver detalles de una asignación"""
    model = TaskAssignment
    template_name = 'assignments/assignment_detail.html'
    context_object_name = 'assignment'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Formularios según el rol
        if self.request.user == self.object.assigned_to:
            if self.object.status == 'ASSIGNED':
                context['accept_form'] = TaskAcceptForm()
            
            if self.object.status in ['ACCEPTED', 'IN_PROGRESS']:
                context['update_form'] = TaskUpdateForm(
                    assignment=self.object,
                    user=self.request.user
                )
            
            if self.object.status == 'IN_PROGRESS':
                context['complete_form'] = TaskCompleteForm()
        
        # Actualizaciones de la tarea
        context['updates'] = self.object.updates.select_related('updated_by').order_by('-created_at')
        
        return context

@login_required
@role_required(['ADMIN', 'MANAGER'])
def create_assignment(request, ticket_number):
    """Vista para crear una asignación"""
    service_request = get_object_or_404(ServiceRequest, ticket_number=ticket_number)
    
    # Verificar que no tenga ya una asignación
    if hasattr(service_request, 'assignment'):
        messages.warning(request, 'Esta solicitud ya tiene una asignación.')
        return redirect('requests:detail', ticket_number=ticket_number)
    
    if request.method == 'POST':
        form = TaskAssignmentForm(
            request.POST,
            request_obj=service_request,
            user=request.user
        )
        if form.is_valid():
            form.save()
            messages.success(request, 'Tarea asignada exitosamente.')
            return redirect('requests:detail', ticket_number=ticket_number)
    else:
        form = TaskAssignmentForm(request_obj=service_request, user=request.user)
    
    return render(request, 'assignments/assignment_create.html', {
        'form': form,
        'service_request': service_request
    })

@login_required
def accept_assignment(request, pk):
    """Vista para que un técnico acepte una asignación"""
    assignment = get_object_or_404(TaskAssignment, pk=pk)
    
    # Verificar que sea el técnico asignado
    if request.user != assignment.assigned_to:
        return HttpResponseForbidden("No tienes permisos para aceptar esta tarea.")
    
    if request.method == 'POST':
        if assignment.status == 'ASSIGNED':
            assignment.status = 'ACCEPTED'
            assignment.accepted_at = timezone.now()
            assignment.save()
            messages.success(request, 'Tarea aceptada exitosamente.')
        else:
            messages.warning(request, 'Esta tarea ya no puede ser aceptada.')
    
    return redirect('assignments:detail', pk=pk)

@login_required
def start_assignment(request, pk):
    """Vista para iniciar una asignación"""
    assignment = get_object_or_404(TaskAssignment, pk=pk)
    
    if request.user != assignment.assigned_to:
        return HttpResponseForbidden("No tienes permisos para iniciar esta tarea.")
    
    if request.method == 'POST':
        if assignment.status in ['ASSIGNED', 'ACCEPTED']:
            assignment.status = 'IN_PROGRESS'
            assignment.started_at = timezone.now()
            assignment.save()
            
            # Actualizar solicitud
            assignment.request.status = 'IN_PROGRESS'
            assignment.request.save()
            
            messages.success(request, 'Tarea iniciada exitosamente.')
        else:
            messages.warning(request, 'Esta tarea no puede ser iniciada.')
    
    return redirect('assignments:detail', pk=pk)

@login_required
def add_task_update(request, pk):
    """Vista para agregar actualización de progreso"""
    assignment = get_object_or_404(TaskAssignment, pk=pk)
    
    if request.user != assignment.assigned_to:
        return HttpResponseForbidden("No tienes permisos para actualizar esta tarea.")
    
    if request.method == 'POST':
        form = TaskUpdateForm(
            request.POST,
            assignment=assignment,
            user=request.user
        )
        if form.is_valid():
            form.save()
            messages.success(request, 'Actualización registrada exitosamente.')
            return redirect('assignments:detail', pk=pk)
    
    return redirect('assignments:detail', pk=pk)


@login_required
def complete_assignment(request, pk):
    """Vista para completar una asignación"""
    assignment = get_object_or_404(TaskAssignment, pk=pk)

    if request.user != assignment.assigned_to:
        return HttpResponseForbidden("No tienes permisos para completar esta tarea.")

    if request.method == 'POST':
        form = TaskCompleteForm(request.POST)
        if form.is_valid():
            assignment.status = 'COMPLETED'
            assignment.actual_completion = timezone.now()
            assignment.actual_hours = form.cleaned_data['actual_hours']
            assignment.notes = form.cleaned_data['notes']

            # Guardar materiales utilizados en materials_needed (reutilizamos el campo)
            if form.cleaned_data.get('materials_used'):
                assignment.materials_needed = form.cleaned_data['materials_used']

            assignment.save()

            # Actualizar solicitud
            assignment.request.status = 'COMPLETED'
            assignment.request.completed_at = timezone.now()
            assignment.request.save()

            messages.success(request, 'Tarea completada exitosamente.')
            return redirect('assignments:detail', pk=pk)

    return redirect('assignments:detail', pk=pk)

@login_required
def notification_list(request):
    """Vista para listar notificaciones del usuario"""
    notifications = Notification.objects.filter(
        recipient=request.user
    ).select_related('related_request').order_by('-created_at')[:20]
    
    # Marcar como leídas las notificaciones vistas
    unread = notifications.filter(is_read=False)
    unread.update(is_read=True)
    
    return render(request, 'assignments/notification_list.html', {
        'notifications': notifications
    })