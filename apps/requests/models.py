from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
import uuid
import os

User = get_user_model()


class ServiceType(models.Model):
    """Tipos de servicios públicos disponibles"""
    name = models.CharField(
        max_length=100,
        verbose_name='Nombre del Servicio'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Descripción'
    )
    icon_class = models.CharField(
        max_length=50,
        default='bi-wrench',
        help_text='Clase CSS del icono Bootstrap',
        verbose_name='Icono'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )

    class Meta:
        verbose_name = 'Tipo de Servicio'
        verbose_name_plural = 'Tipos de Servicios'
        ordering = ['name']

    def __str__(self):
        return self.name


class ServiceArea(models.Model):
    """Áreas o zonas del municipio"""
    name = models.CharField(
        max_length=100,
        verbose_name='Nombre del Área'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Descripción'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activa'
    )

    class Meta:
        verbose_name = 'Área de Servicio'
        verbose_name_plural = 'Áreas de Servicio'
        ordering = ['name']

    def __str__(self):
        return self.name


def generate_ticket_number():
    """Genera un número de ticket único"""
    timestamp = timezone.now().strftime('%Y%m%d')
    unique_id = str(uuid.uuid4())[:8].upper()
    return f"REQ-{timestamp}-{unique_id}"


def request_image_path(instance, filename):
    """Función para generar la ruta de las imágenes"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('requests', str(instance.request.id), filename)


class ServiceRequest(models.Model):
    """Solicitudes de servicios y reportes de averías"""

    STATUS_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('IN_REVIEW', 'En Revisión'),
        ('APPROVED', 'Aprobada'),
        ('IN_PROGRESS', 'En Proceso'),
        ('COMPLETED', 'Completada'),
        ('REJECTED', 'Rechazada'),
        ('CANCELLED', 'Cancelada'),
    ]

    REQUEST_TYPE_CHOICES = [
        ('REPAIR', 'Reparación/Avería'),
        ('NEW_SERVICE', 'Nuevo Servicio'),
        ('MAINTENANCE', 'Mantenimiento'),
        ('COMPLAINT', 'Queja/Reclamo'),
        ('INFORMATION', 'Solicitud de Información'),
    ]

    PRIORITY_CHOICES = [
        ('LOW', 'Baja'),
        ('MEDIUM', 'Media'),
        ('HIGH', 'Alta'),
        ('URGENT', 'Urgente'),
    ]

    # Información básica
    ticket_number = models.CharField(
        max_length=50,
        unique=True,
        default=generate_ticket_number,
        verbose_name='Número de Ticket'
    )

    citizen = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='service_requests',
        verbose_name='Ciudadano'
    )

    service_type = models.ForeignKey(
        ServiceType,
        on_delete=models.CASCADE,
        verbose_name='Tipo de Servicio'
    )

    service_area = models.ForeignKey(
        ServiceArea,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Área de Servicio'
    )

    request_type = models.CharField(
        max_length=50,
        choices=REQUEST_TYPE_CHOICES,
        verbose_name='Tipo de Solicitud'
    )

    # Detalles de la solicitud
    title = models.CharField(
        max_length=200,
        verbose_name='Título'
    )

    description = models.TextField(
        verbose_name='Descripción Detallada'
    )

    # Ubicación
    address = models.TextField(
        verbose_name='Dirección'
    )

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name='Latitud'
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name='Longitud'
    )

    # Estado y prioridad
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='PENDING',
        verbose_name='Estado'
    )

    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='MEDIUM',
        verbose_name='Prioridad'
    )

    # Fechas
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Actualización'
    )

    expected_completion = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha Estimada de Finalización'
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de Finalización'
    )

    # Información adicional
    citizen_phone = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Teléfono de Contacto'
    )

    citizen_email = models.EmailField(
        blank=True,
        verbose_name='Email de Contacto'
    )

    notes = models.TextField(
        blank=True,
        verbose_name='Notas Adicionales'
    )

    # Campos de gestión interna
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_requests',
        limit_choices_to={'role__in': ['TECHNICIAN', 'MANAGER']},
        verbose_name='Asignado a'
    )

    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_requests',
        limit_choices_to={'role__in': ['MANAGER', 'AUTHORITY']},
        verbose_name='Revisado por'
    )

    estimated_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Costo Estimado'
    )

    actual_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Costo Real'
    )

    class Meta:
        verbose_name = 'Solicitud de Servicio'
        verbose_name_plural = 'Solicitudes de Servicio'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['citizen', 'status']),
            models.Index(fields=['ticket_number']),
        ]

    def __str__(self):
        return f"{self.ticket_number} - {self.title}"

    def get_absolute_url(self):
        return reverse('requests:detail', kwargs={'ticket_number': self.ticket_number})

    def get_status_display_class(self):
        """Retorna la clase CSS para el estado"""
        status_classes = {
            'PENDING': 'warning',
            'IN_REVIEW': 'info',
            'APPROVED': 'success',
            'IN_PROGRESS': 'primary',
            'COMPLETED': 'success',
            'REJECTED': 'danger',
            'CANCELLED': 'secondary',
        }
        return status_classes.get(self.status, 'secondary')

    def get_priority_display_class(self):
        """Retorna la clase CSS para la prioridad"""
        priority_classes = {
            'LOW': 'success',
            'MEDIUM': 'warning',
            'HIGH': 'danger',
            'URGENT': 'danger',
        }
        return priority_classes.get(self.priority, 'secondary')

    def is_overdue(self):
        """Verifica si la solicitud está vencida"""
        if self.expected_completion and self.status not in ['COMPLETED', 'REJECTED', 'CANCELLED']:
            return timezone.now().date() > self.expected_completion
        return False

    def days_since_created(self):
        """Días transcurridos desde la creación"""
        return (timezone.now().date() - self.created_at.date()).days

    def can_be_edited_by_citizen(self):
        """Verifica si el ciudadano puede editar la solicitud"""
        return self.status in ['PENDING', 'IN_REVIEW']

    def can_be_cancelled_by_citizen(self):
        """Verifica si el ciudadano puede cancelar la solicitud"""
        return self.status in ['PENDING', 'IN_REVIEW', 'APPROVED']


class RequestImage(models.Model):
    """Imágenes adjuntas a las solicitudes"""
    request = models.ForeignKey(
        ServiceRequest,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='Solicitud'
    )

    image = models.ImageField(
        upload_to=request_image_path,
        verbose_name='Imagen'
    )

    description = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Descripción'
    )

    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Subido por'
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Subida'
    )

    is_before = models.BooleanField(
        default=True,
        verbose_name='Imagen Antes del Trabajo',
        help_text='Marcar si es imagen antes del trabajo, desmarcar si es después'
    )

    class Meta:
        verbose_name = 'Imagen de Solicitud'
        verbose_name_plural = 'Imágenes de Solicitudes'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"Imagen de {self.request.ticket_number}"

    def get_image_type_display(self):
        return "Antes" if self.is_before else "Después"


class RequestStatusHistory(models.Model):
    """Historial de cambios de estado de las solicitudes"""
    request = models.ForeignKey(
        ServiceRequest,
        on_delete=models.CASCADE,
        related_name='status_history',
        verbose_name='Solicitud'
    )

    from_status = models.CharField(
        max_length=50,
        choices=ServiceRequest.STATUS_CHOICES,
        null=True,
        blank=True,
        verbose_name='Estado Anterior'
    )

    to_status = models.CharField(
        max_length=50,
        choices=ServiceRequest.STATUS_CHOICES,
        verbose_name='Nuevo Estado'
    )

    changed_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Cambiado por'
    )

    reason = models.TextField(
        blank=True,
        verbose_name='Motivo del Cambio'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha del Cambio'
    )

    class Meta:
        verbose_name = 'Historial de Estado'
        verbose_name_plural = 'Historial de Estados'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.request.ticket_number}: {self.from_status} → {self.to_status}"


class RequestComment(models.Model):
    """Comentarios en las solicitudes"""
    request = models.ForeignKey(
        ServiceRequest,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Solicitud'
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Usuario'
    )

    comment = models.TextField(
        verbose_name='Comentario'
    )

    is_internal = models.BooleanField(
        default=False,
        verbose_name='Comentario Interno',
        help_text='Los comentarios internos solo son visibles para el personal municipal'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha del Comentario'
    )

    class Meta:
        verbose_name = 'Comentario'
        verbose_name_plural = 'Comentarios'
        ordering = ['created_at']

    def __str__(self):
        return f"Comentario de {self.user.username} en {self.request.ticket_number}"