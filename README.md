# 🐾 Fichas Veterinarias

Una veterinaria atiende decenas de pacientes por semana. Cada consulta termina en una ficha manuscrita: el nombre del animal, su peso, los análisis de sangre, los cálculos de RER y RED, la dieta indicada con gramajes exactos, los suplementos, la fecha del próximo control. Esa información existe, pero está atrapada en papel.

Este proyecto la libera.

---

## El problema

Las fichas clínicas veterinarias manuscritas son difíciles de sistematizar. Tienen estructura variable, abreviaturas específicas del campo (RER, RED, PB, EE, Hto, GPT, GOT), números dispersos entre texto, y letra que varía de profesional en profesional. Las soluciones tradicionales de OCR —Tesseract, por ejemplo— fallan con manuscritos. Transcribir a mano es lento y propenso a errores.

El resultado es que los datos existen pero no se pueden analizar: no hay manera fácil de saber cuántos pacientes tienen sobrepeso, qué dietas se prescriben más, o cuándo vence el próximo control de cada animal.

---

## La solución

Una aplicación web que toma un PDF escaneado de una ficha veterinaria y devuelve los datos estructurados en una base de datos, listos para consultar, exportar y analizar.

El flujo completo:

**1. El usuario sube la ficha** — arrastrando el PDF al dashboard o seleccionando varios archivos de una vez. La app acepta PDFs de múltiples páginas e imágenes JPG/PNG.

**2. El OCR corre en background** — sin bloquear la interfaz. La ficha aparece en la lista con estado "procesando" y cambia a "listo" en segundos, sin necesidad de recargar la página.

**3. Claude Vision lee el manuscrito** — no como un OCR tradicional que transcribe caracteres, sino como un lector que entiende el contexto. Sabe que "3,5 x 1,2 = 195" es un cálculo de RED, que "Hto 53 GB 3600" son valores de hemograma, que "350g pollo + 200g batata + 15g aceite" es una prescripción dietaria. Extrae 27 campos estructurados de cada ficha.

**4. El profesional revisa** — ve la imagen original al lado del formulario con los datos extraídos. Corrige lo que el OCR no leyó bien. Guarda. Los datos quedan en la base de datos.

**5. Los datos se pueden exportar** — en cualquier momento, un botón descarga todas las fichas (o las filtradas por búsqueda) como CSV compatible con Excel.

---

## Qué información extrae de cada ficha

De una ficha típica como esta:

```
ADRIANA BARRACO          12/5/25
ROGER — pastor australiano ♂ 4 años — 19,7kg
bajo peso (alérgico a BDF)
Hto 53  GB 3600  Ur 44  GPT 70  GOT 64  FAS 30  Co 7,66
RED: 24 x 1,8 = 1366 kcal
PB: 50,96–81,32   EE: 19,5–114   Co 1,41   P 1,08
460g carne + 250g verdura + 350g fideos + 20g aceite
+ 2 TTD + 15g yogur
Control 30d. Pesar en 15d.
```

La app construye automáticamente este registro:

| Campo | Valor extraído |
|-------|---------------|
| Propietario | Barraco, Adriana |
| Paciente | Roger |
| Especie / Raza | Canino, Pastor Australiano |
| Sexo | Macho |
| Edad | 4 años |
| Peso actual | 19,7 kg |
| Fecha de consulta | 12/05/25 |
| Motivo | Bajo peso, alérgico a BDF |
| Análisis clínicos | Hto 53, GB 3600, Ur 44, GPT 70, GOT 64, FAS 30, Co 7,66 |
| RED | 1366 kcal/día |
| Factor RED | 1,8 |
| PB mín / máx | 50,96 — 81,32 g |
| EE mín / máx | 19,5 — 114 g |
| Co | 1,41 g |
| P | 1,08 g |
| Dieta | 460g carne + 250g verdura + 350g fideos + 20g aceite + 2 TTD + 15g yogur |
| Suplementos | TTD, Co |
| Control | 30 días |
| Notas | Pesar en 15 días |

---

## Lo que el profesional puede hacer con esos datos

Una vez que las fichas están digitalizadas:

- **Buscar** por propietario, paciente, especie o diagnóstico
- **Filtrar** por estado de procesamiento
- **Corregir** cualquier campo desde la interfaz, con la imagen original visible al lado
- **Exportar** todo a CSV para análisis en Excel, Google Sheets o cualquier herramienta estadística
- **Acceder al historial** de cada paciente desde cualquier dispositivo con browser
- **Volver a procesar** fichas que fallaron o que quieran re-analizar

Lo que antes requería transcripción manual ahora tarda segundos por ficha.

---

## El backend de OCR es intercambiable

La app soporta dos motores de extracción:

**Claude Vision (Anthropic)** — es la opción por defecto y la más precisa para este tipo de documento. Entiende el español médico-veterinario, maneja la variabilidad de la letra manuscrita, y reconoce los cálculos y abreviaturas propias del campo. El costo es aproximadamente $8–12 USD para procesar 800 fichas con el modelo Sonnet.

**Ollama (local)** — para quien tenga GPUs disponibles y prefiera no depender de una API externa. Corre completamente en la infraestructura propia, sin costo por request. La calidad es menor que Claude para abreviaturas clínicas específicas, pero suficiente para fichas con letra clara. Se configura con una línea en el archivo `.env`.

Cambiar de uno a otro no requiere modificar código, solo la variable `OCR_BACKEND`.

---

## Stack técnico

- **Django** como framework web y ORM
- **SQLite** en desarrollo y despliegues pequeños — **PostgreSQL** para producción a escala
- **pdf2image + poppler** para convertir PDFs a imágenes antes de enviárselas al modelo de visión
- **Whitenoise** para servir archivos estáticos sin necesidad de Nginx en deployments simples
- **Docker** para el empaquetado y deploy
- **Railway** como plataforma de hosting — incluye SSL automático con Let's Encrypt

---

## Estado del proyecto

La app procesa fichas, las almacena y las exporta. Lo que viene:

- [ ] Historial de consultas por paciente (múltiples fichas del mismo animal)
- [ ] Gráficos de evolución de peso y parámetros clínicos
- [ ] Alertas de control próximo (pacientes con control vencido)
- [ ] API REST para integración con otros sistemas
- [ ] Soporte para procesar fichas en lote desde línea de comandos

---

## Documentación técnica (repo)

Instalación local, variables de entorno, Ollama y opciones de deploy:

## Setup local (5 minutos)

```bash
# 1. Clonar / descomprimir el proyecto
cd fichas_vet

# 2. Entorno virtual
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 3. Dependencias
pip install -r requirements.txt
apt install poppler-utils -y      # Ubuntu/Debian (para PDF)
# brew install poppler            # Mac

# 4. Variables de entorno
cp .env.example .env
# Editar .env y poner tu ANTHROPIC_API_KEY

# 5. Base de datos
python manage.py migrate

# 6. Usuario admin (opcional)
python manage.py createsuperuser

# 7. Arrancar
python manage.py runserver
# → http://localhost:8000
```

## Cambiar a Ollama (gratis, local)

En `.env`:
```
OCR_BACKEND=ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2-vision:11b
```

Y en otra terminal:
```bash
ollama pull llama3.2-vision:11b
ollama serve
```

---

## Deploy gratuito / barato

### Opción A — Railway (recomendado, ~$5/mes o gratis con límites)
```bash
# Instalar Railway CLI
npm install -g @railway/cli
railway login
railway init
railway up
# Variables de entorno: configurar en el dashboard de Railway
```
- SQLite funciona bien para volúmenes pequeños/medios
- Para más de ~10k fichas, migrar a Postgres (Railway lo ofrece)

### Opción B — Fly.io (gratis para apps pequeñas)
```bash
# Instalar flyctl: https://fly.io/docs/hands-on/install-flyctl/
fly launch
fly secrets set ANTHROPIC_API_KEY=sk-ant-...
fly secrets set DJANGO_SECRET_KEY=clave-larga
fly secrets set DEBUG=False
fly deploy
```

Crear `fly.toml` mínimo:
```toml
app = "fichas-vet"
primary_region = "gru"   # São Paulo, el más cercano a Argentina

[build]
  [build.args]
    PYTHON_VERSION = "3.11"

[http_service]
  internal_port = 8000
  force_https = true

[[vm]]
  memory = "512mb"
  cpu_kind = "shared"
  cpus = 1
```

Y `Dockerfile`:
```dockerfile
FROM python:3.11-slim
RUN apt-get update && apt-get install -y poppler-utils && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN python manage.py collectstatic --noinput
CMD gunicorn fichas_vet.wsgi:application --bind 0.0.0.0:8000 --workers 2
```

### Opción C — VPS propio (Hetzner ~€4/mes, DigitalOcean ~$6/mes)
```bash
# En el servidor
git clone ... fichas_vet
cd fichas_vet
pip install -r requirements.txt
apt install poppler-utils nginx

# Variables
export ANTHROPIC_API_KEY=...
export DJANGO_SECRET_KEY=...
export DEBUG=False
export ALLOWED_HOSTS=tudominio.com

python manage.py migrate
python manage.py collectstatic

# Servir con gunicorn + nginx (ver gunicorn.conf abajo)
gunicorn fichas_vet.wsgi:application --bind 127.0.0.1:8000 --workers 2 --daemon
```

---

## Migrar de SQLite a Postgres (cuando escale)

1. En `.env` descomentar bloque `# Para producción con Postgres`
2. `pip install psycopg2-binary`
3. `python manage.py migrate`
4. Opcional: exportar datos de SQLite e importar

---

## Estructura del proyecto

```
fichas_vet/
├── fichas_vet/          # Configuración Django
│   ├── settings.py
│   └── urls.py
├── fichas/              # App principal
│   ├── models.py        # Modelo Ficha (27 campos)
│   ├── views.py         # Upload, detalle, exportar
│   ├── ocr_service.py   # Claude API + Ollama
│   ├── forms.py
│   └── admin.py
├── templates/fichas/    # HTML
├── media/uploads/       # Archivos subidos
├── db.sqlite3           # Base de datos
├── requirements.txt
└── .env
```
