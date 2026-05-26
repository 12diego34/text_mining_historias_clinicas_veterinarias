from django.db import models
from django.utils import timezone


class Ficha(models.Model):

    class Estado(models.TextChoices):
        PENDIENTE   = 'pendiente',   'Pendiente'
        PROCESANDO  = 'procesando',  'Procesando'
        REVISADO    = 'revisado',    'Revisado'
        ERROR       = 'error',       'Error'

    # ── Archivo original ───────────────────────────────────────────────────────
    archivo      = models.FileField(upload_to='uploads/%Y/%m/')
    nombre       = models.CharField(max_length=255)
    paginas      = models.PositiveSmallIntegerField(default=1)
    estado       = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PENDIENTE)
    ocr_backend  = models.CharField(max_length=20, default='claude')
    ocr_texto    = models.TextField(blank=True, help_text='Texto crudo extraído por OCR')
    error_msg    = models.TextField(blank=True)
    creado       = models.DateTimeField(default=timezone.now)
    procesado    = models.DateTimeField(null=True, blank=True)

    # ── Datos del propietario ──────────────────────────────────────────────────
    propietario  = models.CharField(max_length=200, blank=True)
    telefono     = models.CharField(max_length=50,  blank=True)

    # ── Datos del paciente ─────────────────────────────────────────────────────
    paciente     = models.CharField(max_length=100, blank=True, verbose_name='Nombre animal')
    especie_raza = models.CharField(max_length=150, blank=True)
    sexo         = models.CharField(max_length=30,  blank=True)
    edad         = models.CharField(max_length=50,  blank=True)

    # ── Pesos ─────────────────────────────────────────────────────────────────
    peso_actual_kg  = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    peso_ideal_kg   = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    # ── Consulta ──────────────────────────────────────────────────────────────
    fecha_consulta   = models.CharField(max_length=20, blank=True)
    motivo_consulta  = models.TextField(blank=True)
    diagnostico      = models.TextField(blank=True)
    analisis_clinicos= models.TextField(blank=True)

    # ── Requerimientos nutricionales ──────────────────────────────────────────
    rer_kcal    = models.DecimalField(max_digits=8, decimal_places=1, null=True, blank=True, verbose_name='RER (kcal/día)')
    red_kcal    = models.DecimalField(max_digits=8, decimal_places=1, null=True, blank=True, verbose_name='RED (kcal/día)')
    factor_red  = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)

    # ── Proteína y lípidos ────────────────────────────────────────────────────
    pb_min_g    = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True, verbose_name='PB mín (g)')
    pb_max_g    = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True, verbose_name='PB máx (g)')
    ee_min_g    = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True, verbose_name='EE mín (g)')
    ee_max_g    = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True, verbose_name='EE máx (g)')
    co_g        = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='Co (g)')
    p_g         = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='P (g)')

    # ── Dieta ─────────────────────────────────────────────────────────────────
    dieta_detalle   = models.TextField(blank=True)
    comidas_por_dia = models.PositiveSmallIntegerField(null=True, blank=True)
    suplementos     = models.TextField(blank=True)

    # ── Seguimiento ───────────────────────────────────────────────────────────
    control_dias        = models.PositiveSmallIntegerField(null=True, blank=True)
    notas_adicionales   = models.TextField(blank=True)

    class Meta:
        ordering = ['-creado']
        verbose_name = 'Ficha clínica'
        verbose_name_plural = 'Fichas clínicas'

    def __str__(self):
        return f'{self.paciente or "Sin nombre"} — {self.propietario or "Sin propietario"} ({self.nombre})'

    @property
    def campos_numericos_completos(self):
        """Retorna cuántos campos numéricos clave tienen valor."""
        campos = [self.peso_actual_kg, self.rer_kcal, self.red_kcal,
                  self.pb_min_g, self.pb_max_g, self.ee_min_g, self.ee_max_g]
        return sum(1 for c in campos if c is not None)

    CAMPO_MAP = {
        'propietario':      'propietario',
        'paciente':         'paciente',
        'especie_raza':     'especie_raza',
        'sexo':             'sexo',
        'edad':             'edad',
        'peso_actual_kg':   'peso_actual_kg',
        'peso_ideal_kg':    'peso_ideal_kg',
        'fecha_consulta':   'fecha_consulta',
        'telefono':         'telefono',
        'motivo_consulta':  'motivo_consulta',
        'diagnostico':      'diagnostico',
        'analisis_clinicos':'analisis_clinicos',
        'rer_kcal':         'rer_kcal',
        'red_kcal':         'red_kcal',
        'factor_red':       'factor_red',
        'pb_min_g':         'pb_min_g',
        'pb_max_g':         'pb_max_g',
        'ee_min_g':         'ee_min_g',
        'ee_max_g':         'ee_max_g',
        'co_g':             'co_g',
        'p_g':              'p_g',
        'dieta_detalle':    'dieta_detalle',
        'comidas_por_dia':  'comidas_por_dia',
        'suplementos':      'suplementos',
        'control_dias':     'control_dias',
        'notas_adicionales':'notas_adicionales',
    }

    def aplicar_json(self, data: dict):
        """Aplica el dict extraído por OCR al modelo, convirtiendo tipos."""
        import decimal

        def to_decimal(v):
            if v is None:
                return None
            try:
                return decimal.Decimal(str(v).replace(',', '.'))
            except Exception:
                return None

        def to_int(v):
            if v is None:
                return None
            try:
                return int(float(str(v)))
            except Exception:
                return None

        campos_decimal = {'peso_actual_kg', 'peso_ideal_kg', 'rer_kcal', 'red_kcal',
                          'factor_red', 'pb_min_g', 'pb_max_g', 'ee_min_g', 'ee_max_g',
                          'co_g', 'p_g'}
        campos_int = {'comidas_por_dia', 'control_dias'}

        for json_key, model_field in self.CAMPO_MAP.items():
            val = data.get(json_key)
            if val is None:
                continue
            if model_field in campos_decimal:
                setattr(self, model_field, to_decimal(val))
            elif model_field in campos_int:
                setattr(self, model_field, to_int(val))
            else:
                setattr(self, model_field, str(val).strip()[:500] if val else '')
