from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import TaskAssignment, Notification

@receiver(post_save, sender=TaskAssignment)
def create_assignment_notification(sender, instance, created, **kwargs):
    """Crea notificación cuando se asigna una tarea"""
    if created:
        # Notificar al técnico asignado
        Notification.objects.create(
            recipient=instance.assigned_to,
            notification_type='TASK_ASSIGNED',
            title=f'Nueva tarea asignada: {instance.request.ticket_number}',
            message=f'Se le ha asignado la tarea: {instance.request.title}. Prioridad: {instance.get_priority_display()}.',
            related_request=instance.request
        )
        
        # Notificar al ciudadano
        Notification.objects.create(
            recipient=instance.request.citizen,
            notification_type='TASK_ASSIGNED',
            title=f'Su solicitud ha sido asignada: {instance.request.ticket_number}',
            message=f'Su solicitud ha sido asignada a {instance.assigned_to.get_full_name()}.',
            related_request=instance.request
        )