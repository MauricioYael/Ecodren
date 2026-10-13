import json
import random
import re
import requests
from django.shortcuts import render
from django.db.models import Q
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from .models import (
    Producto, Categoria, Maquinaria, PublicacionRecurso, 
    DocumentoTecnico, CapacitacionImpartida, CursoDisponible,
    PerfilEmpresa, DireccionEntrega, Pedido, ItemPedido, 
    CotizacionGuardada, SolicitudCotizacion, ChasisOption
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
        'has_usable_password': request.user.has_usable_password()  # 👈 Indicador de contraseña local
    }
    return render(request, 'perfil.html', context)


@login_required
@require_POST
def cambiar_password(request):
    try:
        data = json.loads(request.body)
        password_actual = data.get('password_actual', '').strip()
        password_nueva = data.get('password_nueva', '').strip()
        password_confirmar = data.get('password_confirmar', '').strip()

        user = request.user
        tiene_password = user.has_usable_password()

        # Solo validar la contraseña actual si el usuario ya tiene una establecida
        if tiene_password:
            if not password_actual:
                return JsonResponse({'status': 'error', 'mensaje': 'Por favor ingresa tu contraseña actual.'}, status=400)
            if not user.check_password(password_actual):
                return JsonResponse({'status': 'error', 'mensaje': 'La contraseña actual es incorrecta.'}, status=400)

        # Validaciones para la nueva contraseña
        if not password_nueva or len(password_nueva) < 8:
            return JsonResponse({'status': 'error', 'mensaje': 'La nueva contraseña debe tener al menos 8 caracteres.'}, status=400)

        if password_nueva != password_confirmar:
            return JsonResponse({'status': 'error', 'mensaje': 'La nueva contraseña y su confirmación no coinciden.'}, status=400)

        # Guardar nueva contraseña
        user.set_password(password_nueva)
        user.save()

        # Mantener la sesión activa tras cambiar la contraseña
        update_session_auth_hash(request, user)

        msg = 'Contraseña creada exitosamente.' if not tiene_password else 'Contraseña actualizada correctamente.'
        return JsonResponse({'status': 'ok', 'mensaje': msg})

    except Exception as e:
        return JsonResponse({'status': 'error', 'mensaje': f'Error interno: {str(e)}'}, status=500)


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

        for item in items_data:
            item_id = str(item.get('id', ''))
            cantidad = int(item.get('qty', item.get('cantidad', 1)))

            prod = Producto.objects.filter(id=item_id).first() if item_id.isdigit() else None
            curso = None
            if not prod:
                curso = CursoDisponible.objects.filter(id=item_id).first() if item_id.isdigit() else None

            precio_mxn = prod.precio_base if prod else (curso.precio if curso else float(item.get('precio', 0)))
            if moneda_solicitada == 'USD':
                precio_final = round(float(precio_mxn) * tasa_usd, 2)
            else:
                precio_final = float(precio_mxn)

            nombre = prod.nombre if prod else (curso.titulo if curso else item.get('nombre', 'Artículo'))
            
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
        codigo = f"#EC-2026-{random.randint(1000, 9999)}"

        telefono_raw = getattr(getattr(request.user, 'perfil_empresa', None), 'telefono_operativo', '') or '+525512345678'
        telefono_limpio = re.sub(r'[^\d+]', '', telefono_raw)
        if len(telefono_limpio) < 10:
            telefono_limpio = "+525512345678"

        order_payload = {
            "currency": moneda_solicitada,
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

    except requests.exceptions.RequestException as re_err:
        return JsonResponse({'status': 'error', 'mensaje': f"Error de conexión con Conekta: {str(re_err)}"}, status=502)
    except Exception as e:
        return JsonResponse({'status': 'error', 'mensaje': f"Error interno: {str(e)}"}, status=500)


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
        print("[CONEKTA ERROR] No se encontró CONEKTA_PRIVATE_KEY en settings.py")
        return None

    auth = (private_key, '')
    headers = {
        'Accept': 'application/vnd.conekta-v2.0.0+json',
        'Content-Type': 'application/json'
    }

    # 1. Si el usuario ya tiene ID de cliente registrado, verificar que exista en Conekta
    if perfil.conekta_customer_id:
        res = requests.get(f'https://api.conekta.io/customers/{perfil.conekta_customer_id}', auth=auth, headers=headers)
        if res.status_code == 200:
            return res.json()
        else:
            # Si el cliente ya no existe en Conekta (ejemplo: al resetear Sandbox), se limpia el ID guardado
            perfil.conekta_customer_id = None
            perfil.save(update_fields=['conekta_customer_id'])

    # 2. Formatear teléfono para cumplir requerimientos de Conekta
    telefono_raw = perfil.telefono_operativo or '+525512345678'
    telefono_limpio = re.sub(r'[^\d+]', '', telefono_raw)
    if len(telefono_limpio) < 10:
        telefono_limpio = "+525512345678"

    payload = {
        "name": (user.get_full_name() or user.username)[:100],
        "email": user.email or f"cliente_{user.id}@ecodren.com",
        "phone": telefono_limpio
    }

    # 3. Crear cliente en Conekta
    res = requests.post('https://api.conekta.io/customers', auth=auth, headers=headers, json=payload)
    if res.status_code in (200, 201):
        cust_data = res.json()
        perfil.conekta_customer_id = cust_data.get('id')
        perfil.save(update_fields=['conekta_customer_id'])
        return cust_data
    else:
        print(f"[CONEKTA ERROR {res.status_code}] {res.text}")
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
        return JsonResponse({'status': 'error', 'mensaje': str(e)}, status=500)


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
        return JsonResponse({'status': 'error', 'mensaje': f'Error interno: {str(e)}'}, status=500)