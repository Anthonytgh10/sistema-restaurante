# Crear este archivo nuevo en la carpeta restaurant/

from rest_framework import permissions

class IsMesero(permissions.BasePermission):
    """Permiso para meseros: pueden crear pedidos y ver los suyos"""
    def has_permission(self, request, view):
        return request.user.has_perm('restaurant.can_manage_pedidos') or \
               request.user.groups.filter(name='Meseros').exists()

class IsCajero(permissions.BasePermission):
    """Permiso para cajeros: pueden confirmar pagos"""
    def has_permission(self, request, view):
        return request.user.has_perm('restaurant.can_confirm_pedido') or \
               request.user.groups.filter(name='Cajeros').exists()

class IsAdminOrReadOnly(permissions.BasePermission):
    """Solo admin puede modificar, otros solo leer"""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

class PuedeGestionarPedidos(permissions.BasePermission):
    """Puede gestionar todos los pedidos"""
    def has_permission(self, request, view):
        return request.user.has_perm('restaurant.can_manage_pedidos')