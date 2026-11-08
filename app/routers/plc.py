"""Rutas de PLC Modbus TCP/IP (página de Comunicación)."""
from fastapi import APIRouter, Depends, HTTPException

from ..db import Dispositivo, PlcModbus
from ..deps import ahora, get_sesion
from ..schemas import PlcIn
from ..servicios import plc as srv_plc
from ..servicios.dispositivos import registrar_evento

router = APIRouter(tags=["plc"])


def _vista(f, extra=None):
    d = {"id": f.id, "nombre": f.nombre, "ip": f.ip, "puerto": f.puerto,
         "unidad": f.unidad, "direccion": f.direccion,
         "tipo_registro": f.tipo_registro, "intervalo_s": f.intervalo_s,
         "power": bool(f.power),
         "estado": f.estado, "ultimo_valor": f.ultimo_valor,
         "ultimo_contacto": (f.ultimo_contacto.isoformat() + "Z") if f.ultimo_contacto else None}
    if extra:
        d.update(extra)
    return d


def _aplicar(f, d):
    f.nombre = (d.nombre or "PLC").strip()
    f.ip = d.ip.strip()
    f.puerto = min(max(int(d.puerto), 1), 65535)
    f.unidad = min(max(int(d.unidad), 0), 247)
    f.direccion = min(max(int(d.direccion), 0), 65535)
    f.tipo_registro = d.tipo_registro if d.tipo_registro in srv_plc.FUNCIONES else "holding"
    f.intervalo_s = min(max(int(d.intervalo_s), 1), 3600)
    f.power = bool(d.power)


def _reflejar_en_dispositivos(s, f, conectado):
    """El PLC también aparece en la lista general de dispositivos."""
    chip = f"plc-{f.id}"
    disp = s.get(Dispositivo, chip)
    t = ahora()
    if disp is None:
        disp = Dispositivo(chip_id=chip, creado_en=t)
        s.add(disp)
    disp.nombre, disp.tipo = f.nombre, "PLC · Modbus TCP/IP"
    disp.ip, disp.wifi = f.ip, ""
    disp.estado = "conectado" if conectado else "desconectado"
    disp.ultimo_contacto = t


@router.get("/api/plc")
def listar(s=Depends(get_sesion)):
    return {"plc": [_vista(f) for f in s.query(PlcModbus).order_by(PlcModbus.id).all()]}


@router.post("/api/plc/probar")
def probar_sin_guardar(d: PlcIn):
    """Prueba la conexión con los datos del formulario, sin guardar."""
    return srv_plc.probar(d.ip.strip(), d.puerto, d.unidad, d.direccion, d.tipo_registro)


@router.post("/api/plc")
def agregar(d: PlcIn, s=Depends(get_sesion)):
    if not d.ip.strip():
        raise HTTPException(400, "Escribe la dirección IP del PLC.")
    f = PlcModbus(creado_en=ahora())
    _aplicar(f, d)
    s.add(f)
    s.commit()
    r = srv_plc.probar(f.ip, f.puerto, f.unidad, f.direccion, f.tipo_registro)
    f.estado = "conectado" if r["ok"] else "sin respuesta"
    if r["ok"]:
        f.ultimo_valor, f.ultimo_contacto = str(r["valor"]), ahora()
    _reflejar_en_dispositivos(s, f, r["ok"])
    registrar_evento(s, "CONEXION_PLC",
                     f"Se agregó el PLC {f.nombre} ({f.ip}:{f.puerto}) por Modbus TCP/IP"
                     + ("" if r["ok"] else ": sin respuesta al probar"))
    s.commit()
    return _vista(f, {"prueba": r, "mensaje": ("PLC agregado y conectado: primera lectura correcta."
                     if r["ok"] else "PLC guardado, pero sin respuesta por ahora: " + r["mensaje"])})


@router.post("/api/plc/{plc_id}/probar")
def probar_guardado(plc_id: int, s=Depends(get_sesion)):
    f = s.get(PlcModbus, plc_id)
    if f is None:
        raise HTTPException(404, "Ese PLC ya no existe.")
    r = srv_plc.probar(f.ip, f.puerto, f.unidad, f.direccion, f.tipo_registro)
    f.estado = "conectado" if r["ok"] else "sin respuesta"
    if r["ok"]:
        f.ultimo_valor, f.ultimo_contacto = str(r["valor"]), ahora()
    _reflejar_en_dispositivos(s, f, r["ok"])
    s.commit()
    return _vista(f, {"prueba": r})


@router.post("/api/plc/{plc_id}/power")
def toggle_power(plc_id: int, s=Depends(get_sesion)):
    """Encende/apaga el módulo PLC (apagado = no se consulta)."""
    f = s.get(PlcModbus, plc_id)
    if f is None:
        raise HTTPException(404, "Ese PLC ya no existe.")
    f.power = not f.power
    _reflejar_en_dispositivos(s, f, bool(f.power))
    if not f.power:
        f.estado = "apagado"
        f.ultimo_valor = ""
    else:
        r = srv_plc.probar(f.ip, f.puerto, f.unidad, f.direccion, f.tipo_registro)
        f.estado = "conectado" if r["ok"] else "sin respuesta"
        if r["ok"]:
            f.ultimo_valor, f.ultimo_contacto = str(r["valor"]), ahora()
    registrar_evento(s, "PLC_POWER",
                     f"PLC {f.nombre} {'encendido' if f.power else 'apagado'}")
    s.commit()
    return _vista(f)


@router.delete("/api/plc/{plc_id}")
def borrar(plc_id: int, s=Depends(get_sesion)):
    f = s.get(PlcModbus, plc_id)
    if f is None:
        raise HTTPException(404, "Ese PLC ya no existe.")
    disp = s.get(Dispositivo, f"plc-{f.id}")
    if disp is not None:
        s.delete(disp)
    registrar_evento(s, "PLC_BORRADO", f"Se eliminó el PLC {f.nombre} ({f.ip}:{f.puerto})")
    s.delete(f)
    s.commit()
    return {"ok": True}
