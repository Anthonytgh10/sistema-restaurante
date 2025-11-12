# Crear esta estructura:
# restaurante/management/commands/crear_grupos.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Crea grupos de usuarios con permisos predeterminados'
    
    def handle(self, *args, **options):
        # Grupo Meseros
        meseros, created = Group.objects.get_or_create(name='Meseros')
        meseros_perms = [
            'add_pedido', 'view_pedido', 'change_pedido',
            'add_detallepedido', 'view_detallepedido',
            'view_producto', 'view_cliente'
        ]
        meseros.permissions.set(Permission.objects.filter(codename__in=meseros_perms))
        
        # Grupo Cajeros
        cajeros, created = Group.objects.get_or_create(name='Cajeros')
        cajeros_perms = meseros_perms + [
            'restaurante.can_confirm_pedido', 'restaurante.can_cancel_pedido'
        ]
        cajeros.permissions.set(Permission.objects.filter(codename__in=cajeros_perms))
        
        # Grupo Administradores
        admins, created = Group.objects.get_or_create(name='Administradores')
        admins.permissions.set(Permission.objects.all())
        
        self.stdout.write(
            self.style.SUCCESS('Grupos creados exitosamente: Meseros, Cajeros, Administradores')
        )