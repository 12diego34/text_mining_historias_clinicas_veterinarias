"""
fichas/ocr_service.py
Servicio de OCR que soporta Claude API y Ollama.
Se llama desde la vista después de guardar el archivo.
"""
import base64
import io
import json
import re
import logging
from pathlib import Path

from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

# ── Prompt compartido ──────────────────────────────────────────────────────────

PROMPT = """Esta es una ficha clínica veterinaria manuscrita escaneada.

Extraé TODOS los datos visibles y respondé con un JSON con exactamente estas claves:
propietario, paciente, especie_raza, sexo, edad,
peso_actual_kg, peso_ideal_kg, fecha_consulta, telefono,
motivo_consulta, diagnostico, analisis_clinicos,
rer_kcal, red_kcal, factor_red,
pb_min_g, pb_max_g, ee_min_g, ee_max_g, co_g, p_g,
dieta_detalle, comidas_por_dia, suplementos, control_dias, notas_adicionales

Reglas:
- Si un dato no aparece: null
- Campos numéricos (pesos, rer, red, gramos): solo el número sin unidades
- dieta_detalle: transcribí TODOS los alimentos con sus cantidades
- analisis_clinicos: incluí TODOS los valores de laboratorio
- Respondé ÚNICAMENTE con el JSON válido, sin markdown, sin texto extra."""


def _limpiar_json(raw: str) -> str:
    raw = raw.strip()
    raw = re.sub(r'```json|```', '', raw).strip()
    start, end = raw.find('{'), raw.rfind('}')
    if start != -1 and end > start:
        return raw[start:end + 1]
    return raw


def _pdf_a_imagenes(path: str) -> list[str]:
    """Convierte PDF a lista de JPEG base64 usando pdf2image."""
    from pdf2image import convert_from_path
    paginas = convert_from_path(path, dpi=200)
    result = []
    for pag in paginas:
        buf = io.BytesIO()
        pag.save(buf, format='JPEG', quality=90)
        result.append(base64.standard_b64encode(buf.getvalue()).decode())
    return result


def _imagen_a_b64(path: str) -> str:
    with open(path, 'rb') as f:
        return base64.standard_b64encode(f.read()).decode()


def _get_pages_b64(file_path: str) -> tuple[list[str], str]:
    """Retorna (lista_b64, media_type)."""
    ext = Path(file_path).suffix.lower()
    if ext == '.pdf':
        return _pdf_a_imagenes(file_path), 'image/jpeg'
    media = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg',
             'png': 'image/png', 'webp': 'image/webp'}.get(ext.lstrip('.'), 'image/jpeg')
    return [_imagen_a_b64(file_path)], media


# ── Backend Claude ─────────────────────────────────────────────────────────────

def _ocr_claude(pages_b64: list[str], media_type: str) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_KEY)

    content = [
        {'type': 'image', 'source': {'type': 'base64', 'media_type': media_type, 'data': p}}
        for p in pages_b64
    ]
    content.append({'type': 'text', 'text': PROMPT})

    resp = client.messages.create(
        model=settings.CLAUDE_MODEL,
        max_tokens=1500,
        messages=[{'role': 'user', 'content': content}]
    )
    return resp.content[0].text


# ── Backend Ollama ─────────────────────────────────────────────────────────────

def _ocr_ollama(pages_b64: list[str]) -> str:
    import ollama
    client = ollama.Client(host=settings.OLLAMA_HOST)

    if len(pages_b64) == 1:
        resp = client.chat(
            model=settings.OLLAMA_MODEL,
            messages=[{'role': 'user', 'content': PROMPT, 'images': pages_b64}]
        )
        return resp['message']['content']

    # Múltiples páginas: merge de resultados
    partes = []
    for i, b64 in enumerate(pages_b64):
        prompt = PROMPT if i == 0 else f'Página {i+1} de la misma ficha. ' + PROMPT
        resp = client.chat(
            model=settings.OLLAMA_MODEL,
            messages=[{'role': 'user', 'content': prompt, 'images': [b64]}]
        )
        partes.append(resp['message']['content'])

    # Tomar el JSON de la página 1 y completar con las demás
    base = json.loads(_limpiar_json(partes[0]))
    for parte in partes[1:]:
        try:
            extra = json.loads(_limpiar_json(parte))
            for k, v in extra.items():
                if v is not None and base.get(k) is None:
                    base[k] = v
                elif k in ('dieta_detalle', 'analisis_clinicos', 'notas_adicionales'):
                    if v and base.get(k):
                        base[k] = str(base[k]) + ' | ' + str(v)
        except Exception:
            pass
    return json.dumps(base)


# ── Función principal ──────────────────────────────────────────────────────────

def procesar_ficha(ficha) -> None:
    """
    Procesa una instancia de Ficha:
    1. Convierte el archivo a imágenes
    2. Llama al backend OCR configurado
    3. Parsea el JSON y guarda los campos en la DB
    """
    from fichas.models import Ficha as FichaModel

    ficha.estado = FichaModel.Estado.PROCESANDO
    ficha.save(update_fields=['estado'])

    try:
        file_path = ficha.archivo.path
        pages_b64, media_type = _get_pages_b64(file_path)
        ficha.paginas = len(pages_b64)

        backend = settings.OCR_BACKEND.lower()

        if backend == 'claude':
            raw = _ocr_claude(pages_b64, media_type)
        elif backend == 'ollama':
            raw = _ocr_ollama(pages_b64)
        else:
            raise ValueError(f'OCR_BACKEND desconocido: {backend}')

        ficha.ocr_texto = raw
        data = json.loads(_limpiar_json(raw))

        ficha.aplicar_json(data)
        ficha.estado     = FichaModel.Estado.REVISADO
        ficha.ocr_backend = backend
        ficha.procesado  = timezone.now()
        ficha.error_msg  = ''

        logger.info(f'Ficha {ficha.id} procesada OK con {backend} ({len(pages_b64)} pág.)')

    except Exception as exc:
        ficha.estado    = FichaModel.Estado.ERROR
        ficha.error_msg = str(exc)
        logger.exception(f'Error procesando ficha {ficha.id}: {exc}')

    ficha.save()
