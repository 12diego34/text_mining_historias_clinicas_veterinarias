import csv
import threading
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator

from .models import Ficha
from .forms import UploadForm, FichaEditForm
from .ocr_service import procesar_ficha


# ── Helpers ────────────────────────────────────────────────────────────────────

def _procesar_en_hilo(ficha_id: int):
    """Corre el OCR en un thread separado para no bloquear el request."""
    from django.db import connection
    try:
        ficha = Ficha.objects.get(pk=ficha_id)
        procesar_ficha(ficha)
    finally:
        connection.close()


# ── Vistas ─────────────────────────────────────────────────────────────────────

def health(request):
    """Healthcheck público para Railway (sin login)."""
    return HttpResponse('ok', content_type='text/plain')


@login_required
def index(request):
    """Dashboard principal con lista de fichas y filtros."""
    qs = Ficha.objects.all()

    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(propietario__icontains=q) |
            Q(paciente__icontains=q) |
            Q(especie_raza__icontains=q) |
            Q(diagnostico__icontains=q)
        )

    estado = request.GET.get('estado', '')
    if estado:
        qs = qs.filter(estado=estado)

    paginator = Paginator(qs, 25)
    page = paginator.get_page(request.GET.get('page'))

    stats = {
        'total':      Ficha.objects.count(),
        'revisadas':  Ficha.objects.filter(estado=Ficha.Estado.REVISADO).count(),
        'pendientes': Ficha.objects.filter(estado__in=[Ficha.Estado.PENDIENTE, Ficha.Estado.PROCESANDO]).count(),
        'errores':    Ficha.objects.filter(estado=Ficha.Estado.ERROR).count(),
    }

    return render(request, 'fichas/index.html', {
        'page': page,
        'stats': stats,
        'q': q,
        'estado_filtro': estado,
        'estados': Ficha.Estado.choices,
        'upload_form': UploadForm(),
    })


@login_required
def upload(request):
    """Recibe uno o más archivos, los guarda y dispara el OCR en background."""
    if request.method != 'POST':
        return redirect('index')

    archivos = request.FILES.getlist('archivos')
    if not archivos:
        messages.error(request, 'No se recibieron archivos.')
        return redirect('index')

    creadas = []
    for f in archivos:
        ficha = Ficha.objects.create(nombre=f.name, archivo=f)
        creadas.append(ficha)
        t = threading.Thread(target=_procesar_en_hilo, args=(ficha.pk,), daemon=True)
        t.start()

    messages.success(request, f'{len(creadas)} ficha(s) subidas. El OCR corre en background — refrescá en unos segundos.')
    return redirect('index')


@login_required
def detalle(request, pk):
    """Ver y editar los campos de una ficha."""
    ficha = get_object_or_404(Ficha, pk=pk)

    if request.method == 'POST':
        form = FichaEditForm(request.POST, instance=ficha)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cambios guardados.')
            return redirect('detalle', pk=pk)
    else:
        form = FichaEditForm(instance=ficha)

    return render(request, 'fichas/detalle.html', {'ficha': ficha, 'form': form})


@login_required
def reprocesar(request, pk):
    """Vuelve a correr el OCR sobre una ficha (útil si falló o querés actualizar)."""
    ficha = get_object_or_404(Ficha, pk=pk)
    ficha.estado = Ficha.Estado.PENDIENTE
    ficha.error_msg = ''
    ficha.save(update_fields=['estado', 'error_msg'])
    t = threading.Thread(target=_procesar_en_hilo, args=(ficha.pk,), daemon=True)
    t.start()
    messages.info(request, f'Reprocesando "{ficha.nombre}"...')
    return redirect('detalle', pk=pk)


@login_required
def estado_json(request, pk):
    """Endpoint AJAX para polling del estado de procesamiento."""
    ficha = get_object_or_404(Ficha, pk=pk)
    return JsonResponse({
        'estado':   ficha.estado,
        'paciente': ficha.paciente,
        'error':    ficha.error_msg,
    })


@login_required
def exportar_csv(request):
    """Exporta todas las fichas (o las filtradas) a CSV."""
    qs = Ficha.objects.all()

    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(propietario__icontains=q) | Q(paciente__icontains=q) |
            Q(especie_raza__icontains=q) | Q(diagnostico__icontains=q)
        )
    estado = request.GET.get('estado', '')
    if estado:
        qs = qs.filter(estado=estado)

    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="fichas_veterinarias.csv"'

    writer = csv.writer(response)
    headers = [
        'ID', 'Archivo', 'Estado', 'Propietario', 'Teléfono',
        'Paciente', 'Especie/Raza', 'Sexo', 'Edad',
        'Peso actual (kg)', 'Peso ideal (kg)', 'Fecha consulta',
        'Motivo', 'Diagnóstico', 'Análisis clínicos',
        'RER (kcal)', 'RED (kcal)', 'Factor RED',
        'PB mín (g)', 'PB máx (g)', 'EE mín (g)', 'EE máx (g)', 'Co (g)', 'P (g)',
        'Dieta detalle', 'Comidas/día', 'Suplementos',
        'Control (días)', 'Notas', 'Creado', 'Procesado',
    ]
    writer.writerow(headers)

    for f in qs:
        writer.writerow([
            f.id, f.nombre, f.get_estado_display(), f.propietario, f.telefono,
            f.paciente, f.especie_raza, f.sexo, f.edad,
            f.peso_actual_kg, f.peso_ideal_kg, f.fecha_consulta,
            f.motivo_consulta, f.diagnostico, f.analisis_clinicos,
            f.rer_kcal, f.red_kcal, f.factor_red,
            f.pb_min_g, f.pb_max_g, f.ee_min_g, f.ee_max_g, f.co_g, f.p_g,
            f.dieta_detalle, f.comidas_por_dia, f.suplementos,
            f.control_dias, f.notas_adicionales,
            f.creado.strftime('%d/%m/%Y %H:%M') if f.creado else '',
            f.procesado.strftime('%d/%m/%Y %H:%M') if f.procesado else '',
        ])

    return response


@login_required
def eliminar(request, pk):
    """Elimina una ficha (POST only)."""
    if request.method == 'POST':
        ficha = get_object_or_404(Ficha, pk=pk)
        nombre = ficha.nombre
        ficha.archivo.delete(save=False)
        ficha.delete()
        messages.success(request, f'"{nombre}" eliminada.')
    return redirect('index')
