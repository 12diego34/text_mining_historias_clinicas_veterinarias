from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'dev-key-cambiar-en-produccion-xk392')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

_allowed = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
_railway_domain = os.environ.get('RAILWAY_PUBLIC_DOMAIN', '').strip()
# Railway app URLs are *.up.railway.app — ".railway.app" alone does not match them.
for _host in (_railway_domain, 'healthcheck.railway.app', '.up.railway.app'):
    if _host and _host not in _allowed:
        _allowed.append(_host)
ALLOWED_HOSTS = [h.strip() for h in _allowed if h.strip()]

_csrf = [o.strip() for o in os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',') if o.strip()]
if _railway_domain:
    _csrf.append(f'https://{_railway_domain}')
for _host in ALLOWED_HOSTS:
    if _host and not _host.startswith('.'):
        _origin = f'https://{_host}'
        if _origin not in _csrf:
            _csrf.append(_origin)
CSRF_TRUSTED_ORIGINS = _csrf

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'fichas',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'fichas_vet.urls'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / 'templates'],
    'APP_DIRS': True,
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.debug',
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
    ]},
}]

WSGI_APPLICATION = 'fichas_vet.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Para migrar a Postgres cuando quieras, descomentar y completar:
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': os.environ.get('DB_NAME', 'fichas_vet'),
#         'USER': os.environ.get('DB_USER', 'postgres'),
#         'PASSWORD': os.environ.get('DB_PASSWORD', ''),
#         'HOST': os.environ.get('DB_HOST', 'localhost'),
#         'PORT': os.environ.get('DB_PORT', '5432'),
#     }
# }

LANGUAGE_CODE = 'es-ar'
TIME_ZONE = 'America/Argentina/Buenos_Aires'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# OCR backend: 'claude' o 'ollama'
OCR_BACKEND    = os.environ.get('OCR_BACKEND', 'claude')
ANTHROPIC_KEY  = os.environ.get('ANTHROPIC_API_KEY', '')
CLAUDE_MODEL   = os.environ.get('CLAUDE_MODEL', 'claude-sonnet-4-5')
OLLAMA_HOST    = os.environ.get('OLLAMA_HOST', 'http://localhost:11434')
OLLAMA_MODEL   = os.environ.get('OLLAMA_MODEL', 'llama3.2-vision:11b')

FILE_UPLOAD_MAX_MEMORY_SIZE = 20 * 1024 * 1024   # 20 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 20 * 1024 * 1024
