from django.shortcuts import render
from django.http import JsonResponse
from .models import Empleado, Mesa, Categoria, Producto
from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import EmpleadoSerializer, MesaSerializer, CategoriaSerializer, ProductoSerializer


def dashboard(request):
    total_empleados = Empleado.objects.count()
    empleados_activos = Empleado.objects.filter(entrada_registrada=True).count()
    total_mesas = Mesa.objects.count()
    mesas_ocupadas = Mesa.objects.filter(ocupada=True).count()
    
    context = {
        'total_empleados': total_empleados,
        'empleados_activos': empleados_activos,
        'total_mesas': total_mesas,
        'mesas_ocupadas': mesas_ocupadas,
    }
    return render(request, 'dashboard.html', context)

def lista_empleados(request):
    empleados = Empleado.objects.all()
    return render(request, 'empleados/lista.html', {'empleados': empleados})

def lista_mesas(request):
    mesas = Mesa.objects.all()
    return render(request, 'mesas/lista.html', {'mesas': mesas})
# APIs REST
@api_view(['GET'])
def api_empleados_list(request):
    empleados = Empleado.objects.all()
    serializer = EmpleadoSerializer(empleados, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def api_mesas_list(request):
    mesas = Mesa.objects.all()
    serializer = MesaSerializer(mesas, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def api_registrar_entrada(request, empleado_id):
    try:
        empleado = Empleado.objects.get(id=empleado_id)
        success = empleado.registrar_entrada()
        return Response({'success': success, 'message': 'Entrada registrada' if success else 'Ya tiene entrada registrada'})
    except Empleado.DoesNotExist:
        return Response({'success': False, 'message': 'Empleado no encontrado'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def api_registrar_salida(request, empleado_id):
    try:
        empleado = Empleado.objects.get(id=empleado_id)
        success = empleado.registrar_salida()
        return Response({'success': success, 'message': 'Salida registrada' if success else 'No tiene entrada registrada'})
    except Empleado.DoesNotExist:
        return Response({'success': False, 'message': 'Empleado no encontrado'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def api_ocupar_mesa(request, mesa_id):
    try:
        mesa = Mesa.objects.get(id=mesa_id)
        cantidad_clientes = request.data.get('cantidad_clientes', 1)
        success = mesa.ocupar(cantidad_clientes)
        return Response({'success': success, 'message': 'Mesa ocupada' if success else 'No se pudo ocupar la mesa'})
    except Mesa.DoesNotExist:
        return Response({'success': False, 'message': 'Mesa no encontrada'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def api_liberar_mesa(request, mesa_id):
    try:
        mesa = Mesa.objects.get(id=mesa_id)
        success = mesa.liberar()
        return Response({'success': success, 'message': 'Mesa liberada' if success else 'Mesa ya estaba libre'})
    except Mesa.DoesNotExist:
        return Response({'success': False, 'message': 'Mesa no encontrada'}, status=status.HTTP_404_NOT_FOUND)

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [permissions.IsAuthenticated]  # ajustar según política

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [permissions.IsAuthenticated]  # puedes usar IsAdminUser para crear/editar
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['precio', 'stock', 'nombre']