from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Report(models.Model):
    """Modelo para almacenar reportes generados"""
    
    REPORT_TYPE_CHOICES = [
        ('GENERAL', 'Reporte General'),
        ('SERVICE_TYPE', 'Por Tipo de Servicio'),
        ('AREA', 'Por Área'),
        ('TECHNICIAN', 'Rendimiento de Técnicos'),
        ('SATISFACTION', 'Satisfacción Ciudadana'),
        ('MONTHLY', 'Reporte Mensual'),
        ('ANNUAL', 'Reporte Anual'),
    ]
    
    title = models.CharField(
        max_length=200,
        verbose_name='Título'
    )
    
    report_type = models.CharField(
        max_length=20,
        choices=REPORT_TYPE_CHOICES,
        verbose_name='Tipo de Reporte'
    )
    
    generated_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Generado por'
    )
    
    date_from = models.DateField(
        verbose_name='Fecha Desde'
    )
    
    date_to = models.DateField(
        verbose_name='Fecha Hasta'
    )
    
    file = models.FileField(
        upload_to='reports/',
        null=True,
        blank=True,
        verbose_name='Archivo'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    
    class Meta:
        verbose_name = 'Reporte'
        verbose_name_plural = 'Reportes'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.created_at.strftime('%d/%m/%Y')}"

class CitizenSatisfaction(models.Model):
    """Encuestas de satisfacción ciudadana"""
    
    RATING_CHOICES = [
        (1, 'Muy Insatisfecho'),
        (2, 'Insatisfecho'),
        (3, 'Neutral'),
        (4, 'Satisfecho'),
        (5, 'Muy Satisfecho'),
    ]
    
    request = models.OneToOneField(
        'requests.ServiceRequest',
        on_delete=models.CASCADE,
        related_name='satisfaction',
        verbose_name='Solicitud'
    )
    
    rating = models.IntegerField(
        choices=RATING_CHOICES,
        verbose_name='Calificación'
    )
    
    response_time_rating = models.IntegerField(
        choices=RATING_CHOICES,
        verbose_name='Calificación del Tiempo de Respuesta'
    )
    
    quality_rating = models.IntegerField(
        choices=RATING_CHOICES,
        verbose_name='Calificación de la Calidad'
    )
    
    technician_rating = models.IntegerField(
        choices=RATING_CHOICES,
        null=True,
        blank=True,
        verbose_name='Calificación del Técnico'
    )
    
    comments = models.TextField(
        blank=True,
        verbose_name='Comentarios'
    )
    
    would_recommend = models.BooleanField(
        default=True,
        verbose_name='¿Recomendaría el servicio?'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha'
    )
    
    class Meta:
        verbose_name = 'Evaluación de Satisfacción'
        verbose_name_plural = 'Evaluaciones de Satisfacción'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Evaluación: {self.request.ticket_number} - {self.rating}/5"
    
    def get_average_rating(self):
        """Calcula el promedio de todas las calificaciones"""
        ratings = [self.rating, self.response_time_rating, self.quality_rating]
        if self.technician_rating:
            ratings.append(self.technician_rating)
        return sum(ratings) / len(ratings)