from django.contrib import admin
from .models import Empleado, Mesa

@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo', 'zona', 'entrada_registrada', 'ultima_entrada']
    list_filter = ['tipo', 'entrada_registrada']

@admin.register(Mesa)
class MesaAdmin(admin.ModelAdmin):
    list_display = ['numero', 'capacidad', 'ocupada', 'clientes_actuales']
    list_filter = ['ocupada']
