from django.urls import path
from .views import (
    TaskAssignmentListView,
    TaskAssignmentDetailView,
    create_assignment,
    accept_assignment,
    start_assignment,
    add_task_update,
    complete_assignment,
    notification_list,
    technician_management,
)

app_name = 'assignments'

urlpatterns = [
    path('', TaskAssignmentListView.as_view(), name='list'),
    path('<int:pk>/', TaskAssignmentDetailView.as_view(), name='detail'),
    path('crear/<str:ticket_number>/', create_assignment, name='create'),
    path('<int:pk>/aceptar/', accept_assignment, name='accept'),
    path('<int:pk>/iniciar/', start_assignment, name='start'),
    path('<int:pk>/actualizar/', add_task_update, name='add_update'),
    path('<int:pk>/completar/', complete_assignment, name='complete'),
    path('notificaciones/', notification_list, name='notifications'),
    path('personal/', technician_management, name='technician_management'),
]