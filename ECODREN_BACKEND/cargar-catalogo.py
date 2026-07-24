import os
import django

os.environ.setdefault('DJANGO_SETTING_MODULE', 'config.settings')
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
        "Válvula de alivio de 2\"ø ", "Actuador de válvula de mariposa"
    ]
}