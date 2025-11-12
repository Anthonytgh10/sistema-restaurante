from django.db import models

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta

class Usuario(AbstractUser):
    ROLES = [
        ('ADMIN', 'Administrador'),
        ('MESERO', 'Mesero'),
        ('CAJERO', 'Cajero'),
        ('COCINERO', 'Cocinero'),
    ]

    rol = models.CharField(max_length=20, choices=ROLES, default='MESERO')
    intentos_fallidos = models.IntegerField(default=0)
    bloqueado_hasta = models.DateTimeField(null=True, blank=True)
    activo = models.BooleanField(default=True)

    def esta_bloqueado(self):
        """Verifica si el usuario está temporalmente bloqueado"""
        if self.bloqueado_hasta and timezone.now() < self.bloqueado_hasta:
            return True
        return False

    def registrar_intento_fallido(self):
        """Incrementa los intentos fallidos y bloquea si llega a 5"""
        self.intentos_fallidos += 1
        if self.intentos_fallidos >= 5:
            self.bloqueado_hasta = timezone.now() + timedelta(minutes=15)
            self.intentos_fallidos = 0
        self.save()

    def resetear_intentos(self):
        """Resetea los intentos fallidos"""
        self.intentos_fallidos = 0
        self.save()


class ResetToken(models.Model):
    usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE, related_name='reset_tokens')
    token = models.CharField(max_length=128, unique=True)
    expira_en = models.DateTimeField()
    usado = models.BooleanField(default=False)

    def esta_vigente(self):
        from django.utils import timezone
        return (not self.usado) and timezone.now() <= self.expira_en
