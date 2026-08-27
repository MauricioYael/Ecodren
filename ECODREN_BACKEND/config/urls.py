from django.contrib import admin
from django.urls import path, include  # 👈 include importado
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
    path('api/crear-pedido/', views.registrar_pedido_checkout, name='crear_pedido'),

    #endpoint de cotizacion
    path('api/enviar-cotizacion/', views.enviar_cotizacion, name='enviar_cotizacion'),
    
    # Rutas de autenticación (allauth)
    path('accounts/', include('allauth.urls')),
]

# Servir archivos subidos por el usuario en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)