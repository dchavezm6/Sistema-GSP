from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from decouple import config

User = get_user_model()


class Command(BaseCommand):
    help = 'Crea superusuario desde variables de entorno'

    def handle(self, *args, **options):
        username = config('DJANGO_SUPERUSER_USERNAME', default='admin')
        email = config('DJANGO_SUPERUSER_EMAIL', default='admin@municipalidad.gt')
        password = config('DJANGO_SUPERUSER_PASSWORD', default='Admin2024!Change')

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                first_name='Administrador',
                last_name='Municipal',
                role='ADMIN'
            )
            self.stdout.write(self.style.SUCCESS(f'Superusuario {username} creado'))
        else:
            self.stdout.write(self.style.WARNING('Superusuario ya existe'))