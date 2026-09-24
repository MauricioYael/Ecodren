import json
import random
import re
import requests
from django.shortcuts import render
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from .models import (
    Producto, Categoria, Maquinaria, PublicacionRecurso, 
    DocumentoTecnico, CapacitacionImpartida, CursoDisponible,
    PerfilEmpresa, DireccionEntrega, Pedido, ItemPedido, 
    CotizacionGuardada, SolicitudCotizacion
)

def index(request):
    productos_destacados = Producto.objects.filter(disponible=True).order_by('?')[:4]
    return render(request, 'index.html', {
        'productos_destacados': productos_destacados,
        'conekta_public_key': getattr(settings, 'CONEKTA_PUBLIC_KEY', '')
    })

def tienda(request):
    categorias = Categoria.objects.all()
    productos = Producto.objects.filter(disponible=True)

    cat_param = request.GET.get('cat', '').strip()
    if cat_param and cat_param.lower() != 'todos':
        if cat_param.isdigit():
            productos = productos.filter(categoria_id=int(cat_param))
        else:
            productos = productos.filter(categoria__nombre__icontains=cat_param)

    busqueda = request.GET.get('q', '').strip()
    if busqueda:
        productos = productos.filter(
            Q(nombre__icontains=busqueda) |
            Q(codigo_sku__icontains=busqueda) |
            Q(descripcion__icontains=busqueda)
        )

    solo_stock = request.GET.get('stock')
    if solo_stock == '1':
        productos = productos.filter(stock__gt=0)

    etiqueta_param = request.GET.get('etiqueta', '').strip()
    if etiqueta_param:
        productos = productos.filter(etiqueta=etiqueta_param)

    precio_max = request.GET.get('precio_max', '').strip()
    if precio_max and precio_max.isdigit():
        productos = productos.filter(precio_base__lte=float(precio_max))

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
        'conekta_public_key': getattr(settings, 'CONEKTA_PUBLIC_KEY', '')
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
    perfil, _ = PerfilEmpresa.objects.get_or_create(user=request.user)
    direcciones = DireccionEntrega.objects.filter(usuario=request.user)
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
def actualizar_tema(request):
    try:
        data = json.loads(request.body)
        tema = data.get('tema', '').strip()

        if tema not in ('claro', 'oscuro'):
            return JsonResponse({'status': 'error', 'mensaje': 'Tema inválido'}, status=400)

        perfil, _ = PerfilEmpresa.objects.get_or_create(user=request.user)
        perfil.tema_preferido = tema
        perfil.save(update_fields=['tema_preferido'])

        return JsonResponse({'status': 'ok', 'tema': perfil.tema_preferido})
    except Exception as e:
        return JsonResponse({'status': 'error', 'mensaje': str(e)}, status=400)

def api_actualizar_localizacion(request):
    if request.method != 'POST' or not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'No autorizado'}, status=401)

    try:
        data = json.loads(request.body)
        perfil, _ = PerfilEmpresa.objects.get_or_create(user=request.user)

        if 'moneda' in data:
            perfil.moneda_defecto = data['moneda']
        if 'idioma' in data:
            perfil.idioma_panel = data['idioma']

        perfil.save()
        return JsonResponse({'status': 'ok', 'moneda': perfil.moneda_defecto, 'idioma': perfil.idioma_panel})
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Datos invalidos'}, status=400)

@login_required
@require_POST
def registrar_pedido_checkout(request):
    try:
        data = json.loads(request.body)
        items_data = data.get('items', [])
        metodo = data.get('metodo', 'tarjeta')
        token_id = data.get('token_id', '')

        if not items_data:
            return JsonResponse({'status': 'error', 'mensaje': 'El carrito está vacío'}, status=400)

        line_items_conekta = []
        total_centavos = 0
        items_a_crear = []

        for item in items_data:
            item_id = str(item.get('id', ''))
            cantidad = int(item.get('qty', item.get('cantidad', 1)))

            prod = Producto.objects.filter(id=item_id).first() if item_id.isdigit() else None
            curso = None
            if not prod:
                curso = CursoDisponible.objects.filter(id=item_id).first() if item_id.isdigit() else None

            precio_unitario = prod.precio_base if prod else (curso.precio if curso else float(item.get('precio', 0)))
            nombre = prod.nombre if prod else (curso.titulo if curso else item.get('nombre', 'Artículo'))
            
            unit_price_cents = int(float(precio_unitario) * 100)
            total_centavos += unit_price_cents * cantidad

            line_items_conekta.append({
                "name": str(nombre)[:245],
                "unit_price": unit_price_cents,
                "quantity": cantidad
            })

            items_a_crear.append({
                "producto": prod,
                "curso": curso,
                "nombre_item": nombre,
                "cantidad": cantidad,
                "precio_unitario": precio_unitario
            })

        total_pesos = total_centavos / 100.0
        codigo = f"#EC-2026-{random.randint(1000, 9999)}"

        telefono_raw = getattr(getattr(request.user, 'perfil_empresa', None), 'telefono_operativo', '') or '+525512345678'
        telefono_limpio = re.sub(r'[^\d+]', '', telefono_raw)
        if len(telefono_limpio) < 10:
            telefono_limpio = "+525512345678"

        order_payload = {
            "currency": "MXN",
            "customer_info": {
                "name": (request.user.get_full_name() or request.user.username)[:100],
                "email": request.user.email or "ventas@ecodren.com",
                "phone": telefono_limpio
            },
            "line_items": line_items_conekta
        }

        if metodo == 'tarjeta':
            order_payload["charges"] = [{
                "payment_method": {
                    "type": "card",
                    "token_id": token_id
                }
            }]
        elif metodo == 'spei':
            order_payload["charges"] = [{
                "payment_method": {
                    "type": "spei"
                }
            }]

        private_key = getattr(settings, 'CONEKTA_PRIVATE_KEY', '') or ''
        conekta_res = requests.post(
            'https://api.conekta.io/orders',
            auth=(private_key, ''),
            headers={
                'Accept': 'application/vnd.conekta-v2.0.0+json',
                'Content-Type': 'application/json'
            },
            json=order_payload,
            timeout=15
        )

        conekta_data = conekta_res.json()

        if conekta_res.status_code not in (200, 201):
            details = conekta_data.get('details', [])
            error_msg = details[0].get('message') if details else conekta_data.get('message', 'Error en pasarela de pagos')
            return JsonResponse({'status': 'error', 'mensaje': error_msg}, status=400)

        conekta_order_id = conekta_data.get('id', '')
        charges_data = conekta_data.get('charges', {}).get('data', [])
        charge = charges_data[0] if len(charges_data) > 0 else {}

        clabe_spei = ''
        if metodo == 'tarjeta':
            charge_status = charge.get('status', '')
            estado_pago = 'pagado' if charge_status == 'paid' else 'rechazado'
        else:
            estado_pago = 'pendiente'
            pm = charge.get('payment_method', {})
            clabe_spei = pm.get('clabe', '')

        resumen_txt = ", ".join([f"{i['nombre_item']} × {i['cantidad']}" for i in items_a_crear])[:245]
        
        pedido = Pedido.objects.create(
            usuario=request.user,
            codigo_pedido=codigo,
            equipo_insumo=resumen_txt,
            total=total_pesos,
            estatus='proceso',
            estado_pago=estado_pago,
            conekta_order_id=conekta_order_id,
            metodo_pago=metodo
        )

        for it in items_a_crear:
            ItemPedido.objects.create(
                pedido=pedido,
                producto=it['producto'],
                curso=it['curso'],
                nombre_item=it['nombre_item'],
                cantidad=it['cantidad'],
                precio_unitario=it['precio_unitario']
            )

        return JsonResponse({
            'status': 'ok',
            'codigo_pedido': pedido.codigo_pedido,
            'total': f"{total_pesos:,.2f}",
            'estado_pago': estado_pago,
            'clabe': clabe_spei
        })

    except requests.exceptions.RequestException as re_err:
        return JsonResponse({'status': 'error', 'mensaje': f"Error de conexión con Conekta: {str(re_err)}"}, status=502)
    except Exception as e:
        return JsonResponse({'status': 'error', 'mensaje': f"Error interno: {str(e)}"}, status=500)