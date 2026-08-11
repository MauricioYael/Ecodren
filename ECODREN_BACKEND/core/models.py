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


class Maquinaria(models.Model):
    CATEGORIAS_EQUIPO = [
        ('ecojet', 'Ecojet'),
        ('ecovac', 'Ecovac'),
        ('ecodren', 'Ecodren'),
        ('ecoclean', 'Ecoclean'),
    ]
    slug = models.SlugField(unique=True, help_text="Identificador unico para JS, ej: 'Ecodren-17'")
    nombre = models.CharField(max_length=100)
    categoria_equipo = models.CharField(max_length=20, choices=CATEGORIAS_EQUIPO, default='ecodren')
    tagline = models.TextField(help_text="Descripcion corta del equipo")
    capacidad = models.CharField(max_length=50)
    presion = models.CharField(max_length=50)
    succion = models.CharField(max_length=50, default="Alto vacío", blank=True, null=True)
    peso = models.CharField(max_length=50, default="19,500 Kg", blank=True, null=True)
    tipo_trabajo = models.CharField(max_length=50, default="Industrial", blank=True, null=True)
    recomendado = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Maquinaria'
        verbose_name_plural = 'Maquinarias'
        ordering = ['-recomendado', 'nombre']

    def __str__(self):
        return self.nombre


class ImagenMaquinaria(models.Model):
    maquinaria = models.ForeignKey(
        Maquinaria, related_name='imagenes',
        on_delete=models.CASCADE
    )
    imagen = models.ImageField(upload_to='maquinaria/')
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['orden']
        verbose_name = 'Imagen de Maquinaria'
        verbose_name_plural = 'Imágenes de Maquinaria'


class Equipamento(models.Model):
    maquinaria = models.ForeignKey(Maquinaria, on_delete=models.CASCADE, related_name='equipamentos')
    nombre = models.CharField(max_length=100)
    especificacion = models.CharField(max_length=255, help_text="Ej. Fibra de vidrio o Aluminio / 80 GPM / Hidrahulico")
    icono = models.CharField(max_length=50, default="fa-screwdriver-wrench", help_text="Clase FontAwesome, ej: fa-water")

    class Meta:
        verbose_name = "Equipamento"
        verbose_name_plural = "Equipamentos"

    def __str__(self):
        return f"{self.nombre} - {self.maquinaria.nombre}"


class AccesorioExtra(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    maquinarias = models.ManyToManyField(Maquinaria, related_name='accesorios_disponibles', blank=True)

    class Meta:
        verbose_name = "Accesorio Extra"
        verbose_name_plural = "Accesorios Extras"

    def __str__(self):
        return self.nombre