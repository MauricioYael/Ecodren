from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_solicitudcotizacion'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='solicitudcotizacion',
            options={'ordering': ['-creado_en'], 'verbose_name': 'Solicitud de Cotización', 'verbose_name_plural': 'Solicitudes de Cotizaciones'},
        ),
        migrations.CreateModel(
            name='PerfilEmpresa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('razon_social', models.CharField(blank=True, default='Servicios Hidráulicos del Centro S.A.', max_length=200, null=True, verbose_name='Razón Social')),
                ('telefono_operativo', models.CharField(blank=True, default='+52 55 1234 5678', max_length=50, null=True, verbose_name='Teléfono Operativo')),
                ('direccion_principal', models.CharField(blank=True, default='Av. Central #123, Col. Industrial, C.P. 12345, Ciudad de México', max_length=300, null=True, verbose_name='Dirección de Entrega Principal')),
                ('actualizado_en', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='perfil_empresa', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Perfil de Empresa',
                'verbose_name_plural': 'Perfiles de Empresa',
            },
        ),
    ]