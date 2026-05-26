from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Ficha',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('archivo', models.FileField(upload_to='uploads/%Y/%m/')),
                ('nombre', models.CharField(max_length=255)),
                ('paginas', models.PositiveSmallIntegerField(default=1)),
                ('estado', models.CharField(choices=[('pendiente','Pendiente'),('procesando','Procesando'),('revisado','Revisado'),('error','Error')], default='pendiente', max_length=20)),
                ('ocr_backend', models.CharField(default='claude', max_length=20)),
                ('ocr_texto', models.TextField(blank=True, help_text='Texto crudo extraído por OCR')),
                ('error_msg', models.TextField(blank=True)),
                ('creado', models.DateTimeField(default=django.utils.timezone.now)),
                ('procesado', models.DateTimeField(blank=True, null=True)),
                ('propietario', models.CharField(blank=True, max_length=200)),
                ('telefono', models.CharField(blank=True, max_length=50)),
                ('paciente', models.CharField(blank=True, max_length=100, verbose_name='Nombre animal')),
                ('especie_raza', models.CharField(blank=True, max_length=150)),
                ('sexo', models.CharField(blank=True, max_length=30)),
                ('edad', models.CharField(blank=True, max_length=50)),
                ('peso_actual_kg', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('peso_ideal_kg', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('fecha_consulta', models.CharField(blank=True, max_length=20)),
                ('motivo_consulta', models.TextField(blank=True)),
                ('diagnostico', models.TextField(blank=True)),
                ('analisis_clinicos', models.TextField(blank=True)),
                ('rer_kcal', models.DecimalField(blank=True, decimal_places=1, max_digits=8, null=True, verbose_name='RER (kcal/día)')),
                ('red_kcal', models.DecimalField(blank=True, decimal_places=1, max_digits=8, null=True, verbose_name='RED (kcal/día)')),
                ('factor_red', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True)),
                ('pb_min_g', models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True, verbose_name='PB mín (g)')),
                ('pb_max_g', models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True, verbose_name='PB máx (g)')),
                ('ee_min_g', models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True, verbose_name='EE mín (g)')),
                ('ee_max_g', models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True, verbose_name='EE máx (g)')),
                ('co_g', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True, verbose_name='Co (g)')),
                ('p_g', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True, verbose_name='P (g)')),
                ('dieta_detalle', models.TextField(blank=True)),
                ('comidas_por_dia', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('suplementos', models.TextField(blank=True)),
                ('control_dias', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('notas_adicionales', models.TextField(blank=True)),
            ],
            options={'ordering': ['-creado'], 'verbose_name': 'Ficha clínica', 'verbose_name_plural': 'Fichas clínicas'},
        ),
    ]
