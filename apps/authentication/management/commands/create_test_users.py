from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from decouple import config

User = get_user_model()

class Command(BaseCommand):
    help = 'Crea usuarios de prueba para el sistema'

    def handle(self, *args, **options):
        # Password por defecto
        default_password = config('TEST_USER_PASSWORD', default='municipal2024')
        
        users = [
            {
                'username': 'encargado_municipal',
                'email': 'encargado@municipalidad.gt',
                'first_name': 'Juan',
                'last_name': 'Pérez',
                'role': 'MANAGER',
                'phone': '78901234',
            },
            {
                'username': 'tecnico_agua',
                'email': 'tecnico.agua@municipalidad.gt',
                'first_name': 'Carlos',
                'last_name': 'López',
                'role': 'TECHNICIAN',
                'phone': '78905678',
            },
            {
                'username': 'tecnico_electricidad',
                'email': 'tecnico.luz@municipalidad.gt',
                'first_name': 'María',
                'last_name': 'García',
                'role': 'TECHNICIAN',
                'phone': '78909012',
            },
            {
                'username': 'ciudadano_demo',
                'email': 'ciudadano@example.com',
                'first_name': 'Pedro',
                'last_name': 'Rodríguez',
                'role': 'CITIZEN',
                'phone': '78903456',
            },
        ]
        
        created = 0
        for user_data in users:
            if not User.objects.filter(username=user_data['username']).exists():
                user = User.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    password=default_password,
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    role=user_data['role'],
                    phone=user_data.get('phone', ''),
                )
                created += 1
                self.stdout.write(f"✓ Creado: {user.username} ({user.get_role_display()})")
            else:
                self.stdout.write(f"- Ya existe: {user_data['username']}")
        
        self.stdout.write(
            self.style.SUCCESS(f'\nTotal: {created} usuarios creados')
        )
        self.stdout.write(f'Password por defecto: {default_password}')