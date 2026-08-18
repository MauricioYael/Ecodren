from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = "Crea los grupos y asigna permisos bajo el principio de mínimo privilegio."

    def handle(self, *args, **options):
        # 1. Editor de Catálogo: CRUD completo en productos, maquinaria y categorías
        catalogo_group, _ = Group.objects.get_or_create(name='Editor de Catálogo')
        modelos_catalogo = ['categoria', 'producto', 'maquinaria', 'imagenmaquinaria', 'equipamento', 'accesorioextra', 'puntodestacado']
        perms_catalogo = Permission.objects.filter(content_type__app_label='core', content_type__model__in=modelos_catalogo)
        catalogo_group.permissions.set(perms_catalogo)

        # 2. Editor de Contenido: CRUD completo en recursos y capacitaciones
        contenido_group, _ = Group.objects.get_or_create(name='Editor de Contenido')
        modelos_contenido = ['publicacionrecurso', 'documentotecnico', 'capacitacionimpartida', 'cursodisponible']
        perms_contenido = Permission.objects.filter(content_type__app_label='core', content_type__model__in=modelos_contenido)
        contenido_group.permissions.set(perms_contenido)

        # 3. Soporte y Ventas: Solo LECTURA (view_*) + Cambio de estado en Pedidos (change_pedido)
        soporte_group, _ = Group.objects.get_or_create(name='Soporte y Ventas')
        modelos_soporte = ['pedido', 'cotizacionguardada', 'perfilempresa', 'direccionentrega']
        perms_soporte = Permission.objects.filter(
            content_type__app_label='core',
            content_type__model__in=modelos_soporte
        ).filter(
            codename__startswith='view_'
        ) | Permission.objects.filter(
            content_type__app_label='core',
            content_type__model='pedido',
            codename='change_pedido'
        )
        soporte_group.permissions.set(perms_soporte)

        self.stdout.write(self.style.SUCCESS("✔ Permisos y roles actualizados con políticas de seguridad."))