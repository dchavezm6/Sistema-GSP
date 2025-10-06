from django.core.management.base import BaseCommand
from apps.requests.models import ServiceType

class Command(BaseCommand):
    help = 'Crea tipos de servicio iniciales'

    def handle(self, *args, **options):
        services = [
            {'name': 'Suministro de Agua', 'description': 'Solicitudes relacionadas con agua potable', 'icon_class': 'fas fa-tint'},
            {'name': 'Alumbrado Público', 'description': 'Reportes de alumbrado público', 'icon_class': 'fas fa-lightbulb'},
            {'name': 'Recolección de Basura', 'description': 'Servicios de recolección de desechos', 'icon_class': 'fas fa-trash'},
            {'name': 'Mantenimiento de Calles', 'description': 'Baches, pavimento, señalización', 'icon_class': 'fas fa-road'},
            {'name': 'Parques y Jardines', 'description': 'Mantenimiento de áreas verdes', 'icon_class': 'fas fa-tree'},
            {'name': 'Drenajes', 'description': 'Sistema de drenaje y alcantarillado', 'icon_class': 'fas fa-water'},
            {'name': 'Limpieza Pública', 'description': 'Limpieza de áreas públicas', 'icon_class': 'fas fa-broom'},
            {'name': 'Mercado Municipal', 'description': 'Servicios del mercado municipal', 'icon_class': 'fas fa-store'},
        ]
        
        created = 0
        for service_data in services:
            service, created_now = ServiceType.objects.get_or_create(
                name=service_data['name'],
                defaults={
                    'description': service_data['description'],
                    'icon_class': service_data['icon_class'],
                    'is_active': True
                }
            )
            if created_now:
                created += 1
                self.stdout.write(f"✓ Creado: {service.name}")
            else:
                self.stdout.write(f"- Ya existe: {service.name}")
        
        self.stdout.write(
            self.style.SUCCESS(f'\nTotal: {created} tipos de servicio creados')
        )