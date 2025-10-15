from rest_framework import serializers
from .models import Empleado, Mesa

class EmpleadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empleado
        fields = ['id', 'nombre', 'tipo', 'zona', 'entrada_registrada', 'ultima_entrada']

class MesaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mesa
        fields = ['id', 'numero', 'capacidad', 'ocupada', 'clientes_actuales']