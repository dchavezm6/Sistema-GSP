# config/wsgi.py

import os
from django.core.wsgi import get_wsgi_application

# Usar configuración de producción por defecto
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

application = get_wsgi_application()