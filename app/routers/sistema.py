"""Estado general del sistema y registro de eventos."""
from fastapi import APIRouter, Depends

from .. import rag, search, tasks
from ..cache import TIPO_CACHE
from ..db import Dispositivo, Evento, Lectura, TIPO_BD
from ..deps import ahora, get_sesion

router = APIRouter(tags=["sistema"])


@router.get("/api/salud")
def salud():
    return {"estado": "ok", "base_de_datos": TIPO_BD, "cache": TIPO_CACHE,
            "worker": tasks.MODO, "busqueda_web": search.proveedor_activo(),
            "busqueda_respaldo": "duckduckgo",
            "rag": rag.estado_rag(),
            "hora": ahora().isoformat() + "Z"}


@router.get("/api/estado")
def estado(s=Depends(get_sesion)):
    return {
        "dispositivos": s.query(Dispositivo).count(),
        "conectados": s.query(Dispositivo).filter_by(estado="conectado").count(),
        "lecturas": s.query(Lectura).count(),
        "eventos": s.query(Evento).count(),
        "base_de_datos": TIPO_BD, "cache": TIPO_CACHE, "worker": tasks.MODO,
    }


@router.get("/api/eventos")
def eventos(limite: int = 20, s=Depends(get_sesion)):
    filas = s.query(Evento).order_by(Evento.id.desc()).limit(limite).all()
    return {"eventos": [{"id": f.id, "tipo": f.tipo, "detalle": f.detalle,
                         "hora": f.creado_en.isoformat() + "Z"} for f in filas]}
