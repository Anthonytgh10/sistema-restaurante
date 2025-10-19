from rest_framework import serializers
from .models import Empleado, Mesa, Categoria, Producto, Pedido, DetallePedido, Cliente
from django.contrib.auth import get_user_model

class EmpleadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empleado
        fields = ['id', 'nombre', 'tipo', 'zona', 'entrada_registrada', 'ultima_entrada']

class MesaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mesa
        fields = ['id', 'numero', 'capacidad', 'ocupada', 'clientes_actuales']

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'descripcion']

class ProductoSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    
    class Meta:
        model = Producto
        fields = ['id', 'nombre', 'descripcion', 'precio', 'stock', 'categoria', 'categoria_nombre', 'activo', 'created_at', 'updated_at']

class DetallePedidoSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = DetallePedido
        fields = ['id', 'producto', 'producto_nombre', 'cantidad', 'precio_unitario', 'subtotal']

class PedidoSerializer(serializers.ModelSerializer):
    # ✅ CORREGIDO: Agregar required=False para permitir pedidos sin detalles
    detalles = DetallePedidoSerializer(many=True, required=False)
    cliente_nombre = serializers.CharField(source='cliente.nombre', read_only=True)
    mesero_nombre = serializers.CharField(source='mesero.get_full_name', read_only=True)
    
    class Meta:
        model = Pedido
        fields = [
            'id', 'numero_pedido', 'cliente', 'cliente_nombre', 'mesero', 'mesero_nombre',
            'estado', 'fecha_creacion', 'subtotal', 'impuesto_porcentaje', 'impuesto_monto',
            'descuento_porcentaje', 'descuento_monto', 'total', 'observaciones', 'detalles'
        ]
        read_only_fields = ['numero_pedido', 'fecha_creacion', 'subtotal', 'impuesto_monto', 'descuento_monto', 'total', 'mesero']
    
    def create(self, validated_data):
        # ✅ CORREGIDO: Extraer detalles con valor por defecto []
        detalles_data = validated_data.pop('detalles', [])
        
        # Generar número de pedido
        validated_data['numero_pedido'] = Pedido.generar_numero_pedido()
        
        # Asignar mesero desde el request o usar el primer usuario
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            validated_data['mesero'] = request.user
        else:
            User = get_user_model()
            first_user = User.objects.first()
            if first_user:
                validated_data['mesero'] = first_user
        
        # Crear pedido
        pedido = Pedido.objects.create(**validated_data)
        
        # Crear detalles del pedido
        for detalle_data in detalles_data:
            DetallePedido.objects.create(pedido=pedido, **detalle_data)
        
        # Calcular totales
        pedido.calcular_totales()
        
        # Registrar auditoría
        try:
            from .models import AuditLog
            AuditLog.registrar(
                usuario=pedido.mesero,
                accion="CREAR_PEDIDO",
                modelo="Pedido",
                objeto_id=str(pedido.id),
                descripcion=f"Pedido {pedido.numero_pedido} creado",
                request=request
            )
        except Exception as e:
            pass  # Si no existe AuditLog o hay error, continuar
        
        return pedido
    
    def update(self, instance, validated_data):
        # ✅ NUEVO: Permitir actualizar pedidos
        detalles_data = validated_data.pop('detalles', None)
        
        # Actualizar campos del pedido
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Si se proporcionan detalles, actualizar
        if detalles_data is not None:
            # Eliminar detalles anteriores
            instance.detalles.all().delete()
            
            # Crear nuevos detalles
            for detalle_data in detalles_data:
                DetallePedido.objects.create(pedido=instance, **detalle_data)
            
            # Recalcular totales
            instance.calcular_totales()
        
        return instance

class ConfirmarPedidoSerializer(serializers.Serializer):
    motivo_cancelacion = serializers.CharField(required=False, allow_blank=True)

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ['id', 'nombre', 'email', 'telefono', 'direccion']
        read_only_fields = ['id']