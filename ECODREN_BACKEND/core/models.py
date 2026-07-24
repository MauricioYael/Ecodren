from django.db import models


class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre de la Categoría")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    categoria = models.ForeignKey(
        Categoria, 
        on_delete=models.PROTECT, 
        related_name='productos',
        verbose_name="Categoría"
    )
    codigo_sku = models.CharField(max_length=50, unique=True, verbose_name="Código / SKU")
    nombre = models.CharField(max_length=200, verbose_name="Nombre del Producto/Equipo")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción General")
    
    # Detalle técnico (ej. Presión máx, Caudal, Material, Diámetro)
    especificaciones = models.TextField(
        blank=True, 
        null=True, 
        help_text="Especificaciones técnicas (presión, caudal, dimensiones, etc.)"
    )
    
    precio_base = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0.00, 
        verbose_name="Precio Base (MXN)"
    )
    stock = models.PositiveIntegerField(default=0, verbose_name="Stock / Inventario")
    disponible = models.BooleanField(default=True, verbose_name="¿Disponible para venta/cotización?")
    
    # Archivos adjuntos opcionales (imágenes y ficha técnica)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True, verbose_name="Imagen Principal")
    ficha_tecnica = models.FileField(upload_to='fichas_tecnicas/', blank=True, null=True, verbose_name="Ficha Técnica (PDF)")

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Producto / Equipo'
        verbose_name_plural = 'Productos y Equipos'
        ordering = ['-creado_en']

    def __str__(self):
        return f"[{self.codigo_sku}] {self.nombre}"