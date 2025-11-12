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
    authentication_classes = []  # JWT por defecto (settings)
    permission_classes = [permissions.IsAuthenticated]
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
    authentication_classes = []  # JWT por defecto (settings)
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['precio', 'stock', 'nombre']

# ✅ CLASE CATEGORIA - PERMISOS COMPLETAMENTE ABIERTOS
class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    authentication_classes = []  # JWT por defecto (settings)
    permission_classes = [permissions.IsAuthenticated]

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

from rest_framework.decorators import action
from django.db import transaction
from decimal import Decimal
from .models import Producto, Pedido, DetallePedido, Cliente, AuditLog

@action(detail=True, methods=['post'], url_path='confirmar')
def confirmar(self, request, pk=None):
    pedido = self.get_object()
    # Validar stock
    with transaction.atomic():
        for det in pedido.detalles.select_related('producto').all():
            if det.producto.stock < det.cantidad:
                return Response({'error': f'Sin stock para {det.producto.nombre}'}, status=400)
        # Descontar stock
        for det in pedido.detalles.select_related('producto').all():
            prod = det.producto
            prod.stock -= det.cantidad
            prod.save()
    pedido.estado = 'confirmado'
    pedido.save()
    AuditLog.registrar(usuario=request.user, accion='pedido_confirmado', modelo='Pedido', objeto_id=pedido.id)
    return Response({'message': 'Pedido confirmado'})

@action(detail=True, methods=['post'], url_path='pagar')
def pagar(self, request, pk=None):
    pedido = self.get_object()
    metodo = request.data.get('metodo', 'efectivo')
    monto = request.data.get('monto')
    try:
        monto = Decimal(monto) if monto is not None else pedido.total
    except Exception:
        return Response({'error': 'Monto inválido'}, status=400)
    # Registrar pago simple y cerrar
    pedido.estado = 'pagado'
    pedido.save()
    AuditLog.registrar(usuario=request.user, accion='pedido_pagado', modelo='Pedido', objeto_id=pedido.id, 
                       descripcion=f'Método: {metodo}, Monto: {monto}')
    return Response({'message': 'Pago registrado'})

@action(detail=True, methods=['post'], url_path='cancelar')
def cancelar(self, request, pk=None):
    pedido = self.get_object()
    motivo = request.data.get('motivo', 'N/D')
    # Revertir stock si estaba confirmado
    if pedido.estado in ['confirmado','pagado']:
        for det in pedido.detalles.select_related('producto').all():
            prod = det.producto
            prod.stock += det.cantidad
            prod.save()
    pedido.estado = 'cancelado'
    pedido.save()
    AuditLog.registrar(usuario=request.user, accion='pedido_cancelado', modelo='Pedido', objeto_id=pedido.id,
                       descripcion=f'Motivo: {motivo}')
    return Response({'message': 'Pedido cancelado'})

@action(detail=False, methods=['get'], url_path='reportes')
def reportes(self, request):
    # Filtros: fecha_desde, fecha_hasta, cliente, mesero
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
    # Export CSV si ?export=csv
    if request.query_params.get('export') == 'csv':
        import csv
        from django.http import HttpResponse
        resp = HttpResponse(content_type='text/csv')
        resp['Content-Disposition'] = 'attachment; filename="reportes_pedidos.csv"'
        w = csv.writer(resp)
        w.writerow(['#','Cliente','Mesero','Estado','Subtotal','Impuesto','Descuento','Total','Fecha'])
        for p in qs:
            w.writerow([p.numero_pedido, getattr(p.cliente,'nombre',''), getattr(p.mesero,'username',''),
                        p.estado, p.subtotal, p.impuesto_monto, p.descuento_monto, p.total, p.fecha_creacion])
        return resp
    return Response(data)
