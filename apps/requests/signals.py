from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from .models import ServiceRequest, RequestStatusHistory


@receiver(pre_save, sender=ServiceRequest)
def track_status_changes(sender, instance, **kwargs):
    """Registra cambios de estado en el historial"""
    if instance.pk:  # Solo para instancias existentes
        try:
            original = ServiceRequest.objects.get(pk=instance.pk)
            if original.status != instance.status:
                # El estado cambió, se creará el historial en post_save
                instance._status_changed = True
                instance._original_status = original.status
        except ServiceRequest.DoesNotExist:
            pass


@receiver(post_save, sender=ServiceRequest)
def create_status_history(sender, instance, created, **kwargs):
    """Crea registro en el historial cuando cambia el estado"""
    if created:
        # Nueva solicitud creada
        RequestStatusHistory.objects.create(
            request=instance,
            from_status=None,
            to_status=instance.status,
            changed_by=instance.citizen,
            reason="Solicitud creada"
        )
    elif hasattr(instance, '_status_changed') and instance._status_changed:
        # Estado cambió
        RequestStatusHistory.objects.create(
            request=instance,
            from_status=instance._original_status,
            to_status=instance.status,
            changed_by=instance.citizen,  # Esto se debe cambiar según quién hizo el cambio
            reason="Estado actualizado"
        )


@receiver(post_save, sender=ServiceRequest)
def send_status_notification(sender, instance, created, **kwargs):
    """Envía notificaciones por email cuando cambia el estado"""
    if created:
        # Notificación de nueva solicitud
        subject = f"Nueva Solicitud Creada: {instance.ticket_number}"
        message = f"""
        Se ha creado una nueva solicitud:

        Ticket: {instance.ticket_number}
        Tipo: {instance.get_request_type_display()}
        Servicio: {instance.service_type.name}
        Ciudadano: {instance.citizen.get_full_name()}

        Descripción: {instance.description[:200]}...
        """

        # Enviar a personal municipal (esto se puede mejorar)
        # send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, ['admin@municipalidad.gt'])

    elif hasattr(instance, '_status_changed') and instance._status_changed:
        # Notificación de cambio de estado
        subject = f"Actualización de Solicitud: {instance.ticket_number}"
        message = f"""
        Su solicitud ha sido actualizada:

        Ticket: {instance.ticket_number}
        Estado: {instance.get_status_display()}

        Puede ver más detalles en el sistema.
        """

        # Enviar al ciudadano
        if instance.citizen.email:
            # send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [instance.citizen.email])
            pass