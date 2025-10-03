from django.apps import AppConfig


class RequestsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.requests'
    verbose_name = 'Gestión de Solicitudes'

    def ready(self):
        import apps.requests.signals