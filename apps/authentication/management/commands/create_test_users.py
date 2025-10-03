from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()


class Command(BaseCommand):
    help = 'Crear usuarios de prueba para el sistema municipal'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete-existing',
            action='store_true',
            help='Eliminar usuarios existentes antes de crear nuevos',
        )

    def handle(self, *args, **options):
        if options['delete_existing']:
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write(
                self.style.WARNING('Usuarios existentes eliminados.')
            )

        users_data = [
            {
                'username': 'admin_municipal',
                'email': 'admin@municipalidad.gt',
                'first_name': 'Administrador',
                'last_name': 'Municipal',
                'role': 'ADMIN',
                'phone': '+502 1234-5678',
                'address': 'Municipalidad Santo Tomás La Unión',
                'is_staff': True
            },
            {
                'username': 'autoridad_municipal',
                'email': 'autoridad@municipalidad.gt',
                'first_name': 'Ana',
                'last_name': 'Rodríguez',
                'role': 'AUTHORITY',
                'phone': '+502 1234-5679',
                'address': 'Municipalidad Santo Tomás La Unión'
            },
            {
                'username': 'encargado_servicios',
                'email': 'encargado@municipalidad.gt',
                'first_name': 'Carlos',
                'last_name': 'González',
                'role': 'MANAGER',
                'phone': '+502 1234-5680',
                'address': 'Municipalidad Santo Tomás La Unión'
            },
            {
                'username': 'tecnico_agua',
                'email': 'tecnico.agua@municipalidad.gt',
                'first_name': 'María',
                'last_name': 'López',
                'role': 'TECHNICIAN',
                'phone': '+502 1234-5681',
                'address': 'Santo Tomás La Unión'
            },
            {
                'username': 'ciudadano_demo',
                'email': 'juan.perez@email.com',
                'first_name': 'Juan',
                'last_name': 'Pérez',
                'role': 'CITIZEN',
                'phone': '+502 5555-1234',
                'address': 'Barrio El Centro, Santo Tomás La Unión'
            }
        ]

        with transaction.atomic():
            for user_data in users_data:
                user, created = User.objects.get_or_create(
                    username=user_data['username'],
                    defaults=user_data
                )

                if created:
                    user.set_password('municipal2024')
                    user.save()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Usuario {user.username} creado exitosamente'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Usuario {user.username} ya existe'
                        )
                    )

        self.stdout.write(
            self.style.SUCCESS(
                '\n=== USUARIOS DE PRUEBA CREADOS ===\n'
                'Contraseña para todos: municipal2024\n'
                '\nUsuarios disponibles:\n'
                '- admin_municipal (ADMIN)\n'
                '- autoridad_municipal (AUTHORITY)\n'
                '- encargado_servicios (MANAGER)\n'
                '- tecnico_agua (TECHNICIAN)\n'
                '- ciudadano_demo (CITIZEN)\n'
            )
        )