import json
import random
from django.shortcuts import render
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import (
    Producto, Categoria, Maquinaria, PublicacionRecurso, 
    DocumentoTecnico, CapacitacionImpartida, CursoDisponible,
    PerfilEmpresa, DireccionEntrega, Pedido, CotizacionGuardada,
    SolicitudCotizacion
)
from django.http import JsonResponse
from django.views.decorators.http import require_POST    
from django.core.mail import send_mail
from django.conf import settings


def index(request):
    productos_destacados = Producto.objects.filter(disponible=True).order_by('?')[:4]
    return render(request, 'index.html', {
        'productos_destacados': productos_destacados
    })

def tienda(request):
    categorias = Categoria.objects.all()
    productos = Producto.objects.filter(disponible=True)

    # 1. Filtro por Categoría
    cat_param = request.GET.get('cat', '').strip()
    if cat_param and cat_param.lower() != 'todos':
        if cat_param.isdigit():
            productos = productos.filter(categoria_id=int(cat_param))
        else:
            productos = productos.filter(categoria__nombre__icontains=cat_param)

    # 2. Búsqueda por texto
    busqueda = request.GET.get('q', '').strip()
    if busqueda:
        productos = productos.filter(
            Q(nombre__icontains=busqueda) |
            Q(codigo_sku__icontains=busqueda) |
            Q(descripcion__icontains=busqueda)
        )

    # 3. Filtro por Stock
    solo_stock = request.GET.get('stock')
    if solo_stock == '1':
        productos = productos.filter(stock__gt=0)

    # 4. Filtro por Etiquetas / Ofertas (NUEVO)
    etiqueta_param = request.GET.get('etiqueta', '').strip()
    if etiqueta_param:
        productos = productos.filter(etiqueta=etiqueta_param)

    # 5. Filtro por Precio Máximo
    precio_max = request.GET.get('precio_max', '').strip()
    if precio_max and precio_max.isdigit():
        productos = productos.filter(precio_base__lte=float(precio_max))

    # 6. Ordenamiento
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
        'cat_seleccionada': cat_param,
        'etiqueta_seleccionada': etiqueta_param,
        'busqueda': busqueda,
        'precio_max': precio_max or '10000',
    }
    return render(request, 'tienda.html', context)

def maquinaria(request):
    maquinas_qs = Maquinaria.objects.filter(activo=True).prefetch_related(
        'imagenes', 'equipamentos', 'accesorios_disponibles', 'puntos_destacados'
    )
    maquinaria_data = []
    for m in maquinas_qs:
        maquinaria_data.append({
            'id': m.id,
            'slug': m.slug or str(m.id),
            'nombre': m.nombre,
            'categoria': m.categoria_equipo,
            'tagline': m.tagline or '',
            'capacidad': m.capacidad or '',
            'presion': m.presion or '',
            'succion': m.succion or 'Alto Vacío',
            'peso': m.peso or '19,500 Kg',
            'tipo_trabajo': m.tipo_trabajo or 'Industrial',
            'recomendado': m.recomendado,
            'imagenes': [img.imagen.url for img in m.imagenes.all() if img.imagen] or ['/static/Assets/logo-ecodren.png'],
            'equipamento': [
                {'nombre': eq.nombre, 'especificacion': eq.especificacion, 'icono': eq.icono}
                for eq in m.equipamentos.all()
            ],
            'accesorios': [
                {'nombre': acc.nombre, 'descripcion': acc.descripcion or ''}
                for acc in m.accesorios_disponibles.all()
            ],
            'puntos_destacados': [
                {'titulo': p.titulo, 'descripcion': p.descripcion, 'icono': p.icono}
                for p in m.puntos_destacados.all()
            ],
            'pdf_url': m.ficha_tecnica_pdf.url if m.ficha_tecnica_pdf else ''
        })

    context = {
        'maquinas': maquinas_qs,
        'maquinaria_data': maquinaria_data
    }
    return render(request, 'maquinaria.html', context)


def recursos(request):
    videos = PublicacionRecurso.objects.filter(activo=True, tipo='video')
    noticias = PublicacionRecurso.objects.filter(activo=True, tipo='noticia')
    comunidad_bento = PublicacionRecurso.objects.filter(activo=True, tipo='redes')

    doc_ficha = DocumentoTecnico.objects.filter(activo=True, categoria='ficha').first()
    doc_manual = DocumentoTecnico.objects.filter(activo=True, categoria='manual').first()
    doc_catalogo = DocumentoTecnico.objects.filter(activo=True, categoria='catalogo').first()

    context = {
        'videos': videos,
        'noticias': noticias,
        'comunidad_bento': comunidad_bento,
        'doc_ficha': doc_ficha,
        'doc_manual': doc_manual,
        'doc_catalogo': doc_catalogo,
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


def capacitaciones(request):
    experiencias = CapacitacionImpartida.objects.filter(activo=True)
    cursos_disponibles = CursoDisponible.objects.filter(activo=True)

    context = {
        'experiencias': experiencias,
        'cursos_disponibles': cursos_disponibles,
    }
    return render(request, 'capacitaciones.html', context)


@login_required
def perfil_view(request):
    # 🟢 Se usa 'user' para coincidir con la definición de PerfilEmpresa en models.py
    perfil, _ = PerfilEmpresa.objects.get_or_create(user=request.user)
    direcciones = DireccionEntrega.objects.filter(usuario=request.user)
    
    # 🟢 Pedidos ordenados cronológicamente (más recientes primero)
    pedidos = Pedido.objects.filter(usuario=request.user).order_by('-fecha_operacion')
    cotizaciones = SolicitudCotizacion.objects.filter(usuario=request.user).order_by('-creado_en')

    context = {
        'perfil': perfil,
        'direcciones': direcciones,
        'pedidos': pedidos,
        'cotizaciones': cotizaciones,
    }
    return render(request, 'perfil.html', context)


@require_POST
def enviar_cotizacion(request):
    nombre = request.POST.get('nombre', '').strip()
    empresa = request.POST.get('empresa', '').strip()
    telefono = request.POST.get('telefono', '').strip()
    email = request.POST.get('email', '').strip()
    categoria = request.POST.get('categoria', '').strip()
    detalles = request.POST.get('detalles', '').strip()

    if not nombre or not email:
        return JsonResponse({'status': 'error', 'mensaje': 'El nombre y correo electrónico son requeridos'})

    usuario_activo = request.user if request.user.is_authenticated else None
    cotizacion = SolicitudCotizacion.objects.create(
        usuario=usuario_activo,
        nombre=nombre,
        empresa=empresa,
        telefono=telefono,
        email=email,
        categoria=categoria,
        detalles=detalles
    )

    asunto_cliente = "Hemos recibido tu solicitud de cotización | ECODREN"
    mensaje_cliente = (
        f"Hola {nombre},\n\n"
        f"Hemos recibido con éxito tu solicitud de cotización (Folio: #COT-{cotizacion.id:04d}).\n\n"
        f"Resumen de tu solicitud:\n"
        f"• Categoría: {categoria or 'General'}\n"
        f"• Empresa: {empresa or 'Particular'}\n"
        f"• Teléfono de contacto: {telefono or 'No proporcionado'}\n"
        f"• Requerimiento: {detalles or 'Sin detalles adicionales'}\n\n"
        f"Uno de nuestros asesores comerciales y técnicos de Equipos MC se comunicará contigo en breve.\n\n"
        f"Atentamente,\n"
        f"Equipo ECODREN México"
    )

    try: 
        send_mail(
            asunto_cliente,
            mensaje_cliente,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Error al enviar correo: {e}")

    return JsonResponse({
        'status': 'ok',
        'mensaje': '¡Cotización enviada con éxito! Te hemos enviado un correo con los detalles.'
    })


@login_required
@require_POST
def actualizar_datos_perfil(request):
    try: 
        data = json.loads(request.body)
        user = request.user

        nombre_completo = data.get('nombre', '').strip()
        if nombre_completo:
            partes = nombre_completo.split(' ', 1)
            user.first_name = partes[0]
            user.last_name = partes[1] if len(partes) > 1 else ''

        email = data.get('email', '').strip()
        if email:
            user.email = email
        user.save()

        perfil, _ = PerfilEmpresa.objects.get_or_create(user=user)
        perfil.razon_social = data.get('razon', '').strip()
        perfil.telefono_operativo = data.get('telefono', '').strip()
        perfil.direccion_principal = data.get('direccion', '').strip()
        perfil.save()

        return JsonResponse({
            'status': 'ok',
            'mensaje': 'Datos guardados correctamente en la base de datos.',
            'nombre': user.get_full_name() or user.username,
            'email': user.email
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'mensaje': str(e)}, status=400)


@login_required
@require_POST
def registrar_pedido_checkout(request):
    try:
        data = json.loads(request.body)
        items = data.get('items', [])
        total = float(data.get('total', 0))

        if not items:
            return JsonResponse({'status': 'error', 'mensaje': 'El carrito está vacío'}, status=400)

        # Folio único de pedido
        codigo = f"#EC-2026-{random.randint(1000, 9999)}"

        # Resumen de artículos adquiridos
        resumen_productos = ", ".join([
            f"{item.get('nombre', 'Producto')} × {item.get('qty', item.get('cantidad', 1))}" 
            for item in items
        ])
        if len(resumen_productos) > 250:
            resumen_productos = resumen_productos[:247] + "..."

        pedido = Pedido.objects.create(
            usuario=request.user,
            codigo_pedido=codigo,
            equipo_insumo=resumen_productos,
            total=total,
            estatus='proceso'
        )

        return JsonResponse({
            'status': 'ok',
            'mensaje': 'Pedido registrado con éxito.',
            'codigo_pedido': pedido.codigo_pedido
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'mensaje': str(e)}, status=400)