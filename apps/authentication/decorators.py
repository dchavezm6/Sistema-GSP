from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def role_required(allowed_roles):
    """
    Decorador que verifica si el usuario tiene uno de los roles permitidos.
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(
                    request, 
                    'No tienes permisos para acceder a esta página.'
                )
                return redirect('authentication:dashboard')
        return _wrapped_view
    return decorator

def admin_required(view_func):
    """Decorador para vistas que requieren rol de administrador."""
    return role_required(['ADMIN'])(view_func)

def manager_required(view_func):
    """Decorador para vistas que requieren rol de encargado o superior."""
    return role_required(['ADMIN', 'MANAGER'])(view_func)

def technician_required(view_func):
    """Decorador para vistas que requieren rol de técnico o superior."""
    return role_required(['ADMIN', 'MANAGER', 'TECHNICIAN'])(view_func)

def authority_required(view_func):
    """Decorador para vistas que requieren rol de autoridad o superior."""
    return role_required(['ADMIN', 'AUTHORITY'])(view_func)