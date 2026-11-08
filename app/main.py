"""Backend FastAPI de Planta Inteligente — punto de entrada.

Solo crea la aplicación, registra las rutas (app/routers/) y sirve el
frontend (HTML) en / desde el mismo origen, para que la sincronización
funcione sin configurar CORS en el navegador. La lógica vive en
app/servicios/ y los modelos de datos en app/schemas.py.

Respaldo en cada capa:
  BD:      Postgres -> SQLite
  Caché:   Upstash  -> LRU en memoria
  Worker:  Celery   -> QStash -> ejecución local
  Avisos:  Gmail / Telegram reales si hay credenciales; si no, simulados.
"""
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .routers import (alertas, asistente, dispositivos, documentos,
                      lecturas, notificaciones, plc, sistema)

app = FastAPI(title="Planta Inteligente API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"],
                   allow_headers=["*"])

# ----------------------------- API -----------------------------
for _r in (sistema, lecturas, dispositivos, notificaciones, asistente,
           documentos, plc, alertas):
    app.include_router(_r.router)

# ----------------------------- frontend -----------------------------
FRONT = os.path.join(os.path.dirname(__file__), "..", "..", "planta-backend")
app.mount("/", StaticFiles(directory=FRONT, html=True), name="frontend")
