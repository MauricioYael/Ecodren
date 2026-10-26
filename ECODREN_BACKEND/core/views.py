import json
import re
import uuid
import logging
import requests

from django.shortcuts import render
from django.db import transaction
from django.db.models import Q
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email
from django.contrib.auth.models import User

from .models import (
    Producto, Categoria, Maquinaria, PublicacionRecurso, 
    DocumentoTecnico, CapacitacionImpartida, CursoDisponible,
    PerfilEmpresa, DireccionEntrega, Pedido, ItemPedido, 
    CotizacionGuardada, SolicitudCotizacion, ChasisOption
)

logger = logging.getLogger(__name__)


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
    
    chasis_globales = [
        {
            'id': c.id,
            'nombre': c.nombre,
            'marca': c.get_marca_display(),
            'tipo_cabina': "Cabina Convencional" if c.tipo_cabina == 'convencional' else "Cab Over",
            'libras': c.libra_minimas
        }
        for c in ChasisOption.objects.filter(activo=True)
    ]

    maquinaria_data = []
    for m in maquinas_qs:
        maquinaria_data.append({
            'id': m.id,
            'slug': m.slug or str(m.id),
            'nombre': m.nombre,
            'categoria': m.categoria_equipo,
            'tagline': m.tagline or '',
            'capacidad': m.capacidad or '',
            'capacidad_m3': float(m.capacidad_m3) if m.capacidad_m3 else 0,
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
                {'id': acc.id, 'nombre': acc.nombre, 'descripcion': acc.descripcion or ''}
                for acc in m.accesorios_disponibles.all()
            ],
            'chasis': chasis_globales,
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

    fichas = DocumentoTecnico.objects.filter(activo=True, categoria='ficha').first()
    manuales = DocumentoTecnico.objects.filter(activo=True, categoria='manual').first()
    catalogos = DocumentoTecnico.objects.filter(activo=True, categoria='catalogo').first()

    context = {
        'videos': videos,
        'noticias': noticias,
        'comunidad_bento': comunidad_bento,
        'doc_ficha': fichas,
        'doc_manual': manuales,
        'doc_catalogo': catalogos,
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

    metodos_pago = []
    if perfil.conekta_customer_id:
        private_key = getattr(settings, 'CONEKTA_PRIVATE_KEY', '') or ''
        try:
            res = requests.get(
                f'https://api.conekta.io/customers/{perfil.conekta_customer_id}/payment_sources',
                auth=(private_key, ''),
                headers={'Accept': 'application/vnd.conekta-v2.0.0+json'},
                timeout=5
            )
            if res.status_code == 200:
                metodos_pago = res.json().get('data', [])
        except Exception:
            metodos_pago = []
    
    context = {
        'perfil': perfil,
        'direcciones': direcciones,
        'pedidos': pedidos,
        'cotizaciones': cotizaciones,
        'metodos_pago': metodos_pago,
        'conekta_public_key': getattr(settings, 'CONEKTA_PUBLIC_KEY', ''),
        'has_usable_password': request.user.has_usable_password()
    }
    return render(request, 'perfil.html', context)


@login_required
@require_POST
def cambiar_password(request):
    try:
        data = json.loads(request.body)
        password_actual = data.get('password_actual', '')
        password_nueva = data.get('password_nueva', '')
        password_confirmar = data.get('password_confirmar', '')

        user = request.user
        tiene_password = user.has_usable_password()

        if tiene_password:
            if not password_actual:
                return JsonResponse({'status': 'error', 'mensaje': 'Por favor ingresa tu contraseña actual.'}, status=400)
            if not user.check_password(password_actual):
                return JsonResponse({'status': 'error', 'mensaje': 'La contraseña actual es incorrecta.'}, status=400)

        if not password_nueva or not password_confirmar:
            return JsonResponse({'status': 'error', 'mensaje': 'Por favor completa todos los campos de la nueva contraseña.'}, status=400)

        if password_nueva != password_confirmar:
            return JsonResponse({'status': 'error', 'mensaje': 'La nueva contraseña y su confirmación no coinciden.'}, status=400)

        try:
            validate_password(password_nueva, user=user)
        except ValidationError as ve:
            return JsonResponse({'status': 'error', 'mensaje': ' '.join(ve.messages)}, status=400)

        user.set_password(password_nueva)
        user.save()

        update_session_auth_hash(request, user)

        msg = 'Contraseña asignada exitosamente.' if not tiene_password else 'Contraseña actualizada correctamente.'
        return JsonResponse({'status': 'ok', 'mensaje': msg})

    except Exception as e:
        logger.error(f"Error cambiando contraseña: {str(e)}", exc_info=True)
        return JsonResponse({'status': 'error', 'mensaje': 'Ocurrió un error interno al intentar cambiar la contraseña.'}, status=500)


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
        logger.error(f"Error al enviar correo de cotización: {str(e)}")

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
        email_nuevo = data.get('email', '').strip().lower()
        razon_social = data.get('razon', '').strip()
        telefono = data.get('telefono', '').strip()
        direccion = data.get('direccion', '').strip()

        if email_nuevo and email_nuevo != user.email:
            try:
                validate_email(email_nuevo)
            except ValidationError:
                return JsonResponse({'status': 'error', 'mensaje': 'El correo electrónico ingresado no tiene un formato válido.'}, status=400)

            if User.objects.filter(email__iexact=email_nuevo).exclude(pk=user.pk).exists():
                return JsonResponse({'status': 'error', 'mensaje': 'Este correo electrónico ya está registrado por otra cuenta.'}, status=400)

            user.email = email_nuevo

        if nombre_completo:
            partes = nombre_completo.split(' ', 1)
            user.first_name = partes[0]
            user.last_name = partes[1] if len(partes) > 1 else ''

        user.save()

        perfil, _ = PerfilEmpresa.objects.get_or_create(user=user)
        perfil.razon_social = razon_social
        perfil.telefono_operativo = telefono
        perfil.direccion_principal = direccion
        perfil.save()

        return JsonResponse({
            'status': 'ok',
            'mensaje': 'Datos guardados correctamente en la base de datos.',
            'nombre': user.get_full_name() or user.username,
            'email': user.email
        })

    except ValidationError as ve:
        return JsonResponse({'status': 'error', 'mensaje': ' '.join(ve.messages)}, status=400)
    except Exception as e:
        logger.error(f"Error al actualizar datos de perfil: {str(e)}", exc_info=True)
        return JsonResponse({'status': 'error', 'mensaje': 'Ocurrió un error interno al actualizar tu perfil.'}, status=500)


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
        logger.error(f"Error al actualizar tema: {str(e)}")
        return JsonResponse({'status': 'error', 'mensaje': 'No se pudo guardar la preferencia.'}, status=400)


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
        return JsonResponse({'status': 'error', 'message': 'Datos inválidos'}, status=400)


@login_required
@require_POST
def registrar_pedido_checkout(request):
    try:
        email_usuario = request.user.email
        if not email_usuario or '@' not in email_usuario:
            return JsonResponse({'status': 'error', 'mensaje': 'Tu cuenta no tiene un correo electrónico válido registrado.'}, status=400)

        perfil = getattr(request.user, 'perfil_empresa', None)
        telefono_raw = perfil.telefono_operativo if perfil else ''
        telefono_limpio = re.sub(r'[^\d+]', '', telefono_raw or '')

        if len(re.sub(r'[^\d]', '', telefono_limpio)) < 10:
            return JsonResponse({'status': 'error', 'mensaje': 'Por favor registra un número telefónico válido (10 dígitos) en tu perfil antes de comprar.'}, status=400)

        data = json.loads(request.body)
        items_data = data.get('items', [])
        metodo = data.get('metodo', 'tarjeta')
        token_id = data.get('token_id', '')
        moneda_solicitada = data.get('moneda', 'MXN').upper()

        if not items_data:
            return JsonResponse({'status': 'error', 'mensaje': 'El carrito está vacío'}, status=400)

        tasa_usd = 1.0
        if moneda_solicitada == 'USD':
            try:
                res_tasa = requests.get('https://api.exchangerate-api.com/v4/latest/MXN', timeout=5)
                if res_tasa.status_code == 200:
                    tasa_usd = res_tasa.json().get('rates', {}).get('USD', 0.055)
                else:
                    tasa_usd = 0.055
            except Exception:
                tasa_usd = 0.055

        line_items_conekta = []
        total_centavos = 0
        items_a_crear = []

        with transaction.atomic():
            for item in items_data:
                item_id = str(item.get('id', ''))
                
                try:
                    cantidad = int(item.get('qty', item.get('cantidad', 1)))
                except (ValueError, TypeError):
                    return JsonResponse({'status': 'error', 'mensaje': 'Cantidad inválida para uno de los artículos.'}, status=400)

                if cantidad <= 0 or cantidad > 100:
                    return JsonResponse({'status': 'error', 'mensaje': 'La cantidad debe ser mayor a 0 y máximo 100 por artículo.'}, status=400)

                prod = Producto.objects.select_for_update().filter(id=item_id).first() if item_id.isdigit() else None
                curso = None
                if not prod:
                    curso = CursoDisponible.objects.filter(id=item_id).first() if item_id.isdigit() else None

                if not prod and not curso:
                    return JsonResponse({'status': 'error', 'mensaje': f'El artículo con ID "{item_id}" no existe en la base de datos.'}, status=400)

                if prod:
                    if getattr(prod, 'disponible', True) is False:
                        return JsonResponse({'status': 'error', 'mensaje': f'El producto "{prod.nombre}" no está disponible.'}, status=400)

                    if prod.stock < cantidad:
                        return JsonResponse({
                            'status': 'error',
                            'mensaje': f'Stock insuficiente para "{prod.nombre}". Disponibles: {prod.stock}, solicitados: {cantidad}'
                        }, status=400)

                    precio_mxn = prod.precio_base
                    nombre = prod.nombre
                    prod.stock -= cantidad
                    prod.save()
                else:
                    precio_mxn = curso.precio
                    nombre = curso.titulo

                if moneda_solicitada == 'USD':
                    precio_final = round(float(precio_mxn) * tasa_usd, 2)
                else:
                    precio_final = float(precio_mxn)

                unit_price_cents = int(precio_final * 100)
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
                    "precio_unitario": precio_final
                })

            total_cobrado = total_centavos / 100.0
            codigo = f"#EC-{uuid.uuid4().hex[:6].upper()}"

            order_payload = {
                "currency": moneda_solicitada,
                "customer_info": {
                    "name": (request.user.get_full_name() or request.user.username)[:100],
                    "email": email_usuario,
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
                raise ValueError(error_msg)

            conekta_order_id = conekta_data.get('id', '')
            charges_data = conekta_data.get('charges', {}).get('data', [])
            charge = charges_data[0] if len(charges_data) > 0 else {}

            clabe_spei = ''
            if metodo == 'tarjeta':
                charge_status = charge.get('status', '')
                if charge_status != 'paid':
                    mensaje_error = charge.get('failure_message') or 'La tarjeta fue declinada por el banco emisor.'
                    raise ValueError(f'Pago no autorizado: {mensaje_error}')
                estado_pago = 'pagado'
            else:
                estado_pago = 'pendiente'
                pm = charge.get('payment_method', {})
                clabe_spei = pm.get('clabe', '')

            resumen_txt = ", ".join([f"{i['nombre_item']} × {i['cantidad']}" for i in items_a_crear])[:245]
            
            pedido = Pedido.objects.create(
                usuario=request.user,
                codigo_pedido=codigo,
                equipo_insumo=f"[{moneda_solicitada}] {resumen_txt}"[:245],
                total=total_cobrado,
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
                'total': f"{total_cobrado:,.2f} {moneda_solicitada}",
                'estado_pago': estado_pago,
                'clabe': clabe_spei
            })

    except ValueError as ve:
        return JsonResponse({'status': 'error', 'mensaje': str(ve)}, status=400)
    except requests.exceptions.RequestException as re_err:
        logger.error(f"Error de conexión con Conekta: {str(re_err)}")
        return JsonResponse({'status': 'error', 'mensaje': "Error de comunicación con la pasarela de pagos."}, status=502)
    except Exception as e:
        logger.error(f"Error procesando la orden: {str(e)}", exc_info=True)
        return JsonResponse({'status': 'error', 'mensaje': "Ocurrió un error interno al procesar tu pedido. Intenta nuevamente."}, status=500)


def api_calendario_cursos(request):
    cursos = CursoDisponible.objects.filter(activo=True).exclude(fecha_evento__isnull=True)
    eventos = []

    for c in cursos:
        eventos.append({
            'id': c.id,
            'title': c.titulo,
            'start': c.fecha_evento.isoformat(),
            'extendedProps': {
                'precio': f"${c.precio:,.2f} MXN",
                'duracion': c.duracion,
                'cupos': c.cupos,
                'img': c.imagen.url if c.imagen else '/static/Assets/logo_web_ecodren.png'
            }
        })

    return JsonResponse(eventos, safe=False)


def _obtener_o_crear_cliente_conekta(user):
    perfil, _ = PerfilEmpresa.objects.get_or_create(user=user)
    private_key = getattr(settings, 'CONEKTA_PRIVATE_KEY', '') or ''
    
    if not private_key:
        logger.error("[CONEKTA ERROR] No se encontró CONEKTA_PRIVATE_KEY en settings.py")
        return None

    auth = (private_key, '')
    headers = {
        'Accept': 'application/vnd.conekta-v2.0.0+json',
        'Content-Type': 'application/json'
    }

    if perfil.conekta_customer_id:
        res = requests.get(f'https://api.conekta.io/customers/{perfil.conekta_customer_id}', auth=auth, headers=headers)
        if res.status_code == 200:
            return res.json()
        else:
            perfil.conekta_customer_id = None
            perfil.save(update_fields=['conekta_customer_id'])

    telefono_raw = perfil.telefono_operativo or '+525512345678'
    telefono_limpio = re.sub(r'[^\d+]', '', telefono_raw)
    if len(re.sub(r'[^\d]', '', telefono_limpio)) < 10:
        telefono_limpio = "+525512345678"

    payload = {
        "name": (user.get_full_name() or user.username)[:100],
        "email": user.email or f"cliente_{user.id}@ecodren.com",
        "phone": telefono_limpio
    }

    res = requests.post('https://api.conekta.io/customers', auth=auth, headers=headers, json=payload)
    if res.status_code in (200, 201):
        cust_data = res.json()
        perfil.conekta_customer_id = cust_data.get('id')
        perfil.save(update_fields=['conekta_customer_id'])
        return cust_data
    else:
        logger.error(f"[CONEKTA ERROR {res.status_code}] {res.text}")
        return None


@login_required
@require_POST
def agregar_metodo_pago(request):
    try:
        data = json.loads(request.body)
        token_id = data.get('token_id')
        if not token_id:
            return JsonResponse({'status': 'error', 'mensaje': 'Token de tarjeta no válido.'}, status=400)

        cliente = _obtener_o_crear_cliente_conekta(request.user)
        if not cliente:
            return JsonResponse({'status': 'error', 'mensaje': 'No se pudo conectar o crear el cliente en Conekta.'}, status=500)

        private_key = getattr(settings, 'CONEKTA_PRIVATE_KEY', '') or ''
        customer_id = cliente['id']

        headers = {
            'Accept': 'application/vnd.conekta-v2.0.0+json',
            'Content-Type': 'application/json'
        }

        res = requests.post(
            f'https://api.conekta.io/customers/{customer_id}/payment_sources',
            auth=(private_key, ''),
            headers=headers,
            json={"type": "card", "token_id": token_id}
        )

        if res.status_code in (200, 201):
            return JsonResponse({'status': 'ok', 'mensaje': 'Método de pago guardado con éxito en Conekta.'})
        else:
            err = res.json()
            msg = err.get('message') or err.get('details', [{}])[0].get('message', 'Error al guardar la tarjeta.')
            return JsonResponse({'status': 'error', 'mensaje': msg}, status=400)

    except Exception as e:
        logger.error(f"Error al agregar método de pago: {str(e)}", exc_info=True)
        return JsonResponse({'status': 'error', 'mensaje': 'Ocurrió un error al vincular el método de pago.'}, status=500)


@login_required
@require_POST
def eliminar_metodo_pago(request):
    try:
        data = json.loads(request.body)
        source_id = data.get('source_id')
        perfil = getattr(request.user, 'perfil_empresa', None)

        if not perfil or not perfil.conekta_customer_id or not source_id:
            return JsonResponse({'status': 'error', 'mensaje': 'Datos de solicitud incompletos.'}, status=400)

        private_key = getattr(settings, 'CONEKTA_PRIVATE_KEY', '') or ''
        headers = {
            'Accept': 'application/vnd.conekta-v2.0.0+json',
            'Content-Type': 'application/json'
        }

        res = requests.delete(
            f'https://api.conekta.io/customers/{perfil.conekta_customer_id}/payment_sources/{source_id}',
            auth=(private_key, ''),
            headers=headers
        )

        if res.status_code in (200, 204):
            return JsonResponse({'status': 'ok', 'mensaje': 'Método de pago eliminado correctamente.'})
        else:
            try:
                err_data = res.json()
                msg = err_data.get('message') or err_data.get('details', [{}])[0].get('message', 'Error al eliminar en Conekta.')
            except Exception:
                msg = res.text
            return JsonResponse({'status': 'error', 'mensaje': msg}, status=400)

    except Exception as e:
        logger.error(f"Error al eliminar método de pago: {str(e)}", exc_info=True)
        return JsonResponse({'status': 'error', 'mensaje': 'Ocurrió un error al eliminar el método de pago.'}, status=500)


@csrf_exempt
def conekta_webhook(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'mensaje': 'Método no permitido'}, status=405)
    
    try:
        payload = json.loads(request.body)
        event_type = payload.get('type', '')

        if event_type == 'order.paid':
            order_data = payload.get('data', {}).get('object', {})
            conekta_order_id = order_data.get('id')

            if conekta_order_id:
                pedido = Pedido.objects.filter(conekta_order_id=conekta_order_id).first()
                if pedido:
                    pedido.estado_pago = 'pagado'
                    pedido.estatus = 'completado'
                    pedido.save(update_fields=['estado_pago', 'estatus'])

        return JsonResponse({'status': 'ok'})
    except Exception as e:
        logger.error(f"Error procesando Webhook Conekta: {str(e)}", exc_info=True)
        return JsonResponse({'status': 'error', 'mensaje': 'Error procesando evento'}, status=400)


@login_required
@require_POST
def actualizar_avatar(request):
    try:
        data = json.loads(request.body)
        avatar_b64 = data.get('avatar_b64', '').strip()

        if not avatar_b64 or not avatar_b64.startswith('data:image'):
            return JsonResponse({'status': 'error', 'mensaje': 'Formato de imagen no válido.'}, status=400)

        if len(avatar_b64) > 3 * 1024 * 1024:
            return JsonResponse({'status': 'error', 'mensaje': 'La imagen excede el tamaño máximo permitido.'}, status=400)

        perfil, _ = PerfilEmpresa.objects.get_or_create(user=request.user)
        perfil.avatar_base64 = avatar_b64
        perfil.save(update_fields=['avatar_base64'])

        return JsonResponse({'status': 'ok', 'mensaje': 'Foto de perfil actualizada correctamente.'})
    except Exception as e:
        logger.error(f"Error al guardar avatar: {str(e)}", exc_info=True)
        return JsonResponse({'status': 'error', 'mensaje': 'Ocurrió un error interno al guardar la foto de perfil.'}, status=500)