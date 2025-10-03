from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CustomLoginForm, CitizenRegistrationForm, UserProfileForm
from .models import User


class CustomLoginView(LoginView):
    form_class = CustomLoginForm
    template_name = 'auth/login.html'

    def get_success_url(self):
        return reverse_lazy('authentication:dashboard')


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('authentication:login')


class CitizenRegistrationView(CreateView):
    model = User
    form_class = CitizenRegistrationForm
    template_name = 'auth/register.html'
    success_url = reverse_lazy('authentication:login')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            'Tu cuenta ha sido creada exitosamente. Ya puedes iniciar sesión.'
        )
        return response


class UserProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'auth/profile.html'

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Tu perfil ha sido actualizado exitosamente.')
        return response


@login_required
def dashboard_view(request):
    """Vista del dashboard principal que redirige según el rol del usuario"""
    user = request.user

    context = {
        'user': user,
        'role_display': user.get_role_display(),
    }

    if user.is_admin():
        template = 'dashboard/admin.html'
    elif user.is_authority():
        template = 'dashboard/authority.html'
    elif user.is_manager():
        template = 'dashboard/manager.html'
    elif user.is_technician():
        template = 'dashboard/technician.html'
    else:  # CITIZEN
        template = 'dashboard/citizen.html'

    return render(request, template, context)