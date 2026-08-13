from django.contrib import admin
from .models import Categoria, Producto, Maquinaria, ImagenMaquinaria, Equipamento, AccesorioExtra, PuntoDestacado

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
