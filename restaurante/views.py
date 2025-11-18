# restaurante/views.py

from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import authenticate, get_user_model
from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from django.db import transaction
from decimal import Decimal

from .models import (
    Empleado, Mesa, Categoria, Producto, Pedido,
    DetallePedido, Cliente, AuditLog
)

from .serializers import (
    EmpleadoSerializer, MesaSerializer, CategoriaSerializer,
    ProductoSerializer, PedidoSerializer, ConfirmarPedidoSerializer
)

from .serializers_create import PedidoCreateSerializer

User = get_user_model()

# -----------------------------------------------------------------------------
# LOGIN SIMPLE
# -----------------------------------------------------------------------------
@api_view(["POST"])
def api_login(request):
    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(username=username, password=password)

    if user is not None:
        return JsonResponse({"status": "ok", "user": user.username})
    else:
        return JsonResponse(
            {"status": "error", "message": "Credenciales incorrectas"},
            status=400
        )

# -----------------------------------------------------------------------------
# HOME API
# -----------------------------------------------------------------------------
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
        }
    })

# -----------------------------------------------------------------------------
#     VIEWSETS PRINCIPALES
# -----------------------------------------------------------------------------

# PEDIDO
class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all().order_by('-fecha_creacion')
    authentication_classes = []          # anula JWT del settings
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.action == 'create':
            return PedidoCreateSerializer
        return PedidoSerializer

    def create(self, request, *args, **kwargs):
        print("📦 DATOS RECIBIDOS:", request.data)
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        # asignar usuario por defecto
        first_user = User.objects.first()
        if not first_user:
            first_user = User.objects.create_user(
                username='temp_user',
                email='temp@example.com',
                password='temp_password'
            )
        serializer.save(mesero=first_user)

    # CONFIRMAR PEDIDO
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
            }, status=400)

    # CANCELAR
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
        return Response(serializer.errors, status=400)

    # VALIDAR STOCK
    @action(detail=True, methods=['get'])
    def validar_stock(self, request, pk=None):
        pedido = self.get_object()
        errores = pedido.validar_stock()
        return Response({
            'valido': len(errores) == 0,
            'errores': errores
        })


# PRODUCTO
class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.filter(activo=True)
    serializer_class = ProductoSerializer
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['precio', 'stock', 'nombre']


# CATEGORIA
class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    authentication_classes = []
    permission_classes = [permissions.AllowAny]


# -----------------------------------------------------------------------------
#     APIS SIMPLES (empleados, mesas…)
# -----------------------------------------------------------------------------

@api_view(['GET'])
def api_empleados_list(request):
    empleados = Empleado.objects.all()
    return Response(EmpleadoSerializer(empleados, many=True).data)


@api_view(['GET'])
def api_mesas_list(request):
    mesas = Mesa.objects.all()
    return Response(MesaSerializer(mesas, many=True).data)


@api_view(['POST'])
def api_registrar_entrada(request, empleado_id):
    try:
        empleado = Empleado.objects.get(id=empleado_id)
        success = empleado.registrar_entrada()
        return Response({'success': success})
    except Empleado.DoesNotExist:
        return Response({'success': False}, status=404)


@api_view(['POST'])
def api_registrar_salida(request, empleado_id):
    try:
        empleado = Empleado.objects.get(id=empleado_id)
        success = empleado.registrar_salida()
        return Response({'success': success})
    except Empleado.DoesNotExist:
        return Response({'success': False}, status=404)


@api_view(['POST'])
def api_ocupar_mesa(request, mesa_id):
    try:
        mesa = Mesa.objects.get(id=mesa_id)
        cant = request.data.get('cantidad_clientes', 1)
        success = mesa.ocupar(cant)
        return Response({'success': success})
    except Mesa.DoesNotExist:
        return Response({'success': False}, status=404)


@api_view(['POST'])
def api_liberar_mesa(request, mesa_id):
    try:
        mesa = Mesa.objects.get(id=mesa_id)
        success = mesa.liberar()
        return Response({'success': success})
    except Mesa.DoesNotExist:
        return Response({'success': False}, status=404)


# -----------------------------------------------------------------------------
#    REPORTES (GET /api/pedidos/reportes)
# -----------------------------------------------------------------------------

@action(detail=False, methods=['get'])
def reportes(self, request):
    desde = request.query_params.get('desde')
    hasta = request.query_params.get('hasta')
    cliente = request.query_params.get('cliente')
    mesero = request.query_params.get('mesero')

    qs = Pedido.objects.all().order_by('-fecha_creacion')

    if desde: qs = qs.filter(fecha_creacion__date__gte=desde)
    if hasta: qs = qs.filter(fecha_creacion__date__lte=hasta)
    if cliente: qs = qs.filter(cliente__nombre__icontains=cliente)
    if mesero: qs = qs.filter(mesero__username__icontains=mesero)

    total_pedidos = qs.count()
    total_ventas = sum([p.total for p in qs])

    por_estado = {}
    for p in qs:
        por_estado[p.estado] = por_estado.get(p.estado, 0) + 1

    data = {
        'total_pedidos': total_pedidos,
        'total_ventas': str(total_ventas),
        'por_estado': por_estado,
    }

    return Response(data)
