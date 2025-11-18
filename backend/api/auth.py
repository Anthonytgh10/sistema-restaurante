from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(["POST"])
def login_view(request):
    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(username=username, password=password)

    if user:
        return Response({"status": "ok", "message": "Login exitoso"})
    else:
        return Response({"status": "error", "message": "Credenciales incorrectas"}, status=400)
