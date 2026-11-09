"""Punto de entrada FastAPI para AgroClima / Planta Inteligente.

Registra los routers, configura CORS, expone el health check y sirve el
frontend desde una carpeta incluida en planta-backend.

Orden de búsqueda del frontend:
1. FRONTEND_DIR (absoluta o relativa a planta-backend).
2. planta-backend/iot-plataforma (estructura indicada por el proyecto).
3. planta-backend/static (estructura alternativa para Render).
4. carpeta hermana ../iot-plataforma (compatibilidad con desarrollo local).

El montaje de archivos estáticos se registra al final para no interceptar
rutas de API ni /healthz.
"""
from __future__ import annotations

import logging
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .routers import (
    alertas,
    asistente,
    dispositivos,
    documentos,
    lecturas,
    notificaciones,
    plc,
    sistema,
)

logger = logging.getLogger("agroclima.api")

app = FastAPI(
    title="AgroClima — Gemelo Digital",
    description=(
        "API para telemetría IoT, dispositivos ESP32, OpenPLC y servicios AgroClima."
    ),
    version="1.0.2",
)

# CORS: definir CORS_ORIGINS en producción, separado por comas.
_cors_raw = os.getenv("CORS_ORIGINS", "*").strip()
_cors_origins = [item.strip() for item in _cors_raw.split(",") if item.strip()]
if not _cors_origins:
    _cors_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials="*" not in _cors_origins,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "Origin", "X-Requested-With"],
)

# Registrar routers de la API.
for router_module in (
    sistema,
    lecturas,
    dispositivos,
    notificaciones,
    asistente,
    documentos,
    plc,
    alertas,
):
    app.include_router(router_module.router)


@app.get("/healthz", tags=["Sistema"], include_in_schema=False)
async def healthz() -> dict[str, str]:
    """Health check sencillo para Render y monitorización."""
    return {"status": "ok"}


def _resolve_frontend() -> Path | None:
    """Encuentra el frontend independientemente del directorio de ejecución."""
    backend_dir = Path(__file__).resolve().parent.parent  # .../planta-backend
    project_dir = backend_dir.parent
    configured = os.getenv("FRONTEND_DIR", "").strip()

    candidates: list[Path] = []
    if configured:
        configured_path = Path(configured).expanduser()
        # Las rutas relativas se interpretan desde planta-backend, no desde cwd.
        candidates.append(
            configured_path if configured_path.is_absolute() else backend_dir / configured_path
        )

    # Estructura que el usuario confirmó: frontend dentro de planta-backend.
    candidates.extend(
        [
            backend_dir / "iot-plataforma",
            backend_dir / "static",
            project_dir / "iot-plataforma",
        ]
    )

    checked: list[str] = []
    for candidate in candidates:
        resolved = candidate.resolve()
        checked.append(str(resolved))
        if resolved.is_dir() and (resolved / "index.html").is_file():
            logger.info("Frontend encontrado en: %s", resolved)
            return resolved

    logger.warning(
        "No se encontró el frontend. La API iniciará sin interfaz web. "
        "Coloque index.html en planta-backend/iot-plataforma o configure "
        "FRONTEND_DIR. Rutas revisadas: %s",
        checked,
    )
    return None


FRONTEND_DIR = _resolve_frontend()

if FRONTEND_DIR is not None:
    # Montar '/' al final: así no oculta /docs, /healthz ni los routers API.
    app.mount(
        "/",
        StaticFiles(directory=str(FRONTEND_DIR), html=True, check_dir=True),
        name="frontend",
    )
else:
    @app.get("/", tags=["Sistema"], include_in_schema=False)
    async def root_status() -> dict[str, str]:
        """Respuesta informativa si el frontend no fue incluido en el despliegue."""
        return {
            "name": "AgroClima — Gemelo Digital API",
            "status": "ok",
            "message": "API activa. Consulta /docs para ver los endpoints.",
            "docs": "/docs",
        }
