from django.core.management.base import BaseCommand
from apps.requests.models import ServiceArea

class Command(BaseCommand):
    help = 'Crea áreas de servicio iniciales'

    def handle(self, *args, **options):
        areas = [
            'Cantón Camache chiquito, Sector Godínes'
            'Cantón Camache chiquito, Sector Patricio'
            'Cantón Camache chiquito, Sector Ramirez'
            'Cantón Camache chiquito, Sector Silvestre'
            'Cantón Camache Grande Centro'
            'Cantón Camache Grande, Sector Camino'
            'Cantón Maza, San  Rubén'
            'Cantón San Antoñito'
            'Casco Urbano: Barrio la Unión'
            'Casco Urbano: Barrio Pobre'
            'Casco Urbano: Barrio Rico'
            'Casco Urbano: Colonia el Rastro'
            'Casco Urbano: Colonia el Tigre'
            'Casco Urbano: Colonia Juárez'
            'Casco Urbano: Colonia la Bendición'
            'Casco Urbano: Colonia Margarita'
            'Casco Urbano: Colonia San Francisco'
            'Casco Urbano: La Alameda'
            'Casco Urbano: La Cuchilla'
            'Casco Urbano: Monjón'
            'Casco Urbano: Sector Claveles'
            'Casco Urbano: Sector Maxeño'
            'Chirij Sin'
            'Loma larga'
            'Pabayal I'
            'Pabayal II'
            'Pabayal III'
            'San Juan Maza'
            'Sector el Carmen'
            'Sector Vásquez'
        ]

        created = 0
        for area_name in areas:
            area, created_now = ServiceArea.objects.get_or_create(
                name=area_name,
                defaults={'is_active': True}
            )
            if created_now:
                created += 1
                self.stdout.write(f"✓ Creado: {area.name}")
            else:
                self.stdout.write(f"- Ya existe: {area.name}")

        self.stdout.write(
            self.style.SUCCESS(f'\nTotal: {created} áreas de servicio creadas')
        )