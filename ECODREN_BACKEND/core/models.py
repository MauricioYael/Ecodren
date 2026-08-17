from django.db import models
from django.contrib.auth.models import User

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
    ficha_tecnica_pdf = models.FileField(
        upload_to='ficha_tecnica/',
        blank=True,
        null=True,
        verbose_name="Ficha Tecnica (PDF)"
    )

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

class PuntoDestacado(models.Model):
    maquinaria = models.ForeignKey(
        Maquinaria,
        on_delete=models.CASCADE,
        related_name='puntos_destacados'
    )
    titulo = models.CharField(max_length=100,help_text="Ej: Alto rendimiento")
    descripcion = models.CharField(max_length=255, help_text="Ej: Tecnologia avanzada para máxima eficiencia.")
    icono = models.CharField(
        max_length=50,
        default="fa-shield-halved",
        help_text="Clase FontAwesome, ej: fa-shield-halved, fa-droplet, fa-gear"
    )
    orden = models.PositiveBigIntegerField(default=0)

    class Meta:
        verbose_name = "Puntos Destacado"
        verbose_name_plural = "Puntos Destacados"
        ordering = ['orden']

    def __str__(self):
        return f"{self.titulo} - {self.maquinaria.nombre}"

class PublicacionRecurso(models.Model):
    TIPO_CHOICES = [
        ('video', 'Video'),
        ('noticia', 'Noticia / Artículo'),
        ('redes', 'Publicación de Comunidad'),
    ]

    RED_SOCIAL_CHOICES = [
        ('facebook', 'Facebook'),
        ('youtube', 'YouTube'),
        ('linkedin', 'LinkedIn'),
        ('instagram', 'Instagram'),
        ('ninguna', 'Ninguna / Web'),
    ]

    titulo = models.CharField(max_length=200, verbose_name="Título")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción corta")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='noticia', verbose_name="Tipo de contenido")
    
    etiqueta_badge = models.CharField(max_length=50, blank=True, null=True, help_text="Ej: 04:35 Min, 20 May 2024, Empresa, Destacado")
    duracion_o_fecha = models.CharField(max_length=50, blank=True, null=True, help_text="Ej: 04:35 Min ó 15 de mayo, 2024")
    
    imagen_portada = models.ImageField(upload_to='recursos_portadas/', blank=True, null=True, verbose_name="Imagen de Portada")
    url_destino = models.URLField(blank=True, null=True, help_text="URL externa (ej: YouTube, Facebook, LinkedIn)")
    
    red_social = models.CharField(max_length=20, choices=RED_SOCIAL_CHOICES, default='ninguna', verbose_name="Red Social")
    
    destacado = models.BooleanField(default=False, verbose_name="¿Es destacado / Card grande?")
    activo = models.BooleanField(default=True, verbose_name="¿Publicado?")
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Publicación / Recurso"
        verbose_name_plural = "Publicaciones y Recursos"
        ordering = ['-creado_en']

    def __str__(self):
        return f"[{self.get_tipo_display()}] {self.titulo}"

class DocumentoTecnico(models.Model):
    CATEGORIAS_DOC = [
        ('ficha', 'Ficha Técnica'),
        ('manual', 'Manual de Operación'),
        ('catalogo', 'Catálogo de Producto'),
    ]

    titulo = models.CharField(max_length=200, verbose_name="Título del Documento")
    categoria = models.CharField(max_length=20, choices=CATEGORIAS_DOC, verbose_name="Categoría de Documento")
    descripcion = models.CharField(max_length=255, blank=True, null=True, verbose_name="Descripción corta")
    
    # Campo para subir el archivo PDF
    archivo_pdf = models.FileField(upload_to='documentos_tecnicos/', verbose_name="Archivo PDF")
    
    activo = models.BooleanField(default=True, verbose_name="¿Activo / Visible?")
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Documento Técnico / Guía"
        verbose_name_plural = "Documentos Técnicos y Guías"
        ordering = ['categoria', '-actualizado_en']

    def __str__(self):
        return f"[{self.get_categoria_display()}] {self.titulo}"

class CapacitacionImpartida(models.Model):
    titulo = models.CharField(max_length=200, verbose_name="Titulo del curso impartido")
    fecha = models.CharField(max_length=50, help_text="Ej: 12 May 2024", verbose_name="Fecha del evento")
    ubicacion = models.CharField(max_length=100, help_text="Ej: Monterrey, N", verbose_name="Ubicacion / Ciudad")
    participantes = models.PositiveBigIntegerField(default=30, verbose_name="Numero de participantes")
    imagen = models.ImageField(upload_to='capacitaciones_exp/', blank=True, null=True, verbose_name="Foto del evento")
    activo = models.BooleanField(default=True, verbose_name="¿Visible?")
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Capacitación Impartida (Experiencia)"
        verbose_name_plural = "Capacitaciones Impartidas"
        ordering = ['-creado_en']

    def __str__(self):
        return f"{self.titulo}- {self.ubicacion}"

class CursoDisponible(models.Model):
    titulo = models.CharField(max_length=200, verbose_name="Titulo del curso")
    fecha_proxima = models.CharField(max_length=100, default="Proximamente", verbose_name="Fecha / Estado")
    duracion = models.CharField(max_length=50, default="5 Horas", verbose_name="Duracion")
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=3800.00, verbose_name="Precio (MXN)")
    imagen = models.ImageField(upload_to='cursos_disponibles/', blank=True, null=True, verbose_name="Miniatura del Curso")
    cupos = models.PositiveBigIntegerField(default=15, verbose_name="Cupos Disponibles")
    activo = models.BooleanField(default=True, verbose_name="¿Disponible para inscripcion?")
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Curso Disponible"
        verbose_name_plural = "Cursos Disponibles"
        ordering = ['-creado_en']

    def __str__(self):
        return self.titulo

class PerfilEmpresa(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    razon_social = models.CharField(max_length=200, default="Servicios Hidrahilicos del Centro", verbose_name="Razón Social")
    telefono = models.CharField(max_length=30, default="+52 55 XXXX XXXX", verbose_name="Telefono Operativo")
    direccion_principal = models.TextField(
        default="Av. Central #123, Col. Industrial, C.P. 12345, Ciudad de México",
        verbose_name="Dirección de Entrega Principal"
    )
    class Meta:
        verbose_name = "Perfil de Empresa"
        verbose_name_plural = "Perfiles de Empresa"

    def __str__(self):
        return f"{self.usuario.username} - {self.razon_social}"

class DireccionEntrega(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='direcciones')
    nombre_sucursal = models.CharField(max_length=150, verbose_name="Nombre de la Ubicacion / Sucursal")
    calle_numero = models.CharField(max_length=200, verbose_name="Calle y Numero")
    colonia = models.CharField(max_length=150, verbose_name="Colonia")
    codigo_postal = models.CharField(max_length=10, verbose_name="Codigo Postal")
    ciudad_estado = models.CharField(max_length=150, verbose_name="Ciudad y Estado")
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Dirección de Entrega"
        verbose_name_plural = "Direcciones de Entrega"
        ordering = ['-creado_en']

    def __srt__(self):
        return f"{self.nombre_sucursal ({self.usuario.username})}"

class Pedido (models.Model):
    ESTATUS_CHOICES = [
        ('aduana', 'En Aduana / Puerto'),
        ('proceso', 'En preparación'),
        ('entregado', 'Liberado / Entregado'),
        ('cancelado', 'Cancelado'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pedidos')
    codigo_pedido = models.CharField(max_length=50, unique=True, verbose_name="ID pedido (Ej: #EC-2026-9821)")
    equipo_insumo = models.CharField(max_length=255, verbose_name="Equipos / Insumo Solicitado")
    total = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Costo Total (MXN)")
    estatus = models.CharField(max_length=20, choices=ESTATUS_CHOICES, default='proceso', verbose_name="Estatus de Despacho")
    fecha_operacion = models.DateField(auto_now_add=True, verbose_name="Fecha de Operación")

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Historial de Pedidos"
        ordering = ['-fecha_operacion']
        
    def __str__(self):
        return f"{self.codigo_pedido} - {self.usuario.username}"

class CotizacionGuardada(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cotizaciones')
    numero_cotizacion = models.CharField(max_length=50, verbose_name="No. Cotización (Ej: COT-2026-042)")
    equipo_solicitado = models.CharField(max_length=255, verbose_name="Equipo Solicitado")
    vigencia = models.CharField(max_length=100, default="30 Jul 2026", verbose_name="Vigencia")
    asesor_asignado = models.CharField(max_length=150, default="Ing. Roberto Martínez", verbose_name="Asesor Técnico Asignado")
    tipo_operacion = models.CharField(max_length=150, default="Soporte Comercial Directo", verbose_name="Tipo de Operación")
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Cotización Guardada"
        verbose_name_plural = "Cotizaciones Guardadas"
        ordering = ['-creado_en']

    def __str__(self):
        return f"{self.numero_cotizacion} - {self.usuario.username}"  

    