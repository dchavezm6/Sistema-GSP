from django.core.management.base import BaseCommand
from apps.requests.models import ServiceArea

class Command(BaseCommand):
    help = 'Crea áreas de servicio iniciales'

    def handle(self, *args, **options):
        areas = [
            {'name':'Cantón Camache chiquito, Sector Godínes'},
            {'name':'Cantón Camache chiquito, Sector Patricio'},
            {'name':'Cantón Camache chiquito, Sector Ramirez'},
            {'name':'Cantón Camache chiquito, Sector Silvestre'},
            {'name':'Cantón Camache Grande Centro'},
            {'name':'Cantón Camache Grande, Sector Camino'},
            {'name':'Cantón Maza, San  Rubén'},
            {'name':'Cantón San Antoñito'},
            {'name':'Casco Urbano: Barrio la Unión'},
            {'name':'Casco Urbano: Barrio Pobre'},
            {'name':'Casco Urbano: Barrio Rico'},
            {'name':'Casco Urbano: Colonia el Rastro'},
            {'name':'Casco Urbano: Colonia el Tigre'},
            {'name':'Casco Urbano: Colonia Juárez'},
            {'name':'Casco Urbano: Colonia la Bendición'},
            {'name':'Casco Urbano: Colonia Margarita'},
            {'name':'Casco Urbano: Colonia San Francisco'},
            {'name':'Casco Urbano: La Alameda'},
            {'name':'Casco Urbano: La Cuchilla'},
            {'name':'Casco Urbano: Monjón'},
            {'name':'Casco Urbano: Sector Claveles'},
            {'name':'Casco Urbano: Sector Maxeño'},
            {'name':'Chirij Sin'},
            {'name':'Loma larga'},
            {'name':'Pabayal I'},
            {'name':'Pabayal II'},
            {'name':'Pabayal III'},
            {'name':'San Juan Maza'},
            {'name':'Sector el Carmen'},
            {'name':'Sector Vásquez'},
        ]
        
        created = 0
        for area_data in areas:
            area, created_now = ServiceArea.objects.get_or_create(
                name=area_data['name'],
                defaults={
                    'description': area_data['description'],
                    'is_active': True
                }
            )
            if created_now:
                created += 1
                self.stdout.write(f"✓ Creado: {area.name}")
            else:
                self.stdout.write(f"- Ya existe: {area.name}")
        
        self.stdout.write(
            self.style.SUCCESS(f'\nTotal: {created} áreas de servicio creadas')
        )