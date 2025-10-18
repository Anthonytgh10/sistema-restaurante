from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Usuario

class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        try:
            user = Usuario.objects.get(username=username)
        except Usuario.DoesNotExist:
            return Response({"error": "Credenciales inválidas"}, status=status.HTTP_401_UNAUTHORIZED)

        if user.esta_bloqueado():
            return Response({"error": "Cuenta bloqueada. Intente en 15 minutos."}, status=status.HTTP_403_FORBIDDEN)

        user_auth = authenticate(username=username, password=password)

        if user_auth is not None:
            user.resetear_intentos()
            refresh = RefreshToken.for_user(user_auth)
            return Response({
                "message": "Inicio de sesión exitoso",
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "rol": user_auth.rol
            })
        else:
            user.registrar_intento_fallido()
            return Response({"error": "Credenciales inválidas"}, status=status.HTTP_401_UNAUTHORIZED)

