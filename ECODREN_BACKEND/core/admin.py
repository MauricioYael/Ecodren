from django.contrib import admin
from .models import (
    Categoria, Producto, Maquinaria, ImagenMaquinaria, 
    Equipamento, AccesorioExtra, PuntoDestacado, PublicacionRecurso,
    DocumentoTecnico, CapacitacionImpartida, CursoDisponible,
    PerfilEmpresa, DireccionEntrega, Pedido, CotizacionGuardada
)

# ── INLINES DE MAQUINARIA ───────────────────────────────────────────

class ImagenMaquinariaInline(admin.TabularInline):
    model = ImagenMaquinaria
    extra = 1


class EquipamentoInline(admin.TabularInline):
    model = Equipamento
    extra = 1


class PuntoDestacadoInLine(admin.TabularInline):
    model = PuntoDestacado
    extra = 3


# ── ADMINISTRACIÓN DE CATÁLOGO Y OPERACIONES ────────────────────────

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    # 'nombre' o 'codigo_sku' como link principal; los editables permiten cambios directos en tabla
    list_display = ('codigo_sku', 'nombre', 'categoria', 'precio_base', 'stock', 'disponible', 'actualizado_en')
    list_display_links = ('codigo_sku', 'nombre')
    list_editable = ('precio_base', 'stock', 'disponible')
    list_filter = ('disponible', 'categoria', 'maquinarias_compatibles')
    search_fields = ('nombre', 'codigo_sku', 'descripcion')
    filter_horizontal = ('maquinarias_compatibles',)
    list_per_page = 25


@admin.register(Maquinaria)
class MaquinariaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria_equipo', 'capacidad', 'presion', 'activo', 'recomendado')
    list_editable = ('activo', 'recomendado')
    list_filter = ('categoria_equipo', 'activo', 'recomendado')
    search_fields = ('nombre', 'tagline')
    prepopulated_fields = {'slug': ('nombre',)}
    inlines = [ImagenMaquinariaInline, EquipamentoInline, PuntoDestacadoInLine]


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'creado_en')
    search_fields = ('nombre',)


@admin.register(AccesorioExtra)
class AccesorioExtraAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    filter_horizontal = ('maquinarias',)


@admin.register(PublicacionRecurso)
class PublicacionRecursoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo', 'red_social', 'destacado', 'activo', 'creado_en')
    list_editable = ('destacado', 'activo')
    list_filter = ('tipo', 'red_social', 'destacado', 'activo')
    search_fields = ('titulo', 'descripcion')


@admin.register(DocumentoTecnico)
class DocumentoTecnicoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'categoria', 'activo', 'actualizado_en')
    list_editable = ('activo',)
    list_filter = ('categoria', 'activo')
    search_fields = ('titulo', 'descripcion')


@admin.register(CapacitacionImpartida)
class CapacitacionImpartidaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'ubicacion', 'fecha', 'participantes', 'activo')
    list_editable = ('activo',)
    list_filter = ('ubicacion', 'activo')
    search_fields = ('titulo', 'ubicacion')


@admin.register(CursoDisponible)
class CursoDisponibleAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'fecha_proxima', 'duracion', 'precio', 'cupos', 'activo')
    list_editable = ('precio', 'cupos', 'activo')
    list_filter = ('activo',)
    search_fields = ['titulo']


@admin.register(PerfilEmpresa)
class PerfilEmpresaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'razon_social', 'telefono')
    search_fields = ('usuario__username', 'usuario__email', 'razon_social')


@admin.register(DireccionEntrega)
class DireccionEntregaAdmin(admin.ModelAdmin):
    list_display = ('nombre_sucursal', 'usuario', 'ciudad_estado', 'creado_en')
    list_filter = ('ciudad_estado',)
    search_fields = ('nombre_sucursal', 'usuario__username')


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('codigo_pedido', 'usuario', 'equipo_insumo', 'total', 'estatus', 'fecha_operacion')
    list_editable = ('estatus',)
    list_filter = ('estatus', 'fecha_operacion')
    search_fields = ('codigo_pedido', 'usuario__username', 'usuario__email')


@admin.register(CotizacionGuardada)
class CotizacionGuardadaAdmin(admin.ModelAdmin):
    list_display = ('numero_cotizacion', 'usuario', 'equipo_solicitado', 'vigencia')
    search_fields = ('numero_cotizacion', 'usuario__username')