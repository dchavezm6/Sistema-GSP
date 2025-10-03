from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


class User(AbstractUser):
    ROLE_CHOICES = [
        ('ADMIN', 'Administrador'),
        ('AUTHORITY', 'Autoridad'),
        ('MANAGER', 'Encargado'),
        ('TECHNICIAN', 'Técnico'),
        ('CITIZEN', 'Ciudadano'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='CITIZEN',
        verbose_name='Rol'
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Teléfono'
    )
    address = models.TextField(
        blank=True,
        verbose_name='Dirección'
    )
    is_active_citizen = models.BooleanField(
        default=True,
        verbose_name='Ciudadano Activo'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de Actualización'
    )

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"

    def get_absolute_url(self):
        return reverse('authentication:profile')

    def is_admin(self):
        return self.role == 'ADMIN'

    def is_authority(self):
        return self.role == 'AUTHORITY'

    def is_manager(self):
        return self.role == 'MANAGER'

    def is_technician(self):
        return self.role == 'TECHNICIAN'

    def is_citizen(self):
        return self.role == 'CITIZEN'

    def can_assign_tasks(self):
        return self.role in ['ADMIN', 'MANAGER']

    def can_view_reports(self):
        return self.role in ['ADMIN', 'AUTHORITY', 'MANAGER']