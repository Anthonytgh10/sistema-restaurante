
from django.urls import path
from .views import LoginView, LogoutView, UsuarioView, PasswordResetRequestView, PasswordResetConfirmView

urlpatterns = [
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('usuarios/', UsuarioView.as_view(), name='usuarios'),
    path('auth/password/reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('auth/password/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]
