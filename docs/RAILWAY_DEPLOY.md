# Deploy en Railway

Repositorio: [12diego34/text_mining_historias_clinicas_veterinarias](https://github.com/12diego34/text_mining_historias_clinicas_veterinarias)

## 1. Crear proyecto

1. Entrá a [railway.app](https://railway.app) e iniciá sesión con **GitHub** (cuenta `12diego34`).
2. **New Project** → **Deploy from GitHub repo**.
3. Elegí `text_mining_historias_clinicas_veterinarias`.
4. Railway detecta el `Dockerfile` y `railway.toml` automáticamente.

## 2. Variables de entorno

En el servicio → **Variables**, agregá:

| Variable | Valor | Notas |
|----------|-------|-------|
| `DJANGO_SECRET_KEY` | clave larga aleatoria | Generá una con `python -c "import secrets; print(secrets.token_urlsafe(50))"` |
| `DEBUG` | `False` | Obligatorio en producción |
| `OCR_BACKEND` | `claude` | o `ollama` si tenés otro servicio |
| `ANTHROPIC_API_KEY` | `sk-ant-...` | Solo si `OCR_BACKEND=claude` |
| `CLAUDE_MODEL` | `claude-sonnet-4-5` | Opcional |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1,.railway.app` | Railway también setea `RAILWAY_PUBLIC_DOMAIN` |

`RAILWAY_PUBLIC_DOMAIN` lo inyecta Railway solo; no hace falta copiarlo a mano.

## 3. Dominio público

1. En el servicio → **Settings** → **Networking** → **Generate Domain**.
2. Copiá la URL (ej. `https://text-mining-xxx.up.railway.app`).
3. Opcional: pegala en el **About** del repo en GitHub.

## 4. Verificar deploy

- Los logs deben mostrar `migrate` en **pre-deploy** y luego `gunicorn` escuchando en el puerto que define Railway (`$PORT`). El `startCommand` va envuelto en `sh -c` para que `$PORT` no quede como texto literal en deploys con Dockerfile.
- Abrí la URL pública: deberías ver el dashboard de fichas.
- Healthcheck: `GET /` (configurado en `railway.toml`).

## 5. Limitaciones en Railway (importante)

- **SQLite y archivos subidos** viven en el disco del contenedor. Si el servicio se redeploya o reinicia, **podés perder datos**. Para producción seria conviene Postgres + volumen o almacenamiento externo (S3).
- **Ollama local** no corre en Railway sin un servicio aparte; usá `OCR_BACKEND=claude` en este deploy.

## 6. CLI (opcional)

```powershell
scoop install railway
railway login
cd fichas_vet
railway link
railway up
```

O desde el dashboard: cada push a `main` redeploya automáticamente si tenés GitHub conectado.
