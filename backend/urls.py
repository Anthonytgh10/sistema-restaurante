from django.contrib import admin
from django.urls import path, include   # login correcto
from django.http import HttpResponse
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("api/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("", lambda request: HttpResponse("Backend funcionando correctamente")),
    
    # Admin de Django
    path('admin/', admin.site.urls),

    # Rutas API del restaurante (pedidos, productos, categorías, etc.)
    path('api/', include('restaurante.urls')),

    # Rutas API de usuarios
    path('api/', include('usuarios.urls')),
]



