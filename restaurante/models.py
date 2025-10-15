
from django.db import models
from django.utils import timezone

class Empleado(models.Model):
    TIPOS_EMPLEADO = [
        ('general', 'Empleado General'),
        ('mesero', 'Mesero'),
    ]
    
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=10, choices=TIPOS_EMPLEADO, default='general')
    zona = models.CharField(max_length=50, blank=True, null=True)
    entrada_registrada = models.BooleanField(default=False)
    ultima_entrada = models.DateTimeField(null=True, blank=True)
    ultima_salida = models.DateTimeField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def registrar_entrada(self):
        if not self.entrada_registrada:
            self.entrada_registrada = True
            self.ultima_entrada = timezone.now()
            self.save()
            return True
        return False
    
    def registrar_salida(self):
        if self.entrada_registrada:
            self.entrada_registrada = False
            self.ultima_salida = timezone.now()
            self.save()
            return True
        return False
    
    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"

class Mesa(models.Model):
    numero = models.IntegerField(unique=True)
    capacidad = models.IntegerField()
    ocupada = models.BooleanField(default=False)
    clientes_actuales = models.IntegerField(default=0)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def ocupar(self, cantidad_clientes):
        if not self.ocupada and cantidad_clientes <= self.capacidad:
            self.ocupada = True
            self.clientes_actuales = cantidad_clientes
            self.save()
            return True
        return False
    
    def liberar(self):
        if self.ocupada:
            self.ocupada = False
            self.clientes_actuales = 0
            self.save()
            return True
        return False
    
    def __str__(self):
        estado = "Ocupada" if self.ocupada else "Libre"
        return f"Mesa {self.numero} - {estado} ({self.clientes_actuales}/{self.capacidad})"
