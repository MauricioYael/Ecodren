from django.shortcuts import render
from django.db.models import Q
from .models import Producto, Categoria
from .models import Maquinaria
import json


def index(request):
    productos_destacados = Producto.objects.filter(disponible=True).order_by('?')[:4]
    return render(request, 'index.html', {
        'productos_destacados': productos_destacados
    })

def tienda(request):
    categorias = Categoria.objects.all()
    productos = Producto.objects.filter(disponible=True)

    # 1. Filtro por Categoría
    cat_id = request.GET.get('cat')
    if cat_id and cat_id != 'todos':
        productos = productos.filter(categoria_id=cat_id)

    # 2. Filtro de Búsqueda por Nombre o SKU
    busqueda = request.GET.get('q')
    if busqueda:
        productos = productos.filter(
            Q(nombre__icontains=busqueda) | 
            Q(codigo_sku__icontains=busqueda) | 
            Q(descripcion__icontains=busqueda)
        )

    # 3. Filtro Solo en Stock
    solo_stock = request.GET.get('stock')
    if solo_stock == '1':
        productos = productos.filter(stock__gt=0)

    # 4. Ordenamiento
    orden = request.GET.get('sort')
    if orden == 'price-asc':
        productos = productos.order_by('precio_base')
    elif orden == 'price-desc':
        productos = productos.order_by('-precio_base')
    elif orden == 'nombre':
        productos = productos.order_by('nombre')
    elif orden == 'nuevo':
        productos = productos.order_by('-creado_en')

    context = {
        'categorias': categorias,
        'productos': productos,
        'cat_seleccionada': cat_id,
        'busqueda': busqueda or '',
    }
    return render(request, 'tienda.html', context)

def maquinaria(request):
    maquinas_db = Maquinaria.objects.filter(activo=True).prefetch_related('imagenes')

    maquinaria_list = []
    for m in maquinas_db:
        imgs = [img.imagen.url for img in m.imagenes.all()]

        if not imgs:
            imgs = ['/static/Assets/logo_web_ecodren.png']

        maquinaria_list.append({
            'id': m.slug,
            'nombre': m.nombre,
            'categoria': m.categoria_equipo,
            'tagline': m.tagline,
            'capacidad': m.capacidad,
            'presion': m.presion,
            'recomendado': m.recomendado,
            'imagenes': imgs 
        })
    context = {
        'maquinaria_json': json.dumps(maquinaria_list)
    }
    return render(request, 'maquinaria.html', context)