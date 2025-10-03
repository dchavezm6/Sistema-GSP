from django.core.management.base import BaseCommand
from apps.requests.models import ServiceType, ServiceArea


class Command(BaseCommand):
    help = 'Crear tipos de servicios y áreas iniciales'

    def handle(self, *args, **options):
        # Tipos de servicios
        service_types = [
            {
                'name': 'Suministro de agua',
                'description': 'Problemas relacionados con el suministro de agua',
                'icon_class': 'bi-droplet'
            },
            {
                'name': 'Alumbrado Público',
                'description': 'Problemas con el alumbrado público y electricidad',
                'icon_class': 'bi-lightbulb'
            },
            {
                'name': 'Drenajes',
                'description': 'Problemas con drenajes, alcantarillas y aguas residuales',
                'icon_class': 'bi-water'
            },
            {
                'name': 'Recolección de Basura',
                'description': 'Servicios de recolección y manejo de desechos',
                'icon_class': 'bi-trash'
            },
            {
                'name': 'Vías y Calles',
                'description': 'Mantenimiento de calles, banquetas y señalización',
                'icon_class': 'bi-road'
            },
            {
                'name': 'Parques y Jardines',
                'description': 'Mantenimiento de áreas verdes y espacios públicos',
                'icon_class': 'bi-tree'
            },
            {
                'name': 'Seguridad Ciudadana',
                'description': 'Temas relacionados con seguridad y orden público',
                'icon_class': 'bi-shield-check'
            },
            {
                'name': 'Otros Servicios',
                'description': 'Otros servicios municipales no especificados',
                'icon_class': 'bi-gear'
            }
        ]

        for service_data in service_types:
            service_type, created = ServiceType.objects.get_or_create(
                name=service_data['name'],
                defaults=service_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Tipo de servicio creado: {service_type.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Tipo de servicio ya existe: {service_type.name}')
                )

        # Áreas de servicio
        service_areas = [
            'Barrio Claveles',
            'Barrio La Alameda',
            'Barrio La Cuchilla',
            'Barrio Monte Sinaí',
            'Barrio Pobre',
            'Barrio Rico',
            'Camaché Chiquito sector Godínez',
            'Camaché Chiquito sector Loma Larga',
            'Camaché Chiquito sector Patricio',
            'Camaché Chiquito sector Ramírez',
            'Camaché Chiquito sector Silvestre',
            'Camaché Grande sector Camino',
            'Camaché Grande sector Xivir',
            'Chirij-Sin',
            'Colonia Juárez',
            'Colonia Rosales',
            'Colonia San Francisco de Asís',
            'Colonia San Jaime',
            'La Trinidad',
            'Mazá sector Argelia',
            'Mazá sector San Antoñito',
            'Mazá sector San Juan Mazá',
            'Mazá sector San Rubén',
            'Mazá sector Vásquez',
            'San Juan Pabayal',
            'Sector Maxeño'
        ]

        for area_name in service_areas:
            service_area, created = ServiceArea.objects.get_or_create(
                name=area_name
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Área de servicio creada: {service_area.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                '\n=== DATOS INICIALES CREADOS ===\n'
                f'Tipos de servicios: {ServiceType.objects.count()}\n'
                f'Áreas de servicio: {ServiceArea.objects.count()}\n'
            )
        )