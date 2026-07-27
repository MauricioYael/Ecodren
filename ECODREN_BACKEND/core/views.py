from django.shortcuts import render
from .models import Categoria, Producto

def index(request):
    return render(request, 'index.html')

def tienda(request):
    categorias = Categoria.objects.all()
    productos = Producto.objects.filter(disponible=True)

    context = {
        'categorias': categorias,
        'productos': productos,
    }
    return render(request, 'tienda.html', context)