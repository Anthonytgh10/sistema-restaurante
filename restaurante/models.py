from django.db import models
from django.utils import timezone
from decimal import Decimal
from django.conf import settings

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

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True, related_name='productos')
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ['nombre']

class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.TextField(blank=True)
    
    def __str__(self):
        return self.nombre

class Pedido(models.Model):
    ESTADO_CHOICES = (
        ('borrador', 'Borrador'),
        ('confirmado', 'Confirmado'),
        ('preparando', 'En Preparación'),
        ('pagado', 'Pagado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    )
    
    numero_pedido = models.CharField(max_length=20, unique=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    # ✅ CORREGIDO: 'usuarios.Usuario' (con 's')
    mesero = models.ForeignKey('usuarios.Usuario', on_delete=models.PROTECT, related_name='pedidos_mesero')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='borrador')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_confirmacion = models.DateTimeField(null=True, blank=True)
    fecha_entrega = models.DateTimeField(null=True, blank=True)
    
    # Campos de cálculo
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    impuesto_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, default=13)
    impuesto_monto = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    descuento_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    descuento_monto = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    observaciones = models.TextField(blank=True)
    
    class Meta:
        permissions = [
            ("can_confirm_pedido", "Puede confirmar pedidos"),
            ("can_cancel_pedido", "Puede cancelar pedidos"),
            ("can_manage_pedidos", "Puede gestionar todos los pedidos"),
        ]
    
    def __str__(self):
        return f"Pedido {self.numero_pedido} - {self.cliente.nombre}"
    
    def calcular_totales(self):
        self.subtotal = sum(detalle.subtotal for detalle in self.detalles.all())
        self.descuento_monto = (self.subtotal * self.descuento_porcentaje) / Decimal('100')
        base_impuesto = self.subtotal - self.descuento_monto
        self.impuesto_monto = (base_impuesto * self.impuesto_porcentaje) / Decimal('100')
        self.total = base_impuesto + self.impuesto_monto
        self.save(update_fields=['subtotal', 'descuento_monto', 'impuesto_monto', 'total'])
    
    def validar_stock(self):
        errores = []
        for detalle in self.detalles.all():
            if detalle.producto.stock < detalle.cantidad:
                errores.append(
                    f"Stock insuficiente para {detalle.producto.nombre}. "
                    f"Disponible: {detalle.producto.stock}, Solicitado: {detalle.cantidad}"
                )
        return errores
    
    def confirmar_pedido(self):
        errores = self.validar_stock()
        if errores:
            raise ValueError(" | ".join(errores))
        
        for detalle in self.detalles.all():
            detalle.producto.stock -= detalle.cantidad
            detalle.producto.save()
        
        self.estado = 'confirmado'
        self.fecha_confirmacion = timezone.now()
        self.save()
        
        AuditLog.registrar(
            usuario=self.mesero,
            accion="CONFIRMAR_PEDIDO",
            modelo="Pedido",
            objeto_id=self.id,
            descripcion=f"Pedido {self.numero_pedido} confirmado"
        )
    
    def cancelar_pedido(self, motivo=""):
        if self.estado == 'confirmado':
            for detalle in self.detalles.all():
                detalle.producto.stock += detalle.cantidad
                detalle.producto.save()
        
        self.estado = 'cancelado'
        self.save()
        
        AuditLog.registrar(
            usuario=self.mesero,
            accion="CANCELAR_PEDIDO",
            modelo="Pedido",
            objeto_id=self.id,
            descripcion=f"Pedido {self.numero_pedido} cancelado. Motivo: {motivo}"
        )
    
    @classmethod
    def generar_numero_pedido(cls):
        ultimo_pedido = cls.objects.order_by('-id').first()
        if ultimo_pedido and ultimo_pedido.numero_pedido:
            try:
                ultimo_numero = int(ultimo_pedido.numero_pedido.split('-')[1])
                nuevo_numero = ultimo_numero + 1
            except (IndexError, ValueError):
                nuevo_numero = 1
        else:
            nuevo_numero = 1
        return f"PED-{nuevo_numero:06d}"

class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.IntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)
        if self.pedido:
            self.pedido.calcular_totales()
    
    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"

class AuditLog(models.Model):
    # ✅ CORREGIDO: 'usuarios.Usuario' (con 's')
    usuario = models.ForeignKey('usuarios.Usuario', on_delete=models.CASCADE)
    accion = models.CharField(max_length=100)
    modelo = models.CharField(max_length=100)
    objeto_id = models.CharField(max_length=100, blank=True)
    descripcion = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'audit_log'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.accion} - {self.timestamp}"
    
    @classmethod
    def registrar(cls, usuario, accion, modelo, objeto_id="", descripcion="", request=None):
        ip_address = None
        if request:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            ip_address = ip
        
        return cls.objects.create(
            usuario=usuario,
            accion=accion,
            modelo=modelo,
            objeto_id=objeto_id,
            descripcion=descripcion,
            ip_address=ip_address
        )