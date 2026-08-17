from django.contrib import admin
from .models import Categoria, Producto, Maquinaria, ImagenMaquinaria, Equipamento, AccesorioExtra, PuntoDestacado
from .models import PublicacionRecurso, DocumentoTecnico
from .models import CapacitacionImpartida, CursoDisponible
from .models import PerfilEmpresa, DireccionEntrega, Pedido, CotizacionGuardada


class ImagenMaquinariaInline(admin.TabularInline):
    model = ImagenMaquinaria
    extra = 1


class EquipamentoInline(admin.TabularInline):
    model = Equipamento
    extra = 1

class PuntoDestacadoInLine(admin.TabularInline):
    model = PuntoDestacado
    extra = 3 

@admin.register(Maquinaria)
class MaquinariaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria_equipo', 'capacidad', 'presion', 'activo')
    inlines = [ImagenMaquinariaInline, EquipamentoInline, PuntoDestacadoInLine]


@admin.register(AccesorioExtra)
class AccesorioExtraAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo_sku', 'precio_base', 'disponible', 'stock')


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'creado_en')

@admin.register(PublicacionRecurso)
class PublicacionRecursoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo', 'red_social', 'destacado', 'activo', 'creado_en')
    list_filter = ('tipo', 'red_social', 'destacado', 'activo')
    search_fields = ('titulo', 'descripcion')

@admin.register(DocumentoTecnico)
class DocumentoTecnicoAdmin(admin.ModelAdmin):
    list_display =('titulo', 'categoria', 'activo', 'actualizado_en')
    list_filter = ('categoria', 'activo')
    search_fields = ('titulo', 'descripcion')

@admin.register(CapacitacionImpartida)
class CapacitacionImpartidaAdmin(admin.ModelAdmin):
    list_display=('titulo', 'ubicacion', 'fecha', 'participantes', 'activo')
    list_filter=('ubicacion', 'activo')
    search_fields=('titulo', 'ubicacion')

@admin.register(CursoDisponible)
class CursoDisponibleAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'fecha_proxima', 'duracion', 'precio', 'activo')
    list_filter = ('activo',)
    search_fields = ('titulo',) 

@admin.register(PerfilEmpresa)
class PerfilEmpresaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'razon_social', 'telefono')
    search_fields= ('usuario__username', 'razon_social')

@admin.register(DireccionEntrega)
class DireccionEntregaAdmin(admin.ModelAdmin):
    list_display = ('nombre_sucursal', 'usuario', 'ciudad_estado', 'creado_en')
    list_filter = ('ciudad_estado',)
    search_fields= ('nombre_sucursal', 'usuario_username', 'calle_numero')

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('codigo_pedido', 'usuario', 'equipo_insumo', 'total', 'estatus', 'fecha_operacion')
    list_filter = ('estatus', 'fecha_operacion')
    search_fields = ('codigo_pedido', 'usuario__username', 'equipo_insumo')

@admin.register(CotizacionGuardada)
class CotizacionGuardadaAdmin(admin.ModelAdmin):
    list_display=('numero_cotizacion', 'usuario', 'equipo_solicitado', 'vigencia')
    search_fields = ('numero_cotizacion', 'usuario__username', 'equipo_solicitado')