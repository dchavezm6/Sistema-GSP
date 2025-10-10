from django.db.models import Count, Avg, Q, Sum, F
from django.utils import timezone
from datetime import timedelta
from apps.requests.models import ServiceRequest, ServiceType, ServiceArea
from apps.assignments.models import TaskAssignment
from apps.reports.models import CitizenSatisfaction


class ReportGenerator:
    """Clase para generar estadísticas y reportes"""

    def __init__(self, date_from=None, date_to=None):
        self.date_from = date_from or (timezone.now() - timedelta(days=30)).date()
        self.date_to = date_to or timezone.now().date()

    def get_general_statistics(self):
        """Estadísticas generales del sistema"""
        requests = ServiceRequest.objects.filter(
            created_at__date__gte=self.date_from,
            created_at__date__lte=self.date_to
        )

        return {
            'total_requests': requests.count(),
            'pending': requests.filter(status='PENDING').count(),
            'in_progress': requests.filter(status='IN_PROGRESS').count(),
            'completed': requests.filter(status='COMPLETED').count(),
            'rejected': requests.filter(status='REJECTED').count(),
            'cancelled': requests.filter(status='CANCELLED').count(),
            'average_completion_days': self._calculate_avg_completion_time(requests),
            'completion_rate': self._calculate_completion_rate(requests),
        }

    def get_requests_by_service_type(self):
        """Solicitudes agrupadas por tipo de servicio"""
        return ServiceRequest.objects.filter(
            created_at__date__gte=self.date_from,
            created_at__date__lte=self.date_to
        ).values(
            'service_type__name'
        ).annotate(
            total=Count('id'),
            completed=Count('id', filter=Q(status='COMPLETED')),
            pending=Count('id', filter=Q(status='PENDING')),
            in_progress=Count('id', filter=Q(status='IN_PROGRESS'))
        ).order_by('-total')

    def get_requests_by_area(self):
        """Solicitudes agrupadas por área"""
        return ServiceRequest.objects.filter(
            created_at__date__gte=self.date_from,
            created_at__date__lte=self.date_to,
            service_area__isnull=False
        ).values(
            'service_area__name'
        ).annotate(
            total=Count('id'),
            completed=Count('id', filter=Q(status='COMPLETED'))
        ).order_by('-total')

    def get_requests_by_priority(self):
        """Solicitudes agrupadas por prioridad"""
        return ServiceRequest.objects.filter(
            created_at__date__gte=self.date_from,
            created_at__date__lte=self.date_to
        ).values('priority').annotate(
            total=Count('id')
        ).order_by('priority')

    def get_technician_performance(self):
        """Rendimiento de técnicos"""
        assignments = TaskAssignment.objects.filter(
            assigned_at__date__gte=self.date_from,
            assigned_at__date__lte=self.date_to
        )

        return assignments.values(
            'assigned_to__first_name',
            'assigned_to__last_name'
        ).annotate(
            total_tasks=Count('id'),
            completed_tasks=Count('id', filter=Q(status='COMPLETED')),
            in_progress_tasks=Count('id', filter=Q(status='IN_PROGRESS')),
            avg_hours=Avg('actual_hours', filter=Q(status='COMPLETED')),
            total_cost=Sum('materials_cost', filter=Q(status='COMPLETED'))
        ).order_by('-completed_tasks')

    def get_satisfaction_statistics(self):
        """Estadísticas de satisfacción ciudadana"""
        satisfactions = CitizenSatisfaction.objects.filter(
            created_at__date__gte=self.date_from,
            created_at__date__lte=self.date_to
        )

        if not satisfactions.exists():
            return None

        return {
            'total_evaluations': satisfactions.count(),
            'average_rating': satisfactions.aggregate(Avg('rating'))['rating__avg'],
            'average_response_time': satisfactions.aggregate(Avg('response_time_rating'))['response_time_rating__avg'],
            'average_quality': satisfactions.aggregate(Avg('quality_rating'))['quality_rating__avg'],
            'would_recommend_percentage': (satisfactions.filter(
                would_recommend=True).count() / satisfactions.count()) * 100,
            'rating_distribution': satisfactions.values('rating').annotate(count=Count('id')).order_by('rating'),
        }

    def get_monthly_trend(self):
        """Tendencia mensual de solicitudes"""
        from django.db.models.functions import ExtractMonth, ExtractYear

        requests = ServiceRequest.objects.filter(
            created_at__date__gte=self.date_from,
            created_at__date__lte=self.date_to
        ).annotate(
            month=ExtractMonth('created_at'),
            year=ExtractYear('created_at')
        ).values('month', 'year').annotate(
            total=Count('id'),
            completed=Count('id', filter=Q(status='COMPLETED'))
        ).order_by('year', 'month')

        return list(requests)

    def get_response_times(self):
        """Tiempos de respuesta promedio"""
        completed_requests = ServiceRequest.objects.filter(
            created_at__date__gte=self.date_from,
            created_at__date__lte=self.date_to,
            status='COMPLETED',
            completed_at__isnull=False
        )

        times = []
        for req in completed_requests:
            delta = req.completed_at - req.created_at
            times.append(delta.days)

        if times:
            return {
                'average_days': sum(times) / len(times),
                'min_days': min(times),
                'max_days': max(times),
                'total_analyzed': len(times)
            }
        return None

    def _calculate_avg_completion_time(self, requests):
        """Calcula el tiempo promedio de finalización"""
        completed = requests.filter(status='COMPLETED', completed_at__isnull=False)
        if not completed.exists():
            return 0

        total_days = 0
        for req in completed:
            delta = req.completed_at - req.created_at
            total_days += delta.days

        return total_days / completed.count()

    def _calculate_completion_rate(self, requests):
        """Calcula la tasa de finalización"""
        total = requests.count()
        if total == 0:
            return 0
        completed = requests.filter(status='COMPLETED').count()
        return (completed / total) * 100


class ChartDataGenerator:
    """Generador de datos para gráficos"""

    @staticmethod
    def prepare_pie_chart_data(queryset, label_field, value_field='total'):
        """Prepara datos para gráficos de pastel"""
        labels = []
        data = []

        for item in queryset:
            labels.append(item.get(label_field, 'Sin especificar'))
            data.append(item.get(value_field, 0))

        return {
            'labels': labels,
            'data': data
        }

    @staticmethod
    def prepare_bar_chart_data(queryset, label_field, value_fields):
        """Prepara datos para gráficos de barras"""
        labels = []
        datasets = {field: [] for field in value_fields}

        for item in queryset:
            labels.append(item.get(label_field, 'Sin especificar'))
            for field in value_fields:
                datasets[field].append(item.get(field, 0))

        return {
            'labels': labels,
            'datasets': datasets
        }

    @staticmethod
    def prepare_line_chart_data(queryset, label_field, value_field):
        """Prepara datos para gráficos de línea"""
        labels = []
        data = []

        # Nombre de meses en español
        month_names = {
            1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
            5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
            9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
        }

        for item in queryset:
            # Si el label_field es 'month', convertir a nombre del mes
            if label_field == 'month' and 'month' in item:
                month_num = item.get('month')
                month_label = month_names.get(month_num, f'Mes {month_num}')
                # Si también hay año, agregarlo
                if 'year' in item:
                    labels.append(f"{month_label} {item['year']}")
                else:
                    labels.append(month_label)
            else:
                labels.append(str(item.get(label_field, '')))

            data.append(item.get(value_field, 0))

        return {
            'labels': labels,
            'data': data
        }