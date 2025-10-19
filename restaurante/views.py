from django.shortcuts import render
from django.http import JsonResponse
from .models import Empleado, Mesa, Categoria, Producto, Pedido, DetallePedido, Cliente
from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import EmpleadoSerializer, MesaSerializer, CategoriaSerializer, ProductoSerializer, PedidoSerializer, ConfirmarPedidoSerializer
from django.db import transaction
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from .serializers_create import PedidoCreateSerializer
User = get_user_model()

def home(request):
    return JsonResponse({
        'message': '🚀 Sistema de Restaurante - API funcionando!',
        'endpoints_disponibles': {
            'pedidos': '/api/pedidos/',
            'productos': '/api/productos/', 
            'categorias': '/api/categorias/',
            'empleados': '/api/empleados/',
            'mesas': '/api/mesas/',
            'admin_panel': '/admin/'
        },
        'instrucciones': 'Visita /api/pedidos/ para gestionar pedidos'
    })


# ✅ CLASE PEDIDO - PERMISOS COMPLETAMENTE ABIERTOS
class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all().order_by('-fecha_creacion')
    serializer_class = PedidoSerializer
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    def get_serializer_class(self):
        if self.action == 'create':
            return PedidoCreateSerializer  # ✅ Usar el nuevo serializer para crear
        return PedidoSerializer
    def create(self, request, *args, **kwargs):
        print("📦 DATOS RECIBIDOS:", request.data)  # ✅ Ver qué llega
        print("📦 TIPO DE DATOS:", type(request.data))
        return super().create(request, *args, **kwargs)
    def perform_create(self, serializer):
        # Asignar un usuario por defecto
        first_user = User.objects.first()
        if first_user:
            serializer.save(mesero=first_user)
        else:
            # Crear usuario temporal si no existe
            temp_user = User.objects.create_user(
                username='temp_user', 
                email='temp@example.com', 
                password='temp_password'
            )
            serializer.save(mesero=temp_user)
    
    @action(detail=True, methods=['post'])
    def confirmar(self, request, pk=None):
        pedido = self.get_object()
        try:
            with transaction.atomic():
                pedido.confirmar_pedido()
            return Response({
                'status': 'confirmado',
                'message': f'Pedido {pedido.numero_pedido} confirmado exitosamente'
            })
        except ValueError as e:
            return Response({
                'error': 'Stock insuficiente',
                'detalles': str(e).split(' | ')
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        pedido = self.get_object()
        serializer = ConfirmarPedidoSerializer(data=request.data)
        if serializer.is_valid():
            motivo = serializer.validated_data.get('motivo_cancelacion', '')
            with transaction.atomic():
                pedido.cancelar_pedido(motivo)
            return Response({
                'status': 'cancelado',
                'message': f'Pedido {pedido.numero_pedido} cancelado'
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def validar_stock(self, request, pk=None):
        pedido = self.get_object()
        errores = pedido.validar_stock()
        return Response({
            'valido': len(errores) == 0,
            'errores': errores
        })

# ✅ CLASE PRODUCTO - PERMISOS COMPLETAMENTE ABIERTOS
class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.filter(activo=True)
    serializer_class = ProductoSerializer
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['precio', 'stock', 'nombre']

# ✅ CLASE CATEGORIA - PERMISOS COMPLETAMENTE ABIERTOS
class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

# ✅ APIs REST SIMPLIFICADAS
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