# Despliegue

## Local (todo en uno)

```bash
cd planta-backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

FastAPI sirve la API y el frontend en el mismo puerto: no hace falta
ningún otro servidor ni configurar CORS.

## Con servicios reales

1. **Postgres**: crea la base y define `DATABASE_URL`.
2. **Upstash**: crea la base Redis y copia la URL REST y el token.
3. **Celery**: levanta Redis, define `CELERY_BROKER_URL` y arranca
   `celery -A app.worker worker --loglevel=info`.
   Sin servidor propio para el worker, usa **QStash** apuntando a tu
   URL pública `/api/tareas/qstash`.
4. **Avisos**: completa `GMAIL_*` y/o `TELEGRAM_*` (ver NOTIFICACIONES.md).
5. Verifica en `GET /api/salud` que cada capa reporta su servicio
   principal y no el respaldo.

## Variables de entorno

Ver `.env.ejemplo`: todas son opcionales; sin ellas el sistema corre
100 % local (SQLite + LRU + tareas en hilo + avisos simulados).
