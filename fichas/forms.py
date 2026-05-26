from django import forms
from .models import Ficha


class MultiFileInput(forms.FileInput):
    """FileInput que acepta multiple=True en Django 4-6."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs.setdefault("multiple", True)

    class Media:
        pass


class UploadForm(forms.Form):
    archivos = forms.FileField(
        widget=MultiFileInput(attrs={"accept": ".pdf,.jpg,.jpeg,.png,.webp"}),
        label="Fichas (PDF, JPG, PNG)",
        help_text="Podés seleccionar múltiples archivos a la vez.",
        required=False,
    )


class FichaEditForm(forms.ModelForm):
    class Meta:
        model = Ficha
        fields = [
            "propietario", "telefono",
            "paciente", "especie_raza", "sexo", "edad",
            "peso_actual_kg", "peso_ideal_kg", "fecha_consulta",
            "motivo_consulta", "diagnostico", "analisis_clinicos",
            "rer_kcal", "red_kcal", "factor_red",
            "pb_min_g", "pb_max_g", "ee_min_g", "ee_max_g", "co_g", "p_g",
            "dieta_detalle", "comidas_por_dia", "suplementos",
            "control_dias", "notas_adicionales", "estado",
        ]
        widgets = {
            "motivo_consulta":   forms.Textarea(attrs={"rows": 3}),
            "diagnostico":       forms.Textarea(attrs={"rows": 2}),
            "analisis_clinicos": forms.Textarea(attrs={"rows": 3}),
            "dieta_detalle":     forms.Textarea(attrs={"rows": 4}),
            "suplementos":       forms.Textarea(attrs={"rows": 2}),
            "notas_adicionales": forms.Textarea(attrs={"rows": 2}),
        }
