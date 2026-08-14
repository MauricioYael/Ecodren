from django.contrib import admin
from .models import Categoria, Producto, Maquinaria, ImagenMaquinaria, Equipamento, AccesorioExtra, PuntoDestacado
from .models import PublicacionRecurso, DocumentoTecnico

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