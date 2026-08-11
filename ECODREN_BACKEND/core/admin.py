from django.contrib import admin
from .models import Categoria, Producto, Maquinaria, ImagenMaquinaria, Equipamento, AccesorioExtra


class ImagenMaquinariaInline(admin.TabularInline):
    model = ImagenMaquinaria
    extra = 1


class EquipamentoInline(admin.TabularInline):
    model = Equipamento
    extra = 1


@admin.register(Maquinaria)
class MaquinariaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria_equipo', 'capacidad', 'presion', 'activo')
    inlines = [ImagenMaquinariaInline, EquipamentoInline]


@admin.register(AccesorioExtra)
class AccesorioExtraAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo_sku', 'precio_base', 'disponible', 'stock')


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'creado_en')