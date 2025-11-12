
from django.utils import timezone
from django.contrib.auth import authenticate, get_user_model
from django.db import transaction
from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from .models import Usuario, ResetToken
from .serializers import (
    UsuarioSerializer, UsuarioCreateSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer
)
from restaurante.models import AuditLog
from django.core.mail import send_mail
from django.conf import settings
import secrets
from datetime import timedelta

def _get_ip(request):
    xf = request.META.get('HTTP_X_FORWARDED_FOR')
    return xf.split(',')[0] if xf else request.META.get('REMOTE_ADDR')

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username_or_email = request.data.get('username') or ''
        password = request.data.get('password') or ''

        try:
            if '@' in username_or_email:
                user = Usuario.objects.get(email=username_or_email)
                username = user.username
            else:
                user = Usuario.objects.get(username=username_or_email)
                username = username_or_email
        except Usuario.DoesNotExist:
            # Mensaje genérico
            return Response({'error': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)

        if user.esta_bloqueado():
            AuditLog.registrar(usuario=user, accion='login_bloqueado', modelo='Usuario', objeto_id=user.id,
                               descripcion='Cuenta bloqueada por intentos fallidos', ip_address=_get_ip(request))
            return Response({'error': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)

        user_auth = authenticate(username=username, password=password)
        if user_auth is not None and user_auth.is_active:
            user.resetear_intentos()
            refresh = RefreshToken.for_user(user_auth)
            AuditLog.registrar(usuario=user_auth, accion='login_ok', modelo='Usuario', objeto_id=user_auth.id,
                               descripcion='Inicio de sesión exitoso', ip_address=_get_ip(request))
            return Response({
                'message': 'Inicio de sesión exitoso',
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'rol': user_auth.rol
            })
        else:
            user.registrar_intento_fallido()
            AuditLog.registrar(usuario=user, accion='login_fail', modelo='Usuario', objeto_id=user.id,
                               descripcion='Intento de inicio de sesión fallido', ip_address=_get_ip(request))
            return Response({'error': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(APIView):
    def post(self, request):
        # Invalida todos los refresh tokens del usuario (logout global)
        for token in OutstandingToken.objects.filter(user=request.user):
            BlacklistedToken.objects.get_or_create(token=token)
        AuditLog.registrar(usuario=request.user, accion='logout', modelo='Usuario', objeto_id=request.user.id,
                           descripcion='Cierre de sesión manual', ip_address=_get_ip(request))
        return Response({'message': 'Sesión cerrada'})

class UsuarioView(APIView):
    def get(self, request):
        # Listado + filtros básicos por rol/estado/búsqueda
        qs = Usuario.objects.all().order_by('-date_joined')
        rol = request.query_params.get('rol')
        estado = request.query_params.get('estado')
        q = request.query_params.get('q')
        if rol: qs = qs.filter(rol=rol)
        if estado == 'activo': qs = qs.filter(is_active=True)
        elif estado == 'inactivo': qs = qs.filter(is_active=False)
        if q: qs = qs.filter(username__icontains=q) | qs.filter(email__icontains=q)
        data = UsuarioSerializer(qs, many=True).data
        return Response(data)

    def post(self, request):
        # Crear usuario (no se elimina; solo desactiva)
        ser = UsuarioCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = ser.save()
        AuditLog.registrar(usuario=request.user, accion='usuario_creado', modelo='Usuario',
                           objeto_id=user.id, descripcion='Creación de usuario')
        # Envío de correo simple (puede reemplazarse por plantilla real)
        try:
            send_mail(
                subject='Credenciales de acceso',
                message=f"Usuario: {user.username}\nRol: {user.rol}",
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
                recipient_list=[user.email],
                fail_silently=True
            )
        except Exception:
            pass
        return Response(UsuarioSerializer(user).data, status=status.HTTP_201_CREATED)

    def patch(self, request):
        # Editar datos básicos y rol
        uid = request.data.get('id')
        user = Usuario.objects.get(id=uid)
        for f in ['first_name','last_name','email','rol','is_active']:
            if f in request.data:
                setattr(user, f, request.data.get(f))
        user.save()
        AuditLog.registrar(usuario=request.user, accion='usuario_editado', modelo='Usuario',
                           objeto_id=user.id, descripcion='Edición de datos/rol')
        return Response(UsuarioSerializer(user).data)

    def delete(self, request):
        # No se elimina: se desactiva
        uid = request.data.get('id')
        user = Usuario.objects.get(id=uid)
        user.is_active = False
        user.save()
        AuditLog.registrar(usuario=request.user, accion='usuario_desactivado', modelo='Usuario',
                           objeto_id=user.id, descripcion='Desactivación (soft delete)')
        return Response({'message': 'Usuario desactivado'})

class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        ser = PasswordResetRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        email = ser.validated_data['email']
        try:
            user = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            # Mensaje genérico
            return Response({'message': 'Si el correo existe, se enviará un enlace.'})
        token = secrets.token_urlsafe(32)
        expira = timezone.now() + timedelta(minutes=15)
        ResetToken.objects.create(usuario=user, token=token, expira_en=expira)
        # Envío de correo (simplificado)
        try:
            send_mail(
                subject='Recuperación de contraseña',
                message=f'Usa este token para restablecer tu contraseña (15 min): {token}',
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
                recipient_list=[user.email],
                fail_silently=True,
            )
        except Exception:
            pass
        AuditLog.registrar(usuario=user, accion='reset_solicitado', modelo='Usuario',
                           objeto_id=user.id, descripcion='Solicitud de reseteo de contraseña')
        return Response({'message': 'Si el correo existe, se enviará un enlace.'})

class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        ser = PasswordResetConfirmSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        token = ser.validated_data['token']
        new_pwd = ser.validated_data['new_password']
        try:
            t = ResetToken.objects.get(token=token)
        except ResetToken.DoesNotExist:
            return Response({'error': 'Token inválido'}, status=400)
        if not t.esta_vigente():
            return Response({'error': 'Token expirado o usado'}, status=400)
        user = t.usuario
        user.set_password(new_pwd)
        user.save()
        t.usado = True
        t.save()
        AuditLog.registrar(usuario=user, accion='reset_confirmado', modelo='Usuario',
                           objeto_id=user.id, descripcion='Contraseña restablecida')
        return Response({'message': 'Contraseña actualizada'})
