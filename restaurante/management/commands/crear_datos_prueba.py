import os
import django
from django.core.management.base import BaseCommand
from restaurante.models import Empleado, Mesa

class Command(BaseCommand):
    help = 'Crea datos de prueba para el sistema de restaurante'

    def handle(self, *args, **options):
        # Crear empleados
        empleados = [
            {'nombre': 'Ana García', 'tipo': 'mesero', 'zona': 'Terraza'},
            {'nombre': 'Carlos López', 'tipo': 'mesero', 'zona': 'Interior'},
            {'nombre': 'María Rodríguez', 'tipo': 'general', 'zona': None},
        ]
        
        for emp_data in empleados:
            empleado, created = Empleado.objects.get_or_create(
                nombre=emp_data['nombre'],
                defaults=emp_data
            )
            if created:
                self.stdout.write(f'✅ Empleado creado: {emp_data["nombre"]}')
        
        # Crear mesas
        mesas = [
            {'numero': 1, 'capacidad': 4},
            {'numero': 2, 'capacidad': 2},
            {'numero': 3, 'capacidad': 6},
            {'numero': 4, 'capacidad': 4},
        ]
        
        for mesa_data in mesas:
            mesa, created = Mesa.objects.get_or_create(
                numero=mesa_data['numero'],
                defaults=mesa_data
            )
            if created:
                self.stdout.write(f'✅ Mesa creada: {mesa_data["numero"]}')
        
        self.stdout.write('🎉 ¡Datos de prueba creados exitosamente!')