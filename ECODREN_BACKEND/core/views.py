import json
import re
import uuid
import logging
import requests
import base64
import io
from PIL import Image
from allauth.account.models import EmailAddress
from django.core.cache import cache
from django.shortcuts import render, redirect
from django.db import transaction
from django.db.models import Q
from django.contrib.auth import update_session_auth_hash, authenticate, login, logout
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
from django.contrib.auth.forms import PasswordResetForm
from django.contrib import messages

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
    try:
        ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', '')).split(',')[0].strip()
        cache_key = f"cotizacion_ratelimit_{ip}"
        peticiones = cache.get(cache_key, 0)

        if peticiones >= 5:
            return JsonResponse({
                'status': 'error', 
                'mensaje': 'Has alcanzado el límite de solicitudes de cotización por hora. Intenta más tarde.'
            }, status=429)

        honeypot = request.POST.get('website_hp', '').strip()
        if honeypot:
            return JsonResponse({'status': 'ok', 'mensaje': 'Solicitud recibida correctamente.'})

        nombre = request.POST.get('nombre', '').strip()
        empresa = request.POST.get('empresa', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        email = request.POST.get('email', '').strip().lower()
        categoria = request.POST.get('categoria', '').strip()
        detalles = request.POST.get('detalles', '').strip()

        if not nombre or not email:
            return JsonResponse({'status': 'error', 'mensaje': 'El nombre y correo electrónico son requeridos.'}, status=400)

        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse({'status': 'error', 'mensaje': 'El correo electrónico no tiene un formato válido.'}, status=400)

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

        asunto_cliente = f"Hemos recibido tu solicitud de cotización #COT-{cotizacion.id:04d} | ECODREN"
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
            logger.error(f"Error al enviar correo de cotización al cliente ({email}): {str(e)}", exc_info=True)

        email_ventas = getattr(settings, 'VENTAS_EMAIL', settings.DEFAULT_FROM_EMAIL)
        asunto_ventas = f"🚨 NUEVA COTIZACIÓN RECIBIDA #COT-{cotizacion.id:04d} - {nombre}"
        mensaje_ventas = (
            f"Se ha recibido una nueva solicitud de cotización a través de la plataforma web:\n\n"
            f"• Folio: #COT-{cotizacion.id:04d}\n"
            f"• Cliente: {nombre}\n"
            f"• Empresa: {empresa or 'Particular'}\n"
            f"• Correo electrónico: {email}\n"
            f"• Teléfono de contacto: {telefono or 'No proporcionado'}\n"
            f"• Categoría de interés: {categoria or 'General'}\n"
            f"• Requerimiento detallado:\n{detalles or 'Sin detalles adicionales'}\n\n"
            f"Usuario registrado: {'Sí (' + usuario_activo.username + ')' if usuario_activo else 'No (Visitante anónimo)'}\n"
        )

        try:
            send_mail(
                asunto_ventas,
                mensaje_ventas,
                settings.DEFAULT_FROM_EMAIL,
                [email_ventas],
                fail_silently=False,
            )
        except Exception as e:
            logger.error(f"Error al notificar al equipo de ventas ({email_ventas}): {str(e)}", exc_info=True)

        cache.set(cache_key, peticiones + 1, 3600)

        return JsonResponse({
            'status': 'ok',
            'mensaje': '¡Cotización enviada con éxito! Te hemos enviado un correo con los detalles.'
        })

    except Exception as e:
        logger.error(f"Error inesperado en enviar_cotizacion: {str(e)}", exc_info=True)
        return JsonResponse({
            'status': 'error', 
            'mensaje': 'Ocurrió un error interno al procesar tu cotización. Por favor intenta nuevamente.'
        }, status=500)


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

            # Sincronización con django-allauth
            try:
                EmailAddress.objects.filter(user=user, primary=True).update(primary=False)
                email_obj, created = EmailAddress.objects.get_or_create(user=user, email=email_nuevo)
                email_obj.primary = True
                email_obj.verified = True
                email_obj.save()
            except Exception as allauth_err:
                logger.warning(f"No se pudo sincronizar el correo con allauth: {allauth_err}")

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


@login_required
@require_POST
def api_actualizar_localizacion(request):
    try:
        data = json.loads(request.body)
        perfil, _ = PerfilEmpresa.objects.get_or_create(user=request.user)

        field_moneda = PerfilEmpresa._meta.get_field('moneda_defecto')
        field_idioma = PerfilEmpresa._meta.get_field('idioma_panel')

        monedas_validas = [c[0] for c in field_moneda.choices] if field_moneda.choices else ['MXN', 'USD']
        idiomas_validos = [c[0] for c in field_idioma.choices] if field_idioma.choices else ['es', 'en']

        campos_a_actualizar = []

        if 'moneda' in data:
            moneda = str(data.get('moneda', '')).strip().upper()
            if moneda not in monedas_validas:
                return JsonResponse({
                    'status': 'error', 
                    'mensaje': f'Moneda no válida. Opciones permitidas: {", ".join(monedas_validas)}'
                }, status=400)
            perfil.moneda_defecto = moneda
            campos_a_actualizar.append('moneda_defecto')

        if 'idioma' in data:
            idioma = str(data.get('idioma', '')).strip().lower()
            if idioma not in idiomas_validos:
                return JsonResponse({
                    'status': 'error', 
                    'mensaje': f'Idioma no válido. Opciones permitidas: {", ".join(idiomas_validos)}'
                }, status=400)
            perfil.idioma_panel = idioma
            campos_a_actualizar.append('idioma_panel')

        if campos_a_actualizar:
            perfil.save(update_fields=campos_a_actualizar)

        return JsonResponse({
            'status': 'ok',
            'moneda': perfil.moneda_defecto,
            'idioma': perfil.idioma_panel
        })

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'mensaje': 'Formato JSON inválido.'}, status=400)
    except Exception as e:
        logger.error(f"Error al actualizar localización: {str(e)}", exc_info=True)
        return JsonResponse({'status': 'error', 'mensaje': 'Ocurrió un error al actualizar tus preferencias.'}, status=500)


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
        direccion_id = data.get('direccion_id')

        direccion_obj = None
        if direccion_id:
            direccion_obj = DireccionEntrega.objects.filter(id=direccion_id, usuario=request.user).first()

        if not direccion_obj:
            direccion_obj = DireccionEntrega.objects.filter(usuario=request.user, es_principal=True).first() or \
                            DireccionEntrega.objects.filter(usuario=request.user).first()

        if not direccion_obj:
            return JsonResponse({
                'status': 'error', 
                'mensaje': 'Debes registrar al menos una dirección de entrega en tu perfil antes de finalizar la compra.'
            }, status=400)

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
                "line_items": line_items_conekta,
                "shipping_lines": [{
                    "amount": 0,
                    "carrier": "ECODREN Logistics"
                }],
                "shipping_contact": {
                    "phone": direccion_obj.telefono,
                    "receiver": direccion_obj.nombre_destinatario[:100],
                    "address": {
                        "street1": direccion_obj.calle_numero[:100],
                        "street2": direccion_obj.colonia[:100] if direccion_obj.colonia else "",
                        "city": direccion_obj.ciudad[:100],
                        "state": direccion_obj.estado[:100],
                        "country": "MX",
                        "postal_code": direccion_obj.codigo_postal
                    }
                }
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

        # 1. Validar esquema de la imagen (PNG, JPG, JPEG, WEBP)
        match = re.match(r'^data:image/(png|jpeg|jpg|webp);base64,', avatar_b64)
        if not match:
            return JsonResponse({'status': 'error', 'mensaje': 'Formato no soportado. Formatos permitidos: PNG, JPG, JPEG y WEBP.'}, status=400)

        # 2. Decodificar Base64
        try:
            raw_b64 = avatar_b64.split(',', 1)[1]
            img_bytes = base64.b64decode(raw_b64)
        except Exception:
            return JsonResponse({'status': 'error', 'mensaje': 'La codificación Base64 de la imagen es corrupta.'}, status=400)

        # 3. Validar peso máximo binario (2 MB)
        MAX_SIZE_BYTES = 2 * 1024 * 1024
        if len(img_bytes) > MAX_SIZE_BYTES:
            return JsonResponse({'status': 'error', 'mensaje': 'La imagen excede el tamaño máximo permitido (2 MB).'}, status=400)

        # 4. Verificar integridad y formato real con Pillow
        try:
            img = Image.open(io.BytesIO(img_bytes))
            img.verify()
            if img.format.upper() not in ['JPEG', 'PNG', 'WEBP']:
                return JsonResponse({'status': 'error', 'mensaje': 'El archivo no es una imagen válida o compatible.'}, status=400)
        except Exception:
            return JsonResponse({'status': 'error', 'mensaje': 'El archivo enviado no pudo ser verificado como una imagen válida.'}, status=400)

        perfil, _ = PerfilEmpresa.objects.get_or_create(user=request.user)
        perfil.avatar_base64 = avatar_b64
        perfil.save(update_fields=['avatar_base64'])

        return JsonResponse({'status': 'ok', 'mensaje': 'Foto de perfil actualizada correctamente.'})
    except Exception as e:
        logger.error(f"Error al guardar avatar: {str(e)}", exc_info=True)
        return JsonResponse({'status': 'error', 'mensaje': 'Ocurrió un error interno al guardar la foto de perfil.'}, status=500)


@require_POST
def api_login(request):
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')

        if not email or not password:
            return JsonResponse({'status': 'error', 'mensaje': 'Por favor ingresa tu correo y contraseña.'}, status=400)

        user_obj = User.objects.filter(Q(email__iexact=email) | Q(username__iexact=email)).first()
        if not user_obj:
            return JsonResponse({'status': 'error', 'mensaje': 'Credenciales inválidas.'}, status=400)

        user = authenticate(request, username=user_obj.username, password=password)
        if user is not None:
            if not user.is_active:
                return JsonResponse({'status': 'error', 'mensaje': 'Esta cuenta ha sido desactivada.'}, status=403)
            login(request, user)
            return JsonResponse({'status': 'ok', 'mensaje': '!Sesión iniciada correctamente!'})
        else:
            return JsonResponse({'status': 'error', 'mensaje': 'Correo o contraseña incorrectos'}, status=400)

    except Exception as e:
        logger.error(f"Error en api_login: {str(e)}", exc_info=True)
        return JsonResponse({'status': 'error', 'mensaje': 'Ocurrio un error al iniciar sesión.'}, status=500)


@require_POST
def api_register(request):
    try:
        data = json.loads(request.body)
        nombre = data.get('nombre', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        empresa = data.get('empresa', '').strip()

        if not nombre or not email or not password:
            return JsonResponse({'status': 'error', 'mensaje': 'Todos los campos obligatorios deben ser completados.'}, status=400)

        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse({'status': 'error', 'mensaje': 'El correo electrónico no es válido.'}, status=400)

        if User.objects.filter(email__iexact=email).exists():
            return JsonResponse({'status': 'error', 'mensaje': 'Este correo electrónico ya está registrado.'}, status=400)

        try:
            validate_password(password)
        except ValidationError as ve:
            return JsonResponse({'status': 'error', 'mensaje': ' '.join(ve.messages)}, status=400)

        username = email.split('@')[0]
        original_username = username
        counter = 1
        while User.objects.filter(username__iexact=username).exists():
            username = f"{original_username}{counter}"
            counter += 1

        partes = nombre.split(' ', 1)
        first_name = partes[0]
        last_name = partes[1] if len(partes) > 1 else ''

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        perfil, _ = PerfilEmpresa.objects.get_or_create(user=user)
        if empresa:
            perfil.razon_social = empresa
            perfil.save(update_fields=['razon_social'])

        login(request, user)
        return JsonResponse({'status': 'ok', 'mensaje': '¡Cuenta creada e inicio de sesión exitoso!'})

    except Exception as e:
        logger.error(f"Error en api_register: {str(e)}", exc_info=True)
        return JsonResponse({'status': 'error', 'mensaje': 'Ocurrió un error al crear la cuenta.'}, status=500)


@require_POST
def api_forget_password(request):
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip().lower()

        if not email:
            return JsonResponse({'status': 'error', 'mensaje': 'Por favor ingresa tu correo electrónico.'}, status=400)

        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse({'status': 'error', 'mensaje': 'El correo electrónico no es válido.'}, status=400)

        form = PasswordResetForm({'email': email})
        if form.is_valid():
            form.save(
                request=request,
                use_https=request.is_secure(),
                from_email=settings.DEFAULT_FROM_EMAIL
            )

        return JsonResponse({'status': 'ok', 'mensaje': 'Si el correo está registrado, recibirás las instrucciones para restablecer tu contraseña.'})

    except Exception as e:
        logger.error(f"Error en api_forget_password: {str(e)}", exc_info=True)
        return JsonResponse({'status': 'error', 'mensaje': 'Ocurrió un error al procesar tu solicitud.'}, status=500)


@require_POST
def api_logout(request):
    logout(request)
    return JsonResponse({'status': 'ok', 'mensaje': 'Sesión cerrada correctamente.'})


@login_required
@require_POST
def guardar_direccion(request):
    try:
        data = json.loads(request.body)
        direccion_id = data.get('id')
        nombre_destinatario = data.get('nombre_destinatario', '').strip()
        calle_numero = data.get('calle_numero', '').strip()
        colonia = data.get('colonia', '').strip()
        ciudad = data.get('ciudad', '').strip()
        estado = data.get('estado', '').strip()
        codigo_postal = data.get('codigo_postal', '').strip()
        telefono = data.get('telefono', '').strip()
        es_principal = data.get('es_principal', False)

        if not all([nombre_destinatario, calle_numero, ciudad, estado, codigo_postal, telefono]):
            return JsonResponse({'status': 'error', 'mensaje': 'Por favor completa todos los campos obligatorios de la dirección.'}, status=400)

        if es_principal:
            DireccionEntrega.objects.filter(usuario=request.user).update(es_principal=False)

        if direccion_id:
            direccion = DireccionEntrega.objects.filter(id=direccion_id, usuario=request.user).first()
            if not direccion:
                return JsonResponse({'status': 'error', 'mensaje': 'Dirección no encontrada.'}, status=404)
        else:
            direccion = DireccionEntrega(usuario=request.user)

        direccion.nombre_destinatario = nombre_destinatario
        direccion.calle_numero = calle_numero
        direccion.colonia = colonia
        direccion.ciudad = ciudad
        direccion.estado = estado
        direccion.codigo_postal = codigo_postal
        direccion.telefono = telefono
        direccion.es_principal = es_principal
        direccion.save()

        return JsonResponse({
            'status': 'ok',
            'mensaje': 'Dirección guardada correctamente.',
            'direccion': {
                'id': direccion.id,
                'destinatario': direccion.nombre_destinatario,
                'calle': direccion.calle_numero,
                'colonia': direccion.colonia,
                'ciudad': direccion.ciudad,
                'estado': direccion.estado,
                'cp': direccion.codigo_postal,
                'telefono': direccion.telefono,
                'es_principal': direccion.es_principal
            }
        })
    except Exception as e:
        logger.error(f"Error al guardar dirección: {str(e)}", exc_info=True)
        return JsonResponse({'status': 'error', 'mensaje': 'Ocurrió un error al procesar la dirección.'}, status=500)


@login_required
@require_POST
def eliminar_direccion(request):
    try:
        data = json.loads(request.body)
        direccion_id = data.get('id')
        direccion = DireccionEntrega.objects.filter(id=direccion_id, usuario=request.user).first()
        
        if not direccion:
            return JsonResponse({'status': 'error', 'mensaje': 'La dirección solicitada no existe.'}, status=404)
        
        direccion.delete()
        return JsonResponse({'status': 'ok', 'mensaje': 'Dirección eliminada correctamente.'})
    except Exception as e:
        logger.error(f"Error al eliminar dirección: {str(e)}", exc_info=True)
        return JsonResponse({'status': 'error', 'mensaje': 'Ocurrió un error al eliminar la dirección.'}, status=500)