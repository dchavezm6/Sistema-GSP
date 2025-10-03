from django.urls import path
from .views import (
    CustomLoginView,
    CustomLogoutView,
    CitizenRegistrationView,
    UserProfileView,
    dashboard_view
)

app_name = 'authentication'

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('register/', CitizenRegistrationView.as_view(), name='register'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('dashboard/', dashboard_view, name='dashboard'),
]