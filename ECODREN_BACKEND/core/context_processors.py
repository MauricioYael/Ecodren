from .models import PerfilEmpresa

def tema_usuario(request):
    if request.user.is_authenticated:
        perfil, _ = PerfilEmpresa.objects.get_or_create(user=request.user)
        return {'tema_preferido': perfil.tema_preferido}
    return {'tema_preferido': 'claro'}