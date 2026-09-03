from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# ==============================================================================
# 1. TIENDA Y REFACCIONES
# ==============================================================================

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre de la Categoría")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Categoría de Refacción'
        verbose_name_plural = 'Categorías de Refacciones'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    ETIQUETA_CHOICES = [
            ('', 'Sin etiqueta'),
            ('nuevo', 'Nuevo'),
            ('oferta', 'Oferta'),
            ('destacado', 'Destacado'),
        ]

    categoria = models.ForeignKey(
        Categoria, 
        on_delete=models.PROTECT, 
        related_name='productos',
        verbose_name="Categoría de Refacción"
    )
    codigo_sku = models.CharField(max_length=50, unique=True, verbose_name="Código / SKU")
    nombre = models.CharField(max_length=200, verbose_name="Nombre del Producto / Refacción")
    etiqueta = models.CharField(
        max_length=20,
        choices=ETIQUETA_CHOICES,
        default='',
        blank=True,
        verbose_name="Etiqueta visual"
    )
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción General")
    especificaciones = models.TextField(
        blank=True, 
        null=True, 
        help_text="Especificaciones técnicas (presión soportada, caudal GPM, diámetro, etc.)"
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
    
    ficha_tecnica = models.FileField(
        upload_to='fichas_tecnicas_refacciones/', 
        blank=True, 
        null=True, 
        verbose_name="Ficha Técnica de Refacción (PDF)"
    )

    maquinarias_compatibles = models.ManyToManyField(
        'Maquinaria', 
        blank=True, 
        related_name='refacciones_compatibles',
        verbose_name="Maquinaria(s) Compatible(s)"
    )

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Producto / Refacción'
        verbose_name_plural = 'Productos y Refacciones'
        ordering = ['-creado_en']

    def __str__(self):
        return f"[{self.codigo_sku}] {self.nombre}"


# ==============================================================================
# 2. MAQUINARIA PESADA Y CONFIGURADOR
# ==============================================================================

class Maquinaria(models.Model):
    LINEAS_MARCA = [
        ('ecojet', 'Ecojet — Equipos de Presión'),
        ('ecovac', 'Ecovac — Equipos de Vacío'),
        ('ecodren', 'Ecodren — Equipos Mixtos'),
        ('ecoclean', 'Ecoclean — Equipos de Vacío Seco'),
    ]

    slug = models.SlugField(unique=True, help_text="Identificador único para URL/JS, ej: 'ecodren-17'")
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre del Equipo")
    categoria_equipo = models.CharField(max_length=20, choices=LINEAS_MARCA, default='ecodren', verbose_name="Línea / Marca")
    tagline = models.TextField(help_text="Descripción corta del equipo")
    
    capacidad = models.CharField(max_length=50, help_text="Ej: 17 m³")
    presion = models.CharField(max_length=50, help_text="Ej: 3000 PSI")
    succion = models.CharField(max_length=50, default="Alto vacío", blank=True, null=True)
    peso = models.CharField(max_length=50, default="19,500 Kg", blank=True, null=True)
    tipo_trabajo = models.CharField(max_length=50, default="Industrial", blank=True, null=True)
    
    capacidad_m3 = models.DecimalField(max_digits=6, decimal_places=2, default=0.00, verbose_name="Capacidad numérica (m³)")
    presion_psi = models.PositiveIntegerField(default=0, verbose_name="Presión numérica (PSI)")

    recomendado = models.BooleanField(default=False, verbose_name="¿Equipo Destacado?")
    
    ficha_tecnica_pdf = models.FileField(
        upload_to='fichas_tecnicas_equipos/',
        blank=True,
        null=True,
        verbose_name="Ficha Técnica Oficial del Equipo (PDF)"
    )

    activo = models.BooleanField(default=True, verbose_name="¿Activo / Publicado?")
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Maquinaria'
        verbose_name_plural = 'Maquinarias'
        ordering = ['-recomendado', 'nombre']

    def __str__(self):
        return self.nombre


class ImagenMaquinaria(models.Model):
    maquinaria = models.ForeignKey(Maquinaria, related_name='imagenes', on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='maquinaria/')
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['orden']
        verbose_name = 'Imagen de Maquinaria'
        verbose_name_plural = 'Imágenes de Maquinaria'


class Equipamento(models.Model):
    maquinaria = models.ForeignKey(Maquinaria, on_delete=models.CASCADE, related_name='equipamentos')
    nombre = models.CharField(max_length=100)
    especificacion = models.CharField(max_length=255, help_text="Ej. Fibra de vidrio o Aluminio / 80 GPM / Hidráulico")
    icono = models.CharField(max_length=50, default="fa-screwdriver-wrench", help_text="Clase FontAwesome")

    class Meta:
        verbose_name = "Equipamiento"
        verbose_name_plural = "Equipamientos"

    def __str__(self):
        return f"{self.nombre} - {self.maquinaria.nombre}"


class AccesorioExtra(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    maquinarias = models.ManyToManyField(Maquinaria, related_name='accesorios_disponibles', blank=True)

    class Meta:
        verbose_name = "Accesorio Opcional"
        verbose_name_plural = "Accesorios Opcionales"

    def __str__(self):
        return self.nombre


class PuntoDestacado(models.Model):
    maquinaria = models.ForeignKey(Maquinaria, on_delete=models.CASCADE, related_name='puntos_destacados')
    titulo = models.CharField(max_length=100, help_text="Ej: Alto rendimiento")
    descripcion = models.CharField(max_length=255, help_text="Ej: Tecnología avanzada para máxima eficiencia.")
    icono = models.CharField(max_length=50, default="fa-shield-halved", help_text="Clase FontAwesome")
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Punto Destacado"
        verbose_name_plural = "Puntos Destacados"
        ordering = ['orden']

    def __str__(self):
        return f"{self.titulo} - {self.maquinaria.nombre}"


# ==============================================================================
# 3. RECURSOS Y COMUNIDAD
# ==============================================================================

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
    descripcion_corta = models.CharField(max_length=150, blank=True, null=True, verbose_name="Descripción corta")
    descripcion_larga = models.TextField(blank=True, null=True, verbose_name="Sinopsis / Descripción larga")
    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES, default='noticia', verbose_name="Tipo de contenido")
    
    etiqueta_badge = models.CharField(max_length=50, blank=True, null=True, help_text="Ej: 04:35 Min, 20 May 2026, Empresa")
    duracion_o_fecha = models.CharField(max_length=50, blank=True, null=True, help_text="Ej: 04:35 Min ó 15 de mayo, 2026")
    
    imagen_portada = models.ImageField(upload_to='recursos_portadas/', blank=True, null=True, verbose_name="Imagen de Portada")
    url_destino = models.URLField(blank=True, null=True, help_text="URL externa (YouTube, Facebook, etc.)")
    
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
        ('ficha', 'Ficha Técnica General'),
        ('manual', 'Manual de Operación'),
        ('catalogo', 'Catálogo de Producto'),
    ]

    titulo = models.CharField(max_length=200, verbose_name="Título del Documento")
    categoria = models.CharField(max_length=20, choices=CATEGORIAS_DOC, verbose_name="Categoría de Documento")
    descripcion = models.CharField(max_length=255, blank=True, null=True, verbose_name="Descripción corta")
    archivo_pdf = models.FileField(upload_to='documentos_tecnicos/', verbose_name="Archivo PDF Oficial")
    activo = models.BooleanField(default=True, verbose_name="¿Activo / Visible?")
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Documento Técnico / Guía"
        verbose_name_plural = "Documentos Técnicos y Guías"
        ordering = ['categoria', '-actualizado_en']

    def __str__(self):
        return f"[{self.get_categoria_display()}] {self.titulo}"


# ==============================================================================
# 4. CAPACITACIONES
# ==============================================================================

class CapacitacionImpartida(models.Model):
    titulo = models.CharField(max_length=200, verbose_name="Título del Curso Impartido")
    fecha = models.CharField(max_length=50, help_text="Ej: 12 May 2026", verbose_name="Fecha del Evento")
    ubicacion = models.CharField(max_length=100, help_text="Ej: Monterrey, NL", verbose_name="Ubicación / Ciudad")
    participantes = models.PositiveIntegerField(default=30, verbose_name="Número de Participantes")
    imagen = models.ImageField(upload_to='capacitaciones_exp/', blank=True, null=True, verbose_name="Foto del Evento")
    activo = models.BooleanField(default=True, verbose_name="¿Visible?")
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Capacitación Impartida (Experiencia)"
        verbose_name_plural = "Capacitaciones Impartidas"
        ordering = ['-creado_en']

    def __str__(self):
        return f"{self.titulo} - {self.ubicacion}"


class CursoDisponible(models.Model):
    titulo = models.CharField(max_length=200, verbose_name="Título del Curso")
    fecha_proxima = models.CharField(max_length=100, default="Próximamente", verbose_name="Fecha / Estado")
    duracion = models.CharField(max_length=50, default="5 Horas", verbose_name="Duración")
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=3800.00, verbose_name="Precio (MXN)")
    imagen = models.ImageField(upload_to='cursos_disponibles/', blank=True, null=True, verbose_name="Miniatura del Curso")
    cupos = models.PositiveIntegerField(default=15, verbose_name="Cupos Disponibles")
    activo = models.BooleanField(default=True, verbose_name="¿Disponible para inscripción?")
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Curso Disponible"
        verbose_name_plural = "Cursos Disponibles"
        ordering = ['-creado_en']

    def __str__(self):
        return self.titulo


# ==============================================================================
# 5. PERFIL Y OPERACIONES CORPORATIVAS
# ==============================================================================

class PerfilEmpresa(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_empresa')
    razon_social = models.CharField(max_length=200, blank=True, null=True, default="Servicios Hidráulicos del Centro S.A.", verbose_name="Razón Social")
    telefono_operativo = models.CharField(max_length=50, blank=True, null=True, default="+52 55 1234 5678", verbose_name="Teléfono Operativo")
    direccion_principal = models.CharField(
        max_length=300, 
        blank=True, 
        null=True, 
        default="Av. Central #123, Col. Industrial, C.P. 12345, Ciudad de México",
        verbose_name="Dirección de Entrega Principal"
    )
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Perfil de Empresa"
        verbose_name_plural = "Perfiles de Empresa"

    def __str__(self):
        return f"{self.user.username} - {self.razon_social}"


@receiver(post_save, sender=User)
def crear_o_guardar_perfil_empresa(sender, instance, created, **kwargs):
    if created:
        PerfilEmpresa.objects.create(user=instance)
    else:
        PerfilEmpresa.objects.get_or_create(user=instance)
        instance.perfil_empresa.save()


class DireccionEntrega(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='direcciones')
    nombre_sucursal = models.CharField(max_length=150, verbose_name="Nombre de la Ubicación / Sucursal")
    calle_numero = models.CharField(max_length=200, verbose_name="Calle y Número")
    colonia = models.CharField(max_length=150, verbose_name="Colonia")
    codigo_postal = models.CharField(max_length=10, verbose_name="Código Postal")
    ciudad_estado = models.CharField(max_length=150, verbose_name="Ciudad y Estado")
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Dirección de Entrega"
        verbose_name_plural = "Direcciones de Entrega"
        ordering = ['-creado_en']

    def __str__(self):
        return f"{self.nombre_sucursal} ({self.usuario.username})"


class Pedido(models.Model):
    ESTATUS_CHOICES = [
        ('aduana', 'En Aduana / Puerto'),
        ('proceso', 'En Preparación'),
        ('entregado', 'Liberado / Entregado'),
        ('cancelado', 'Cancelado'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pedidos')
    codigo_pedido = models.CharField(max_length=50, unique=True, verbose_name="ID Pedido")
    equipo_insumo = models.CharField(max_length=255, verbose_name="Equipo / Insumo Solicitado")
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
    numero_cotizacion = models.CharField(max_length=50, verbose_name="No. Cotización")
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


class SolicitudCotizacion(models.Model):
    CATEGORIA = [
        ('Maquinaria completa', 'Maquinaria completa'),
        ('Refacciones específicas', 'Refacciones específicas'),
        ('Servicio técnico', 'Servicio técnico'),
        ('Otro', 'Otro'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='solicitudes_cotizacion')
    nombre = models.CharField(max_length=150)
    empresa = models.CharField(max_length=150, blank=True, null=True)
    telefono = models.CharField(max_length=25, blank=True, null=True)
    email = models.EmailField()
    categoria = models.CharField(max_length=60, choices=CATEGORIA, blank=True, null=True)
    detalles = models.TextField(blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Solicitud de Cotización'
        verbose_name_plural = 'Solicitudes de Cotizaciones'
        ordering = ['-creado_en']

    def __str__(self):
        return f"Cotización #{self.id} - {self.nombre} ({self.email})"