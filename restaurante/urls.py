from django.urls import path
from . import views  

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('empleados/', views.lista_empleados, name='lista_empleados'),
    path('mesas/', views.lista_mesas, name='lista_mesas'),
    path('api/empleados/', views.api_empleados_list, name='api_empleados_list'),
    path('api/mesas/', views.api_mesas_list, name='api_mesas_list'),
    path('api/empleados/<int:empleado_id>/entrada/', views.api_registrar_entrada, name='api_registrar_entrada'),
    path('api/empleados/<int:empleado_id>/salida/', views.api_registrar_salida, name='api_registrar_salida'),
    path('api/mesas/<int:mesa_id>/ocupar/', views.api_ocupar_mesa, name='api_ocupar_mesa'),
    path('api/mesas/<int:mesa_id>/liberar/', views.api_liberar_mesa, name='api_liberar_mesa'),
    path('api/empleados/', views.api_empleados_list, name='api_empleados'),
    path('api/mesas/', views.api_mesas_list, name='api_mesas'),
    path('api/empleados/<int:empleado_id>/entrada/', views.api_registrar_entrada, name='api_entrada'),
    path('api/empleados/<int:empleado_id>/salida/', views.api_registrar_salida, name='api_salida'),
    path('api/mesas/<int:mesa_id>/ocupar/', views.api_ocupar_mesa, name='api_ocupar_mesa'),
    path('api/mesas/<int:mesa_id>/liberar/', views.api_liberar_mesa, name='api_liberar_mesa'),
]