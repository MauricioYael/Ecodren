import json
from django.shortcuts import render
from django.db.models import Q
from .models import Producto, Categoria, Maquinaria, PublicacionRecurso


def index(request):
    productos_destacados = Producto.objects.filter(disponible=True).order_by('?')[:4]
    return render(request, 'index.html', {
        'productos_destacados': productos_destacados
    })


def tienda(request):
    categorias = Categoria.objects.all()
    productos = Producto.objects.filter(disponible=True)

    cat_id = request.GET.get('cat')
    if cat_id and cat_id != 'todos':
        productos = productos.filter(categoria_id=cat_id)

    busqueda = request.GET.get('q')
    if busqueda:
        productos = productos.filter(
            Q(nombre__icontains=busqueda) | 
            Q(codigo_sku__icontains=busqueda) | 
            Q(descripcion__icontains=busqueda)
        )

    solo_stock = request.GET.get('stock')
    if solo_stock == '1':
        productos = productos.filter(stock__gt=0)

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
    maquinas_db = Maquinaria.objects.filter(activo=True).prefetch_related('imagenes', 'equipamentos', 'accesorios_disponibles')
    maquinaria_list = []
    
    for m in maquinas_db:
        imgs = []
        for img in m.imagenes.all():
            try:
                if img.imagen and hasattr(img.imagen, 'url'):
                    imgs.append(img.imagen.url)
            except ValueError:
                continue

        if not imgs:
            imgs = ['/static/Assets/logo-ecodren.png']

        equipamentos = []
        if hasattr(m, 'equipamentos'):
            equipamentos = [
                {
                    'id': eq.id,
                    'nombre': eq.nombre,
                    'especificacion': eq.especificacion,
                    'icono': eq.icono
                } for eq in m.equipamentos.all()
            ]

        accesorios = []
        if hasattr(m, 'accesorios_disponibles'):
            accesorios = [
                {
                    'id': acc.id,
                    'nombre': acc.nombre,
                    'descripcion': acc.descripcion or ''
                } for acc in m.accesorios_disponibles.all()
            ]
        puntos = []
        if hasattr(m, 'puntos_destacados'):
            puntos = [
                {
                    'titulo': p.titulo,
                    'descripcion': p.descripcion,
                    'icono': p.icono
                } for p in m.puntos_destacados.all()
            ]

        maquinaria_list.append({
            'id': m.id,
            'slug': getattr(m, 'slug', str(m.id)),
            'nombre': m.nombre,
            'categoria': getattr(m, 'categoria_equipo', 'ecodren'),
            'tagline': m.tagline or '',
            'capacidad': m.capacidad or '',
            'presion': m.presion or '',
            'succion': getattr(m, 'succion', 'Alto vacío') or 'Alto vacío',
            'peso': getattr(m, 'peso', '19,500 Kg') or '19,500 Kg',
            'tipo_trabajo': getattr(m, 'tipo_trabajo', 'Industrial') or 'Industrial',
            'recomendado': m.recomendado,
            'imagenes': imgs,
            'equipamento': equipamentos,
            'accesorios': accesorios,
            'puntos_destacados': puntos,
            'pdf_url': m.ficha_tecnica_pdf.url if m.ficha_tecnica_pdf else ''
        })

    context = {
        'maquinaria_json': json.dumps(maquinaria_list)
    }
    return render(request, 'maquinaria.html', context)

def recursos(request):
    videos = PublicacionRecurso.objects.filter(activo=True, tipo='video')
    noticias = PublicacionRecurso.objects.filter(activo=True, tipo='noticia')
    comunidad_bento = PublicacionRecurso.objects.filter(activo=True, tipo='redes')

    context = {
        'videos': videos,
        'noticias': noticias,
        'comunidad_bento': comunidad_bento,
    }
    return render(request, 'recursos.html', context)

def publicaciones(request):
    cat = request.GET.get('cat', 'todos')
    publicaciones_qs = PublicacionRecurso.objects.filter(activo=True)

    if cat and cat != 'todos':
        publicaciones_qs = publicaciones_qs.filter(tipo=cat)

    context = {
        'publicaciones': publicaciones_qs,
        'cat_actual': cat,
    }
    return render(request, 'publicaciones.html', context)