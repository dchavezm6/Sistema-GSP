from django.urls import path
from .views import (
    ServiceRequestListView,
    ServiceRequestDetailView,
    ServiceRequestCreateView,
    add_request_image,
    add_request_comment,
    update_request_status,
    cancel_request,
    dashboard_stats_api,
)

app_name = 'requests'

urlpatterns = [
    # Lista y detalle de solicitudes
    path('', ServiceRequestListView.as_view(), name='list'),
    path('crear/', ServiceRequestCreateView.as_view(), name='create'),
    path('<str:ticket_number>/', ServiceRequestDetailView.as_view(), name='detail'),
    
    # Acciones en solicitudes
    path('<str:ticket_number>/imagen/', add_request_image, name='add_image'),
    path('<str:ticket_number>/comentario/', add_request_comment, name='add_comment'),
    path('<str:ticket_number>/estado/', update_request_status, name='update_status'),
    path('<str:ticket_number>/cancelar/', cancel_request, name='cancel'),
    
    # API
    path('api/stats/', dashboard_stats_api, name='stats_api'),
]