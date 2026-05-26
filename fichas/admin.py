from django.contrib import admin
from .models import Ficha


@admin.register(Ficha)
class FichaAdmin(admin.ModelAdmin):
    list_display  = ['id', 'paciente', 'propietario', 'especie_raza', 'peso_actual_kg',
                     'rer_kcal', 'red_kcal', 'estado', 'creado']
    list_filter   = ['estado', 'ocr_backend', 'creado']
    search_fields = ['propietario', 'paciente', 'especie_raza', 'diagnostico']
    readonly_fields = ['creado', 'procesado', 'ocr_texto', 'ocr_backend', 'paginas', 'error_msg']
    fieldsets = [
        ('Archivo',         {'fields': ['nombre', 'archivo', 'paginas', 'estado', 'ocr_backend', 'error_msg', 'creado', 'procesado']}),
        ('Propietario',     {'fields': ['propietario', 'telefono']}),
        ('Paciente',        {'fields': ['paciente', 'especie_raza', 'sexo', 'edad', 'peso_actual_kg', 'peso_ideal_kg']}),
        ('Consulta',        {'fields': ['fecha_consulta', 'motivo_consulta', 'diagnostico', 'analisis_clinicos']}),
        ('Nutrición',       {'fields': ['rer_kcal', 'red_kcal', 'factor_red', 'pb_min_g', 'pb_max_g', 'ee_min_g', 'ee_max_g', 'co_g', 'p_g']}),
        ('Dieta',           {'fields': ['dieta_detalle', 'comidas_por_dia', 'suplementos']}),
        ('Seguimiento',     {'fields': ['control_dias', 'notas_adicionales']}),
        ('OCR crudo',       {'fields': ['ocr_texto'], 'classes': ['collapse']}),
    ]
