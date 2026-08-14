from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='home'),
    path('tienda/', views.tienda, name='tienda'),
    path('maquinaria/', views.maquinaria, name='maquinaria'),
    path('recursos/', views.recursos, name='recursos'),
    path('publicaciones', views.publicaciones, name='publicaciones'),
    path('capacitaciones/', views.capacitaciones, name='capacitaciones'),
    path('perfil/', views.perfil_view, name='perfil')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
