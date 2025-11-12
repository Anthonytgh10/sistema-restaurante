from rest_framework import serializers
from .models import Pedido, DetallePedido
from django.contrib.auth import get_user_model

User = get_user_model()

class DetallePedidoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetallePedido
        fields = ['producto', 'cantidad', 'precio_unitario']

class PedidoCreateSerializer(serializers.Serializer):  # ✅ Usar Serializer en lugar de ModelSerializer
    cliente = serializers.IntegerField()
    observaciones = serializers.CharField(required=False, allow_blank=True)
    detalles = DetallePedidoCreateSerializer(many=True)

    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles')
        
        # Obtener el objeto cliente
        from .models import Cliente
        try:
            cliente = Cliente.objects.get(id=validated_data['cliente'])
        except Cliente.DoesNotExist:
            raise serializers.ValidationError({"cliente": "Cliente no encontrado"})
        
        # Generar número de pedido
        numero_pedido = Pedido.generar_numero_pedido()
        
        # Asignar mesero
        first_user = User.objects.first()
        if not first_user:
            # Crear usuario temporal si no existe
            first_user = User.objects.create_user('temp_user', 'temp@example.com', 'temp123')
        
        # Crear pedido
        pedido = Pedido.objects.create(
            numero_pedido=numero_pedido,
            cliente=cliente,
            mesero=first_user,
            observaciones=validated_data.get('observaciones', '')
        )
        
        # Crear detalles
        for detalle_data in detalles_data:
            DetallePedido.objects.create(pedido=pedido, **detalle_data)
        
        # Calcular totales
        pedido.calcular_totales()
        
        return pedido

    def to_representation(self, instance):
        # Para mostrar los datos después de crear
        from .serializers import PedidoSerializer
        return PedidoSerializer(instance).data