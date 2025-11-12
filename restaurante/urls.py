from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'pedidos', views.PedidoViewSet)
router.register(r'productos', views.ProductoViewSet)
router.register(r'categorias', views.CategoriaViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    
    # ✅ SOLO esta vista existe - las demás están comentadas
    path('', views.home, name='home'),
    
    # APIs individuales (opcionales)
    path('api/empleados/', views.api_empleados_list, name='api_empleados_list'),
    path('api/mesas/', views.api_mesas_list, name='api_mesas_list'),
    path('api/empleados/<int:empleado_id>/entrada/', views.api_registrar_entrada, name='api_registrar_entrada'),
    path('api/empleados/<int:empleado_id>/salida/', views.api_registrar_salida, name='api_registrar_salida'),
    path('api/mesas/<int:mesa_id>/ocupar/', views.api_ocupar_mesa, name='api_ocupar_mesa'),
    path('api/mesas/<int:mesa_id>/liberar/', views.api_liberar_mesa, name='api_liberar_mesa'),
]