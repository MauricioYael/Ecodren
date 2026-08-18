import unicodedata
from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import Categoria, Producto, Maquinaria


class Command(BaseCommand):
    help = "Carga y actualiza de forma idempotente el catálogo de productos y refacciones."

    # Diccionario explícito de prefijos para evitar colisiones entre categorías similares
    PREFIJOS_CATEGORIA = {
        'boquillas': 'BOQ',
        'bombas': 'BMP',
        'mangueras': 'MNG',
        'valvulas': 'VLV',
        'filtros': 'FLT',
        'conexiones': 'CNX',
        'toberas': 'TOB',
        'accesorios': 'ACC',
        'motores': 'MOT',
        'sellos': 'SEL',
    }

    # Datos base del catálogo (nombres con o sin espacios se limpian automáticamente)
    DATOS_CATALOGO = [
        # --- Boquillas y Toberas ---
        {
            'categoria': 'Boquillas y Toberas',
            'nombre': 'Tobera Rotativa 3D Premium',
            'sku_custom': 'TOB-3D-01',
            'precio': 4500.00,
            'stock': 12,
            'descripcion': 'Tobera de alta eficiencia para desazolve de drenajes pesados con chorros multidireccionales.',
            'especificaciones': 'Presión: hasta 4000 PSI | Caudal: 40-80 GPM | Conexión: 1" NPT',
            'compatibilidad': ['Ecodren 17', 'Ecovac', 'Ecojet']
        },
        {
            'categoria': 'Boquillas y Toberas',
            'nombre': 'Boquilla Limpiadora Gran Angular',
            'sku_custom': 'BOQ-ANG-02',
            'precio': 3200.00,
            'stock': 20,
            'descripcion': 'Boquilla estándar de arrastre y penetración para limpiezas preventivas.',
            'especificaciones': 'Presión: hasta 3000 PSI | Caudal: 30-60 GPM | Conexión: 3/4" NPT',
            'compatibilidad': ['Ecojet']
        },
        # --- Mangueras ---
        {
            'categoria': 'Mangueras Hidráulicas',
            'nombre': 'Manguera Hidrojet Reforzada 3/4" (100m)',
            'sku_custom': 'MNG-HID-100',
            'precio': 7500.00,
            'stock': 8,
            'descripcion': 'Manguera termoplástica de alta flexibilidad resistente a la abrasión y corte.',
            'especificaciones': 'Presión de trabajo: 3000 PSI | Presión de ruptura: 7500 PSI | Longitud: 100 m',
            'compatibilidad': ['Ecodren 17', 'Ecojet']
        },
        # --- Bombas y Componentes ---
        {
            'categoria': 'Bombas y Motores',
            'nombre': ' Base de pistón cerámico para bomba triplex', # Con espacio intencional para prueba de limpieza
            'sku_custom': 'BMP-PST-03',
            'precio': 1850.00,
            'stock': 15,
            'descripcion': 'Pistón cerámico de repuesto de alta resistencia térmica y mecánica.',
            'especificaciones': 'Diámetro: 20 mm | Compatible con bombas tipo Pratissoli / Hawk',
            'compatibilidad': ['Ecodren 17', 'Ecoclean']
        },
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Ejecuta la validación completa sin guardar cambios en la base de datos.',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Elimina todos los productos y categorías existentes antes de cargar.',
        )

    def normalizar_texto(self, texto):
        """Elimina acentos y normaliza a minúsculas para comparaciones consistentes."""
        if not texto:
            return ""
        texto = texto.strip().lower()
        return ''.join(
            c for c in unicodedata.normalize('NFD', texto)
            if unicodedata.category(c) != 'Mn'
        )

    def obtener_prefijo_sku(self, nombre_cat):
        """Calcula un prefijo de 3 letras único y seguro para la categoría."""
        clave_norm = self.normalizar_texto(nombre_cat)
        
        for clave, prefijo in self.PREFIJOS_CATEGORIA.items():
            if clave in clave_norm:
                return prefijo
        
        # Fallback determinista de 3 letras alfanuméricas
        letras = [c.upper() for c in clave_norm if c.isalnum()]
        return ''.join(letras[:3]).ljust(3, 'X')

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        clear_all = options['clear']

        if dry_run:
            self.stdout.write(self.style.WARNING("🔍 MODO DRY-RUN ACTIVADO: No se guardarán cambios en la base de datos.\n"))

        try:
            with transaction.atomic():
                if clear_all:
                    self.stdout.write(self.style.NOTICE("🧹 Eliminando catálogo previo..."))
                    if not dry_run:
                        Producto.objects.all().delete()
                        Categoria.objects.all().delete()
                    self.stdout.write(self.style.SUCCESS("Catálogo previo eliminado correctamente.\n"))

                categorias_procesadas = 0
                productos_creados = 0
                productos_actualizados = 0

                for item in self.DATOS_CATALOGO:
                    # 1. Limpieza de espacios en blanco
                    cat_nombre = item['categoria'].strip()
                    prod_nombre = item['nombre'].strip()
                    sku_custom = item.get('sku_custom', '').strip()
                    descripcion = item.get('descripcion', '').strip()
                    especificaciones = item.get('especificaciones', '').strip()
                    precio = item.get('precio', 0.0)
                    stock = item.get('stock', 0)

                    # 2. Obtener o actualizar Categoría
                    categoria, cat_created = Categoria.objects.update_or_create(
                        nombre=cat_nombre,
                        defaults={'descripcion': f'Refacciones e insumos de la categoría {cat_nombre}'}
                    )
                    if cat_created:
                        categorias_procesadas += 1

                    # 3. Generar SKU seguro si no viene definido
                    if not sku_custom:
                        prefijo = self.obtener_prefijo_sku(cat_nombre)
                        conteo_cat = Producto.objects.filter(categoria=categoria).count() + 1
                        sku_custom = f"{prefijo}-{conteo_cat:03d}"

                    # 4. update_or_create del Producto basado en SKU único
                    producto, creado = Producto.objects.update_or_create(
                        codigo_sku=sku_custom,
                        defaults={
                            'categoria': categoria,
                            'nombre': prod_nombre,
                            'descripcion': descripcion,
                            'especificaciones': especificaciones,
                            'precio_base': precio,
                            'stock': stock,
                            'disponible': stock > 0,
                        }
                    )

                    # 5. Relacionar con Maquinarias compatibles
                    maquinas_compatibles = item.get('compatibilidad', [])
                    for nombre_maq in maquinas_compatibles:
                        maquinas_encontradas = Maquinaria.objects.filter(
                            nombre__icontains=nombre_maq.strip()
                        )
                        for maq in maquinas_encontradas:
                            producto.maquinarias_compatibles.add(maq)

                    if creado:
                        productos_creados += 1
                        self.stdout.write(self.style.SUCCESS(f"  [+] Creado: [{sku_custom}] {prod_nombre}"))
                    else:
                        productos_actualizados += 1
                        self.stdout.write(self.style.NOTICE(f"  [*] Actualizado: [{sku_custom}] {prod_nombre}"))

                if dry_run:
                    # En modo dry-run forzamos rollback antes de salir del bloque
                    transaction.set_rollback(True)
                    self.stdout.write(self.style.WARNING(
                        f"\nSimulación finalizada con éxito: "
                        f"{productos_creados} productos por crear, "
                        f"{productos_actualizados} por actualizar."
                    ))
                else:
                    self.stdout.write(self.style.SUCCESS(
                        f"\n✅ Carga completada exitosamente:\n"
                        f"  - Nuevas Categorías: {categorias_procesadas}\n"
                        f"  - Productos Creados: {productos_creados}\n"
                        f"  - Productos Actualizados: {productos_actualizados}\n"
                    ))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n❌ Error durante la transacción: {str(e)}"))
            raise e