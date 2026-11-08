"""Tareas en segundo plano: Celery -> QStash -> ejecución local (respaldo).

- Si CELERY_BROKER_URL responde, se encola en Celery (ver worker.py).
- Si no, pero hay QSTASH_TOKEN y QSTASH_DESTINO, se publica con QStash.
- Si tampoco, la tarea se ejecuta al momento en un hilo (modo local/demo).
"""
import threading

import httpx

from . import config

MODO = "local"


def _celery_disponible():
    if not config.CELERY_BROKER_URL:
        return False
    try:
        from celery import Celery
        app = Celery("planta_check", broker=config.CELERY_BROKER_URL)
        with app.connection_for_read() as conn:
            conn.ensure_connection(max_retries=0, timeout=2)
        return True
    except Exception:
        return False


if _celery_disponible():
    MODO = "celery"
elif config.QSTASH_TOKEN and config.QSTASH_DESTINO:
    MODO = "qstash"


def enviar_tarea(nombre, funcion, *args, **kwargs):
    """Encola `funcion` según el modo disponible. Devuelve el modo usado."""
    if MODO == "celery":
        from .worker import app as celery_app
        celery_app.send_task(f"planta.{nombre}", args=args, kwargs=kwargs)
        return "celery"
    if MODO == "qstash":
        try:
            httpx.post(
                f"https://qstash.upstash.io/v2/publish/{config.QSTASH_DESTINO}",
                headers={"Authorization": f"Bearer {config.QSTASH_TOKEN}"},
                json={"tarea": nombre, "args": args, "kwargs": kwargs}, timeout=5)
            return "qstash"
        except Exception:
            pass  # cae a local
    threading.Thread(target=funcion, args=args, kwargs=kwargs, daemon=True).start()
    return "local"
