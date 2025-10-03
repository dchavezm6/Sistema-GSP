from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse, HttpResponseForbidden
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from .models import ServiceRequest, RequestImage, ServiceType, ServiceArea, RequestComment, RequestStatusHistory
from .forms import ServiceRequestForm, RequestImageForm, RequestCommentForm, RequestStatusForm, RequestSearchForm
from apps.authentication.decorators import role_required

class ServiceRequestListView(LoginRequiredMixin, ListView):
    """Vista para listar solicitudes"""
    model = ServiceRequest
    template_name = 'requests/request_list.html'
    context_object_name = 'requests'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = ServiceRequest.objects.select_related(
            'citizen', 'service_type', 'service_area', 'assigned_to'
        ).prefetch_related('images')
        
        # Filtrar por usuario si es ciudadano
        if self.request.user.role == 'CITIZEN':
            queryset = queryset.filter(citizen=self.request.user)
        
        # Aplicar filtros de búsqueda
        form = RequestSearchForm(self.request.GET)
        if form.is_valid():
            search_term = form.cleaned_data.get('search_term')
            if search_term:
                queryset = queryset.filter(
                    Q(ticket_number__icontains=search_term) |
                    Q(title__icontains=search_term) |
                    Q(description__icontains=search_term)
                )
            
            status = form.cleaned_data.get('status')
            if status:
                queryset = queryset.filter(status=status)
            
            service_type = form.cleaned_data.get('service_type')
            if service_type:
                queryset = queryset.filter(service_type=service_type)
            
            service_area = form.cleaned_data.get('service_area')
            if service_area:
                queryset = queryset.filter(service_area=service_area)
            
            date_from = form.cleaned_data.get('date_from')
            if date_from:
                queryset = queryset.filter(created_at__date__gte=date_from)
            
            date_to = form.cleaned_data.get('date_to')
            if date_to:
                queryset = queryset.filter(created_at__date__lte=date_to)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = RequestSearchForm(self.request.GET)
        context['total_requests'] = self.get_queryset().count()
        
        # Estadísticas básicas
        if self.request.user.role == 'CITIZEN':
            user_requests = ServiceRequest.objects.filter(citizen=self.request.user)
            context['stats'] = {
                'pending': user_requests.filter(status='PENDING').count(),
                'in_progress': user_requests.filter(status='IN_PROGRESS').count(),
                'completed': user_requests.filter(status='COMPLETED').count(),
            }
        else:
            # Estadísticas para personal municipal
            context['stats'] = {
                'pending': ServiceRequest.objects.filter(status='PENDING').count(),
                'in_progress': ServiceRequest.objects.filter(status='IN_PROGRESS').count(),
                'overdue': ServiceRequest.objects.filter(
                    expected_completion__lt=timezone.now().date(),
                    status__in=['PENDING', 'IN_PROGRESS']
                ).count(),
            }
        
        return context

class ServiceRequestDetailView(LoginRequiredMixin, DetailView):
    """Vista para ver detalles de una solicitud"""
    model = ServiceRequest
    template_name = 'requests/request_detail.html'
    context_object_name = 'request'
    slug_field = 'ticket_number'
    slug_url_kwarg = 'ticket_number'
    
    def get_queryset(self):
        queryset = ServiceRequest.objects.select_related(
            'citizen', 'service_type', 'service_area', 'assigned_to', 'reviewed_by'
        ).prefetch_related(
            'images', 'comments__user', 'status_history__changed_by'
        )
        
        # Los ciudadanos solo pueden ver sus propias solicitudes
        if self.request.user.role == 'CITIZEN':
            queryset = queryset.filter(citizen=self.request.user)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Formularios para agregar contenido
        context['comment_form'] = RequestCommentForm(
            user=self.request.user,
            request_obj=self.object
        )
        context['image_form'] = RequestImageForm(
            user=self.request.user,
            request_obj=self.object
        )
        
        # Formulario para cambio de estado (solo personal municipal)
        if self.request.user.role in ['ADMIN', 'MANAGER', 'TECHNICIAN']:
            context['status_form'] = RequestStatusForm(
                user=self.request.user,
                instance=self.object
            )
        
        # Comentarios (filtrar internos para ciudadanos)
        comments = self.object.comments.select_related('user')
        if self.request.user.role == 'CITIZEN':
            comments = comments.filter(is_internal=False)
        context['comments'] = comments.order_by('created_at')
        
        return context

class ServiceRequestCreateView(LoginRequiredMixin, CreateView):
    """Vista para crear nuevas solicitudes"""
    model = ServiceRequest
    form_class = ServiceRequestForm
    template_name = 'requests/request_create.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'Solicitud creada exitosamente. Número de ticket: {self.object.ticket_number}'
        )
        return response
    
    def get_success_url(self):
        return reverse('requests:detail', kwargs={'ticket_number': self.object.ticket_number})

@login_required
def add_request_image(request, ticket_number):
    """Vista para agregar imágenes a una solicitud"""
    service_request = get_object_or_404(ServiceRequest, ticket_number=ticket_number)
    
    # Verificar permisos
    if (request.user.role == 'CITIZEN' and service_request.citizen != request.user) or \
       (request.user.role not in ['CITIZEN', 'ADMIN', 'MANAGER', 'TECHNICIAN']):
        return HttpResponseForbidden("No tienes permisos para agregar imágenes a esta solicitud.")
    
    if request.method == 'POST':
        form = RequestImageForm(
            request.POST, 
            request.FILES,
            user=request.user,
            request_obj=service_request
        )
        if form.is_valid():
            form.save()
            messages.success(request, 'Imagen agregada exitosamente.')
            return redirect('requests:detail', ticket_number=ticket_number)
    
    return redirect('requests:detail', ticket_number=ticket_number)

@login_required
def add_request_comment(request, ticket_number):
    """Vista para agregar comentarios a una solicitud"""
    service_request = get_object_or_404(ServiceRequest, ticket_number=ticket_number)
    
    # Verificar permisos
    if request.user.role == 'CITIZEN' and service_request.citizen != request.user:
        return HttpResponseForbidden("No tienes permisos para comentar en esta solicitud.")
    
    if request.method == 'POST':
        form = RequestCommentForm(
            request.POST,
            user=request.user,
            request_obj=service_request
        )
        if form.is_valid():
            form.save()
            messages.success(request, 'Comentario agregado exitosamente.')
            return redirect('requests:detail', ticket_number=ticket_number)
    
    return redirect('requests:detail', ticket_number=ticket_number)

@login_required
@role_required(['ADMIN', 'MANAGER', 'TECHNICIAN'])
def update_request_status(request, ticket_number):
    """Vista para actualizar el estado de una solicitud"""
    service_request = get_object_or_404(ServiceRequest, ticket_number=ticket_number)
    
    if request.method == 'POST':
        form = RequestStatusForm(
            request.POST,
            instance=service_request,
            user=request.user
        )
        if form.is_valid():
            # Guardar estado anterior para el historial
            original_status = service_request.status
            updated_request = form.save()
            
            # Crear entrada en el historial
            RequestStatusHistory.objects.create(
                request=updated_request,
                from_status=original_status,
                to_status=updated_request.status,
                changed_by=request.user,
                reason=form.cleaned_data['reason']
            )
            
            messages.success(request, 'Estado de la solicitud actualizado exitosamente.')
            return redirect('requests:detail', ticket_number=ticket_number)
    
    return redirect('requests:detail', ticket_number=ticket_number)

@login_required
def cancel_request(request, ticket_number):
    """Vista para cancelar una solicitud (solo ciudadanos)"""
    service_request = get_object_or_404(ServiceRequest, ticket_number=ticket_number)
    
    # Solo el ciudadano propietario puede cancelar
    if service_request.citizen != request.user:
        return HttpResponseForbidden("No tienes permisos para cancelar esta solicitud.")
    
    # Solo se puede cancelar en ciertos estados
    if not service_request.can_be_cancelled_by_citizen():
        messages.error(request, 'Esta solicitud no puede ser cancelada en su estado actual.')
        return redirect('requests:detail', ticket_number=ticket_number)
    
    if request.method == 'POST':
        original_status = service_request.status
        service_request.status = 'CANCELLED'
        service_request.save()
        
        # Crear entrada en el historial
        RequestStatusHistory.objects.create(
            request=service_request,
            from_status=original_status,
            to_status='CANCELLED',
            changed_by=request.user,
            reason='Cancelada por el ciudadano'
        )
        
        messages.success(request, 'Solicitud cancelada exitosamente.')
    
    return redirect('requests:detail', ticket_number=ticket_number)

@login_required
def dashboard_stats_api(request):
    """API para obtener estadísticas del dashboard"""
    if request.user.role == 'CITIZEN':
        user_requests = ServiceRequest.objects.filter(citizen=request.user)
        stats = {
            'total': user_requests.count(),
            'pending': user_requests.filter(status='PENDING').count(),
            'in_progress': user_requests.filter(status='IN_PROGRESS').count(),
            'completed': user_requests.filter(status='COMPLETED').count(),
        }
    else:
        # Estadísticas para personal municipal
        stats = {
            'total': ServiceRequest.objects.count(),
            'pending': ServiceRequest.objects.filter(status='PENDING').count(),
            'in_progress': ServiceRequest.objects.filter(status='IN_PROGRESS').count(),
            'completed': ServiceRequest.objects.filter(status='COMPLETED').count(),
            'overdue': ServiceRequest.objects.filter(
                expected_completion__lt=timezone.now().date(),
                status__in=['PENDING', 'IN_PROGRESS']
            ).count(),
        }
    
    return JsonResponse(stats)