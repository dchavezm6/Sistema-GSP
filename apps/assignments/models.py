from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from apps.requests.models import ServiceRequest

User = get_user_model()

class TaskAssignment(models.Model):
    """Asignación de tareas a técnicos"""
    
    PRIORITY_CHOICES = [
        ('LOW', 'Baja'),
        ('MEDIUM', 'Media'),
        ('HIGH', 'Alta'),
        ('URGENT', 'Urgente'),
    ]
    
    STATUS_CHOICES = [
        ('ASSIGNED', 'Asignada'),
        ('ACCEPTED', 'Aceptada'),
        ('IN_PROGRESS', 'En Progreso'),
        ('ON_HOLD', 'En Espera'),
        ('COMPLETED', 'Completada'),
        ('CANCELLED', 'Cancelada'),
    ]
    
    request = models.OneToOneField(
        ServiceRequest,
        on_delete=models.CASCADE,
        related_name='assignment',
        verbose_name='Solicitud'
    )
    
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assignments_made',
        verbose_name='Asignado por'
    )
    
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assignments_received',
        verbose_name='Asignado a'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ASSIGNED',
        verbose_name='Estado de la Tarea'
    )
    
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='MEDIUM',
        verbose_name='Prioridad'
    )
    
    assigned_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Asignación'
    )
    
    accepted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de Aceptación'
    )
    
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de Inicio'
    )
    
    estimated_completion = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha Estimada de Finalización'
    )
    
    actual_completion = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha Real de Finalización'
    )
    
    instructions = models.TextField(
        blank=True,
        verbose_name='Instrucciones Especiales'
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name='Notas del Técnico'
    )
    
    estimated_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Horas Estimadas'
    )
    
    actual_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Horas Reales'
    )
    
    materials_needed = models.TextField(
        blank=True,
        verbose_name='Materiales Necesarios'
    )
    
    materials_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Costo de Materiales'
    )
    
    class Meta:
        verbose_name = 'Asignación de Tarea'
        verbose_name_plural = 'Asignaciones de Tareas'
        ordering = ['-assigned_at']
    
    def __str__(self):
        return f"Tarea: {self.request.ticket_number} - {self.assigned_to.get_full_name()}"
    
    def get_absolute_url(self):
        return reverse('assignments:detail', kwargs={'pk': self.pk})
    
    def is_overdue(self):
        if self.estimated_completion and self.status not in ['COMPLETED', 'CANCELLED']:
            return timezone.now() > self.estimated_completion
        return False

class TaskUpdate(models.Model):
    """Actualizaciones de progreso"""
    
    assignment = models.ForeignKey(
        TaskAssignment,
        on_delete=models.CASCADE,
        related_name='updates',
        verbose_name='Asignación'
    )
    
    updated_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Actualizado por'
    )
    
    status = models.CharField(
        max_length=20,
        choices=TaskAssignment.STATUS_CHOICES,
        verbose_name='Estado'
    )
    
    progress_percentage = models.IntegerField(
        default=0,
        verbose_name='Porcentaje de Progreso'
    )
    
    description = models.TextField(
        verbose_name='Descripción del Progreso'
    )
    
    hours_worked = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Horas Trabajadas'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha'
    )
    
    class Meta:
        verbose_name = 'Actualización de Tarea'
        verbose_name_plural = 'Actualizaciones de Tareas'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Actualización: {self.assignment.request.ticket_number} - {self.progress_percentage}%"

class Notification(models.Model):
    """Sistema de notificaciones"""
    
    TYPE_CHOICES = [
        ('TASK_ASSIGNED', 'Tarea Asignada'),
        ('TASK_UPDATED', 'Tarea Actualizada'),
        ('TASK_COMPLETED', 'Tarea Completada'),
        ('REQUEST_UPDATED', 'Solicitud Actualizada'),
        ('GENERAL', 'General'),
    ]
    
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Destinatario'
    )
    
    notification_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        verbose_name='Tipo'
    )
    
    title = models.CharField(
        max_length=200,
        verbose_name='Título'
    )
    
    message = models.TextField(
        verbose_name='Mensaje'
    )
    
    related_request = models.ForeignKey(
        ServiceRequest,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Solicitud Relacionada'
    )
    
    is_read = models.BooleanField(
        default=False,
        verbose_name='Leída'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha'
    )
    
    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.recipient.username}"