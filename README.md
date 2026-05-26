# Fichas Veterinarias — OCR + DB

App Django para digitalizar fichas clínicas veterinarias manuscritas.
Sube PDFs/imágenes → OCR automático (Claude o Ollama) → guarda en SQLite → exporta CSV.

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
