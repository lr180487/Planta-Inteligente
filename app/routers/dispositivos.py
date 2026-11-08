"""Dispositivos y detección de ESP32 recién conectados."""
from fastapi import APIRouter, Depends

from ..db import Dispositivo
from ..deps import ahora, get_sesion
from ..schemas import DispositivoIn, SincronizarIn
from ..servicios.dispositivos import (avisar_nuevo_esp32, registrar_evento,
                                      tocar_dispositivo)

router = APIRouter(tags=["dispositivos"])


@router.post("/api/dispositivos/sincronizar")
def sincronizar(d: SincronizarIn, s=Depends(get_sesion)):
    detectados = []
    for item in d.dispositivos:
        if tocar_dispositivo(s, item) and item.conectado:
            detectados.append(item.chip_id)
            registrar_evento(s, "CONEXION_ESP32",
                             f"Se conectó {item.nombre or item.chip_id} ({item.chip_id})")
    s.commit()
    for chip in detectados:
        avisar_nuevo_esp32(chip)
    return {"ok": True, "detectados_nuevos": detectados}


@router.post("/api/esp32/anunciar")
def anunciar_esp32(d: DispositivoIn, s=Depends(get_sesion)):
    """Un ESP32 real llamaría a este endpoint al unirse a la Wi-Fi."""
    nuevo = tocar_dispositivo(s, d)
    if nuevo and d.conectado:
        registrar_evento(s, "CONEXION_ESP32",
                         f"Se conectó {d.nombre or d.chip_id} ({d.chip_id}) vía {d.wifi or 'Wi-Fi'}")
    s.commit()
    if nuevo and d.conectado:
        avisar_nuevo_esp32(d.nombre or d.chip_id)
    return {"ok": True, "detectado_nuevo": bool(nuevo and d.conectado)}


@router.post("/api/esp32/heartbeat")
def heartbeat(d: DispositivoIn, s=Depends(get_sesion)):
    tocar_dispositivo(s, d)
    s.commit()
    return {"ok": True}


@router.get("/api/esp32/conectados")
def esp32_conectados(s=Depends(get_sesion)):
    t = ahora()
    filas = s.query(Dispositivo).filter_by(estado="conectado").all()
    return {"conectados": [
        {"chip_id": f.chip_id, "nombre": f.nombre, "tipo": f.tipo,
         "hace_segundos": int((t - f.ultimo_contacto).total_seconds())}
        for f in filas]}


@router.get("/api/dispositivos")
def dispositivos(s=Depends(get_sesion)):
    return {"dispositivos": [
        {"chip_id": f.chip_id, "nombre": f.nombre, "tipo": f.tipo,
         "estado": f.estado, "ultimo_contacto": f.ultimo_contacto.isoformat() + "Z"}
        for f in s.query(Dispositivo).all()]}
