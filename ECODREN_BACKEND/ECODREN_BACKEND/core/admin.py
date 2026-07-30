from django.contrib import admin
from .models import Categoria, Producto


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