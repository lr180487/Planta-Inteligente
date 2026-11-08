"""Worker Celery: `celery -A app.worker worker --loglevel=info`.

Las mismas funciones se reutilizan en modo QStash/local desde main.py.
"""
from celery import Celery

from . import config
from .notify import notificar

app = Celery("planta", broker=config.CELERY_BROKER_URL or "redis://localhost:6379/0",
             backend=config.CELERY_BROKER_URL or "redis://localhost:6379/0")


@app.task(name="planta.notificar")
def tarea_notificar(asunto, mensaje):
    return notificar(asunto, mensaje)


@app.task(name="planta.procesar_lectura")
def tarea_procesar_lectura(dispositivo, temperatura):
    if temperatura is not None and temperatura > config.UMBRAL_TEMP:
        return notificar("🚨 Alarma de temperatura",
                         f"{dispositivo}: {temperatura} °C supera el umbral de {config.UMBRAL_TEMP} °C.")
    return {"ok": True}
