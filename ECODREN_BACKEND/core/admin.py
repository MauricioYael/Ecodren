from django.contrib import admin
from .models import Categoria, Producto
from .models import Maquinaria, ImagenMaquinaria


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'creado_en')
    search_fields = ('nombre',)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('codigo_sku', 'nombre', 'categoria', 'precio_base', 'stock', 'disponible')
    list_filter = ('categoria', 'disponible')
    search_fields = ('codigo_sku', 'nombre', 'descripcion')
    list_editable = ('precio_base', 'stock', 'disponible')

class ImagenMaquinariaInLine(admin.TabularInline):
    model = ImagenMaquinaria
    extra = 3
@admin.register(Maquinaria)
class MaquinariaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug', 'categoria_equipo', 'capacidad', 'presion', 'recomendado', 'activo')
    list_filter = ('categoria_equipo', 'recomendado', 'activo')
    prepopulated_fields = {'slug': ('nombre', )}
    inlines = [ImagenMaquinariaInLine]