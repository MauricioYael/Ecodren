from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views


urlpatterns = [
    path('admin/', admin.site.urls),

    # Vistas Principales (SSR)
    path('', views.index, name='home'),
    path('tienda/', views.tienda, name='tienda'),
    path('maquinaria/', views.maquinaria, name='maquinaria'),
    path('recursos/', views.recursos, name='recursos'),
    path('publicaciones/', views.publicaciones, name='publicaciones'),
    path('capacitaciones/', views.capacitaciones, name='capacitaciones'),
    path('perfil/', views.perfil_view, name='perfil'),
    path("api/actualizar-perfil/", views.actualizar_datos_perfil, name="actualizar_perfil"),
    path("api/actualizar-tema/", views.actualizar_tema, name="actualizar_tema"),
    path('api/crear-pedido/', views.registrar_pedido_checkout, name='crear_pedido'),
    path('api/preferencias/localizacion/', views.api_actualizar_localizacion, name='api_localizacion'),
    path('api/calendario-cursos/', views.api_calendario_cursos, name='api_calendario_cursos'),
    path('api/cambiar-password/', views.cambiar_password, name='cambiar_password'),
    path('api/metodos-pago/agregar/', views.agregar_metodo_pago, name='agregar_metodo_pago'),
    path('api/metodos-pago/eliminar/', views.eliminar_metodo_pago, name='eliminar_metodo_pago'),
    path('api/conekta-webhook/', views.conekta_webhook, name='conekta_webhook'),
    path('api/perfil/avatar/', views.actualizar_avatar, name='actualizar_avatar'),
    path('api/login/', views.api_login, name='api_login'),
    path('api/register/', views.api_register, name='api_register'),
    path('api/recuperar-password/', views.api_forget_password, name='api_forget_password'),
    path('api/logout/', views.api_logout, name='api_logout'),
    path('api/direccion/guardar/', views.guardar_direccion, name='guardar_direccion'),
    path('api/direccion/eliminar/', views.eliminar_direccion, name='eliminar_direccion'),

    #endpoint de cotizacion
    path('api/enviar-cotizacion/', views.enviar_cotizacion, name='enviar_cotizacion'),
    
    # Rutas de autenticación (allauth)
    path('accounts/', include('allauth.urls')),
]

# Servir archivos subidos por el usuario en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)