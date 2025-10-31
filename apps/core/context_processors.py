from django.conf import settings

def site_settings(request):
    """
    Context processor para variables globales del sitio.
    Hace disponibles los logos en todos los templates.
    """
    return {
        'LOGO_MUNICIPALIDAD_URL': getattr(settings, 'LOGO_MUNICIPALIDAD_URL', ''),
        'LOGO_UNIVERSIDAD_URL': getattr(settings, 'LOGO_UNIVERSIDAD_URL', ''),
    }