from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, TemplateView
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Q, Avg  # Asegúrate de que Avg esté aquí
from django.utils import timezone
from datetime import timedelta
import json

from .models import Report, CitizenSatisfaction
from .forms import ReportFilterForm, SatisfactionSurveyForm
from .utils.statistics import ReportGenerator, ChartDataGenerator
from apps.requests.models import ServiceRequest
from apps.authentication.decorators import role_required

class DashboardReportsView(LoginRequiredMixin, TemplateView):
    """Dashboard principal de reportes"""
    template_name = 'reports/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Verificar permisos
        if self.request.user.role not in ['ADMIN', 'AUTHORITY', 'MANAGER']:
            messages.error(self.request, 'No tiene permisos para ver reportes.')
            return context
        
        # Último mes por defecto
        date_to = timezone.now().date()
        date_from = date_to - timedelta(days=30)
        
        generator = ReportGenerator(date_from, date_to)
        chart_generator = ChartDataGenerator()
        
        # Estadísticas generales
        context['general_stats'] = generator.get_general_statistics()
        
        # Datos para gráficos
        by_service = generator.get_requests_by_service_type()
        context['service_chart_data'] = json.dumps(
            chart_generator.prepare_pie_chart_data(by_service, 'service_type__name')
        )
        
        by_area = generator.get_requests_by_area()
        context['area_chart_data'] = json.dumps(
            chart_generator.prepare_bar_chart_data(
                by_area, 
                'service_area__name', 
                ['total', 'completed']
            )
        )
        
        # Rendimiento de técnicos
        context['technician_performance'] = generator.get_technician_performance()
        
        # Satisfacción ciudadana
        context['satisfaction_stats'] = generator.get_satisfaction_statistics()
        
        # Tendencia mensual
        monthly_trend = generator.get_monthly_trend()
        context['monthly_trend_data'] = json.dumps(
            chart_generator.prepare_line_chart_data(monthly_trend, 'month', 'total')
        )
        
        context['date_from'] = date_from
        context['date_to'] = date_to
        context['form'] = ReportFilterForm()
        
        return context

@login_required
@role_required(['ADMIN', 'AUTHORITY', 'MANAGER'])
def generate_custom_report(request):
    """Genera reportes personalizados"""
    if request.method == 'POST':
        form = ReportFilterForm(request.POST)
        if form.is_valid():
            report_type = form.cleaned_data['report_type']
            date_from = form.cleaned_data['date_from']
            date_to = form.cleaned_data['date_to']
            
            generator = ReportGenerator(date_from, date_to)
            chart_generator = ChartDataGenerator()
            
            context = {
                'report_type': report_type,
                'date_from': date_from,
                'date_to': date_to,
            }
            
            if report_type == 'GENERAL':
                context['stats'] = generator.get_general_statistics()
                context['response_times'] = generator.get_response_times()
                template = 'reports/general_report.html'
                
            elif report_type == 'SERVICE_TYPE':
                by_service = generator.get_requests_by_service_type()
                context['service_data'] = by_service
                context['chart_data'] = json.dumps(
                    chart_generator.prepare_pie_chart_data(by_service, 'service_type__name')
                )
                template = 'reports/service_type_report.html'
                
            elif report_type == 'AREA':
                by_area = generator.get_requests_by_area()
                context['area_data'] = by_area
                context['chart_data'] = json.dumps(
                    chart_generator.prepare_bar_chart_data(
                        by_area, 'service_area__name', ['total', 'completed']
                    )
                )
                template = 'reports/area_report.html'
                
            elif report_type == 'TECHNICIAN':
                context['technician_data'] = generator.get_technician_performance()
                template = 'reports/technician_report.html'
                
            elif report_type == 'SATISFACTION':
                context['satisfaction_stats'] = generator.get_satisfaction_statistics()
                template = 'reports/satisfaction_report.html'
            
            else:
                messages.error(request, 'Tipo de reporte no válido.')
                return redirect('reports:dashboard')
            
            return render(request, template, context)
    
    return redirect('reports:dashboard')

@login_required
def submit_satisfaction_survey(request, ticket_number):
    """Vista para que ciudadanos evalúen el servicio"""
    service_request = get_object_or_404(ServiceRequest, ticket_number=ticket_number)
    
    # Verificar que sea el ciudadano propietario
    if service_request.citizen != request.user:
        messages.error(request, 'No tiene permisos para evaluar esta solicitud.')
        return redirect('requests:detail', ticket_number=ticket_number)
    
    # Verificar que la solicitud esté completada
    if service_request.status != 'COMPLETED':
        messages.error(request, 'Solo puede evaluar solicitudes completadas.')
        return redirect('requests:detail', ticket_number=ticket_number)
    
    # Verificar que no haya sido evaluada ya
    if hasattr(service_request, 'satisfaction'):
        messages.info(request, 'Esta solicitud ya ha sido evaluada.')
        return redirect('requests:detail', ticket_number=ticket_number)
    
    if request.method == 'POST':
        form = SatisfactionSurveyForm(request.POST)
        if form.is_valid():
            satisfaction = form.save(commit=False)
            satisfaction.request = service_request
            satisfaction.save()
            
            messages.success(request, '¡Gracias por su evaluación! Su opinión es muy importante.')
            return redirect('requests:detail', ticket_number=ticket_number)
    else:
        form = SatisfactionSurveyForm()
    
    return render(request, 'reports/satisfaction_survey.html', {
        'form': form,
        'service_request': service_request
    })

@login_required
@role_required(['ADMIN', 'AUTHORITY', 'MANAGER'])
def export_report_data(request):
    """API para exportar datos de reportes en formato JSON"""
    report_type = request.GET.get('type', 'general')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if not date_from or not date_to:
        return JsonResponse({'error': 'Fechas requeridas'}, status=400)
    
    from datetime import datetime
    date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
    date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
    
    generator = ReportGenerator(date_from, date_to)
    
    if report_type == 'general':
        data = generator.get_general_statistics()
    elif report_type == 'service_type':
        data = list(generator.get_requests_by_service_type())
    elif report_type == 'area':
        data = list(generator.get_requests_by_area())
    elif report_type == 'technician':
        data = list(generator.get_technician_performance())
    elif report_type == 'satisfaction':
        data = generator.get_satisfaction_statistics()
    else:
        return JsonResponse({'error': 'Tipo de reporte inválido'}, status=400)
    
    return JsonResponse(data, safe=False)


@login_required
@role_required(['ADMIN', 'AUTHORITY', 'MANAGER'])
def satisfaction_list(request):
    """Vista para listar todas las evaluaciones de satisfacción"""
    evaluations = CitizenSatisfaction.objects.select_related(
        'request__citizen', 'request__service_type'
    ).order_by('-created_at')

    # Filtros
    rating_filter = request.GET.get('rating')
    if rating_filter:
        evaluations = evaluations.filter(rating=rating_filter)

    # Estadísticas generales
    total_evaluations = evaluations.count()
    if total_evaluations > 0:
        avg_rating = evaluations.aggregate(Avg('rating'))['rating__avg']
        avg_response_time = evaluations.aggregate(Avg('response_time_rating'))['response_time_rating__avg']
        avg_quality = evaluations.aggregate(Avg('quality_rating'))['quality_rating__avg']
        recommend_count = evaluations.filter(would_recommend=True).count()
        recommend_percentage = (recommend_count / total_evaluations) * 100
    else:
        avg_rating = 0
        avg_response_time = 0
        avg_quality = 0
        recommend_percentage = 0

    context = {
        'evaluations': evaluations[:50],  # Últimas 50 evaluaciones
        'total_evaluations': total_evaluations,
        'avg_rating': avg_rating,
        'avg_response_time': avg_response_time,
        'avg_quality': avg_quality,
        'recommend_percentage': recommend_percentage,
    }

    return render(request, 'reports/satisfaction_list.html', context)

class ReportHistoryView(LoginRequiredMixin, ListView):
    """Historial de reportes generados"""
    model = Report
    template_name = 'reports/report_history.html'
    context_object_name = 'reports'
    paginate_by = 20
    
    def get_queryset(self):
        if self.request.user.role in ['ADMIN', 'AUTHORITY', 'MANAGER']:
            return Report.objects.all().order_by('-created_at')
        return Report.objects.none()