import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Categoria, Producto

DATOS_CATALOGO = {
    "Eléctrico": [
        "Switch de cola de rata", "Switch de vacio", "Switch con seguro",
        "Joystick", "Joystick dual", "Switch de 3 posiciones",
        "Valvula electro-neumatica", "Base de relay para bombas de agua", "Flechas de transito",
        "Flechas de señalización", "Switch de acelaración", "Switch de arranque",
        "Boton de paro de emergencia", "Botonera de 7 vías", "Switch de encendido de la bomba de agua",
        "Relay", "Torreta de strobo color ámbar", "Conector hembra de 7 vías", "Botonera de 9 vías",
    ],
    "Sistema de agua": [
        "Kit de empaques para bombas de agua", "Abrazadera de filtro 3", "Filtros de 3\"ø para bomba",
        "Filtro de 2\"ø para bomba de agua", " Base de piston sensor bomba de agua", "Block de presión de bomba de agua",
        "Tanques de agua inferior y superior", "Tapón expandible de 2\"ø ", "Sensor de proximidad", 
    ],
    "Carrete de Manguera": [
        "Block de detección(muela de seguridad)", "Carrete de manguera de alta presión de 1\"ø x 400",
        "Soporte de carrete de manguera de alta presión ", "Empaques de cilindro de levante de carrete",
    ],
    "Válvulas y Controles": [
        "Válvula de alivio de 2\"ø ", "Actuador de válvula de mariposa",
        "Válvula de 2 vías de 1\"ø ", "Válvula de alivio de 3\"ø ",
        "Válvula de alivio de 1\ø ", "Válvula de escape de 2\"ø ",
        "Válvula de admisión de 3\" ", "Válvula de bronce de 4\"",
        "Válvula de bronce de 3\"", "Válvula de bronce de 6\""
    ],
    "Tanque y Pluma": [
        "Empaque de compuerta de azolve", "Codo de 70"
    ],
    "Manguera y Tuberias": [
        "Sellos para tubos de succión", "Punta corona de 8\"ø ",
        "Tubo de extensión de 8\" ø x 1.50m", "Manguera plana de 6\"ø",
        "Tubo de succión de punta corona de 1\"ø x 1 metro", "Codo de 45\" x  8\"ø",
        "Manguera tipo Kanaflex de 8\"ø ", "Guía de manguera cola de tigre", "Codo de ciclon de turbina",
        "Brida de 8\"ø "
    ],
    "Toberas": [
        "Boquilla de Lavado", "Tobera tipo probe", "Tobera tipo wedge", "Tobera tipo pipe wolf", 
        "Tobera tipo granada", "Tobera tipo commandor", "Tobera tipo power cleaner", "Tobera de penetración eg",
        "Tobera mad flusher", "Tobera tipo cruiser", "Tobera tipo chisel point wedge", "Tobera corta raíz",
        "Tobera sanitaria", "Tobera arenera", "Tobera de penetración", "Tobera tipo thunder", "Tobera tormenta de 1\"ø ",

    ],
    "Accesorios y Consumibles": [
        "Abrazadera rápida de 8\ø", "Empaque de codo giratorio de 1\"",
        "Abrazadera de 6\"", "Abrazaderaa de 8\"", "Abrazadera rapida rey de 8\" ",
        "Tapón de cople fluido", "Cadena de catarina de giro de carrete ", "Vacoumetro de -30 a 3 in/hg",
        "Manómetro de filtro hidrahulico", "Cono de 10\"ø", "Caja de herramientas", "Codo giratorio de 1 1/4\"ø",
        "Codo giratorio 1 1/4\"", "Codo giratorio de 90° 1\"ø", "Codo giratorio de 90° 3/4\"", "Segmento de sello de pluma",
        "Empaques de codo giratorio de 3/4\"", "Kit de sellos de brazo izquierda/derecha", "Kit de sellos de extraccion/retracción de carrete de manguera", 
    ]
}
def ejecutar_carga():
    print("Iniciando carga de catalogo en MySQL")
    total_productos = 0

    for cat_nombre, lista_prods in DATOS_CATALOGO.items():
        categoria_obj, _ = Categoria.objects.get_or_create(nombre=cat_nombre)
        print(f"\n Categoria: {cat_nombre}")

        for idx, prod_nombre in enumerate(lista_prods, start=1):
            prefix = cat_nombre[:3].upper()
            sku = f"ECO-{prefix}-{idx:03d}"

            producto, creado = Producto.objects.get_or_create(
                codigo_sku=sku,
                defaults={
                    'nombre': prod_nombre,
                    'categoria': categoria_obj,
                    'precio_base':0.00,
                    'stock': 10,
                    'disponible': True,
                    'descripcion': f"Refacción Ecodren original: {prod_nombre}"
                }
            )
            if creado:
                print(f"└─ [+] Registrado: [{sku}] {prod_nombre}")
                total_productos += 1

            else: 
                print(f"└─ [=] Ya existía: [{sku}] {prod_nombre}")
    print(f"\n ¡Proceso terminado! Se insertaron {total_productos} productos en MySQL.")
if __name__ == '__main__':
    ejecutar_carga()