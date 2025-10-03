from django.urls import path
from .views import (
    DashboardReportsView,
    generate_custom_report,
    submit_satisfaction_survey,
    export_report_data,
    ReportHistoryView, satisfaction_list,
)

app_name = 'reports'

urlpatterns = [
    path('', DashboardReportsView.as_view(), name='dashboard'),
    path('generar/', generate_custom_report, name='generate'),
    path('evaluar/<str:ticket_number>/', submit_satisfaction_survey, name='satisfaction_survey'),
    path('exportar/', export_report_data, name='export'),
    path('historial/', ReportHistoryView.as_view(), name='history'),
    path('satisfaccion/', satisfaction_list, name='satisfaction_list'),
]