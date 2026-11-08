"""Avisos (Gmail/Telegram) y receptor de tareas QStash."""
from fastapi import APIRouter, Request

from .. import tasks
from ..notify import notificar
from ..schemas import NotificarIn
from ..worker import tarea_notificar

router = APIRouter(tags=["notificaciones"])


@router.post("/api/notificar")
def notificar_api(d: NotificarIn):
    modo = tasks.enviar_tarea("notificar", tarea_notificar.run, d.asunto, d.mensaje)
    return {"ok": True, "tarea": modo, "canales": d.canales}


@router.post("/api/tareas/qstash")
async def receptor_qstash(req: Request):
    """Destino para QStash cuando no hay Celery."""
    cuerpo = await req.json()
    if cuerpo.get("tarea") == "notificar":
        kw = cuerpo.get("kwargs", {})
        notificar(kw.get("asunto", "Aviso"), kw.get("mensaje", ""))
    return {"ok": True}
