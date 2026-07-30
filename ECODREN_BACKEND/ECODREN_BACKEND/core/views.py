from django.shortcuts import render
from django.db.models import Q
from .models import Categoria, Producto

def index(request):
    return render(request, 'index.html')

def tienda(request):
    categorias = Categoria.objects.all()
    productos = Producto.objects.filter(disponible=True)

    cat_id = request.GET.get('cat')
    if cat_id and cat_id != 'todos':
        productos = productos.filter(categoria_id=cat_id)

    search_query = request.GET.get('q')
    if search_query:
        productos = productos.filter(
            Q(nombre__icontains=search_query) |
            Q(codigo_sku__icontains=search_query) |
            Q(descripcion_icontains=search_query)
        )

    only_stock = request.GET.get('stock')
    if only_stock == 'true':
        productos = productos.filter(stock__gt=0)

    sort = request.GET.get('sort')
    if sort == 'price_asc':
        productos = productos.order_by('precio_base')
    elif sort == 'price-desc':
        productos = productos.order_by('-precio_base')
    elif sort == 'nombre':
        productos = productos.order_by('nombre')
    elif sort == 'nuevo':
        productos = productos.order_by('-creado_en')

    context = {
        'categorias': categorias,
        'productos': productos,
        'cat_seleccionada': str(cat_id) if cat_id else 'todos',
        'search_query': search_query or '',
        'only_stock': only_stock == 'true',
        'sort_actual': sort or 'default',
    }
    return render(request, 'tienda.html', context)
