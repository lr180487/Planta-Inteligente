"""Lecturas de sensores: guardar (con alarma) y listar (con caché)."""
from fastapi import APIRouter, Depends

from .. import config, tasks
from ..cache import cache
from ..db import Lectura
from ..deps import get_sesion
from ..schemas import LecturaIn
from ..worker import tarea_procesar_lectura

router = APIRouter(tags=["lecturas"])


@router.post("/api/lecturas")
def crear_lectura(d: LecturaIn, s=Depends(get_sesion)):
    lec = Lectura(dispositivo=d.dispositivo, temperatura=d.temperatura,
                  humedad=d.humedad, nivel=d.nivel)
    s.add(lec)
    s.commit()
    cache.set(f"ultima:{d.dispositivo}",
              {"temperatura": d.temperatura, "humedad": d.humedad, "nivel": d.nivel})
    modo = tasks.enviar_tarea("procesar_lectura", tarea_procesar_lectura.run,
                              d.dispositivo, d.temperatura)
    alarma = d.temperatura is not None and d.temperatura > config.UMBRAL_TEMP
    return {"ok": True, "id": lec.id, "alarma": alarma, "tarea": modo}


@router.get("/api/lecturas")
def listar_lecturas(limite: int = 20, s=Depends(get_sesion)):
    cacheada = cache.get(f"lecturas:{limite}")
    if cacheada is not None:
        return {"origen": "cache", "datos": cacheada}
    filas = s.query(Lectura).order_by(Lectura.id.desc()).limit(limite).all()
    datos = [{"id": f.id, "dispositivo": f.dispositivo, "temperatura": f.temperatura,
              "humedad": f.humedad, "nivel": f.nivel,
              "hora": f.creada_en.isoformat() + "Z"} for f in filas]
    cache.set(f"lecturas:{limite}", datos)
    return {"origen": "bd", "datos": datos}
