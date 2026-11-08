"""CAPTURA DE DATOS · detección · fusión · alertas.

Endpoints del pipeline completo:
  captura:  sensores/SCADA, MQTT, PLC, ESP32
  detección: ventana actual, análisis (OCSVM/OCNN/IsolationForest + fusión)
  alertas:  lista, simular, leer (auditoría), métricas
"""
import json
import random
import time

import numpy as np
from fastapi import APIRouter, Depends

from .. import config
from ..db import Alerta, Captura, Dispositivo, Evento, PlcModbus
from ..deps import ahora, get_sesion
from ..schemas import AnalisisIn, CapturaIn, MqttMsgIn
from ..servicios import deteccion, fusion
from ..servicios import plc as svc_plc

router = APIRouter(tags=["captura"])

VARIABLES = ("temperatura", "humedad", "presion", "vibracion",
             "corriente", "caudal")


def _registrar(s, tipo: str, detalle: str):
    s.add(Evento(tipo=tipo, detalle=detalle))
    s.commit()


def _agregar_capturas(s, dispositivo: str, variables: dict,
                      umbrales: dict, fuente: str) -> int:
    filas = 0
    for nombre, valor in variables.items():
        if valor is None:
            continue
        s.add(Captura(dispositivo=dispositivo, variable=nombre,
                      valor=float(valor), umbral=umbrales.get(nombre),
                      fuente=fuente))
        filas += 1
    s.commit()
    return filas


# ------------------------------ captura ------------------------------
@router.post("/api/captura/sensores")
def captura_sensores(d: CapturaIn, s=Depends(get_sesion)):
    n = _agregar_capturas(s, d.dispositivo, d.variables, d.umbrales, "sensores")
    _registrar(s, "CAPTURA_SENSORES", f"{n} variables de {d.dispositivo}")
    return {"ok": True, "capturas": n, "fuente": "sensores"}


@router.post("/api/captura/scada")
def captura_scada(d: CapturaIn, s=Depends(get_sesion)):
    n = _agregar_capturas(s, d.dispositivo, d.variables, d.umbrales, "scada")
    _registrar(s, "CAPTURA_SCADA", f"{n} variables de SCADA ({d.dispositivo})")
    return {"ok": True, "capturas": n, "fuente": "scada"}


@router.post("/api/captura/esp32")
def captura_esp32(d: CapturaIn, s=Depends(get_sesion)):
    n = _agregar_capturas(s, d.dispositivo, d.variables, d.umbrales, "esp32")
    _registrar(s, "CAPTURA_ESP32", f"{n} variables de ESP32 ({d.dispositivo})")
    return {"ok": True, "capturas": n, "fuente": "esp32"}


@router.post("/api/captura/mqtt")
def captura_mqtt(d: MqttMsgIn, s=Depends(get_sesion)):
    """Un mensaje MQTT: payload número o JSON {variable: valor}."""
    payload = d.payload.strip()
    variables = {}
    try:
        data = json.loads(payload)
        if isinstance(data, dict):
            variables = {str(k): float(v) for k, v in data.items()}
        elif isinstance(data, (int, float)):
            variables = {"mqtt_valor": float(data)}
    except (ValueError, TypeError):
        try:
            variables = {"mqtt_valor": float(payload)}
        except ValueError:
            return {"ok": False, "motivo": "payload no reconocido",
                    "ayuda": "un número o un JSON {variable: valor}"}
    n = _agregar_capturas(s, d.dispositivo, variables, {}, "mqtt")
    _registrar(s, "CAPTURA_MQTT", f"mensaje en {d.topic} ({n} variables)")
    return {"ok": True, "capturas": n, "topic": d.topic, "fuente": "mqtt"}


@router.post("/api/captura/plc")
def captura_plc(s=Depends(get_sesion)):
    """Lee cada PLC conectado y guarda su valor como captura."""
    filas = 0
    for p in s.query(PlcModbus).filter_by(estado="conectado").all():
        res = svc_plc.probar(p.ip, p.puerto, p.unidad, p.direccion,
                             p.tipo_registro)
        if res["ok"] and res["valor"] is not None:
            s.add(Captura(dispositivo=p.nombre, variable="plc_registro",
                          valor=float(res["valor"]), fuente="plc"))
            filas += 1
    s.commit()
    _registrar(s, "CAPTURA_PLC", f"{filas} lecturas de PLC")
    return {"ok": True, "capturas": filas, "fuente": "plc"}


@router.get("/api/captura/series")
def captura_series(variable: str = "temperatura", limite: int = 100,
                   s=Depends(get_sesion)):
    filas = s.query(Captura).filter_by(variable=variable) \
        .order_by(Captura.id.desc()).limit(limite).all()
    filas = list(reversed(filas))
    return {"variable": variable, "puntos": [
        {"v": f.valor, "dispositivo": f.dispositivo, "fuente": f.fuente,
         "umbral": f.umbral, "hora": f.creada_en.isoformat() + "Z"}
        for f in filas]}


@router.get("/api/captura/fuentes")
def captura_fuentes(s=Depends(get_sesion)):
    out = {}
    for f in s.query(Captura).all():
        out[f.fuente] = out.get(f.fuente, 0) + 1
    return {"fuentes": out, "total": s.query(Captura).count(),
            "dispositivos": s.query(Dispositivo).count(),
            "conectados": s.query(Dispositivo).filter_by(estado="conectado").count()}


# ------------------------------ detección ------------------------------
@router.post("/api/deteccion/series-demo")
def serie_demo(s=Depends(get_sesion)):
    """Genera un historial de ejemplo con anomalías para probar el pipeline."""
    # primero se borra el histórico demo anterior para no contaminar el
    # periodo base de entrenamiento
    s.query(Captura).filter_by(fuente="demo").delete()
    s.commit()
    rng = random.Random(int(time.time()) % 1000)
    dispositivo = "sensor-demo-01"
    base = {"temperatura": 55.0, "humedad": 48.0, "presion": 2.4,
            "vibracion": 0.6, "corriente": 12.0, "caudal": 40.0}
    puntos = 120
    for i in range(puntos):
        t = i / puntos * 4 * 3.14159
        variables = {}
        for nombre, b in base.items():
            variables[nombre] = round(
                b + 0.08 * b * np.sin(t) + rng.gauss(0, 0.01 * b), 3)
        # anomalías: picos fuertes en los últimos 12 puntos
        if i >= puntos - 12 and (i % 4 == 0):
            variables["temperatura"] = round(base["temperatura"] * 2.2, 1)
        _agregar_capturas(s, dispositivo, variables, {}, "demo")
    _registrar(s, "SERIE_DEMO",
               f"{puntos} puntos × {len(base)} variables (con anomalías)")
    return {"ok": True, "puntos": puntos, "dispositivo": dispositivo}


@router.post("/api/deteccion/analizar")
def analizar(d: AnalisisIn, s=Depends(get_sesion)):
    """Ejecuta el pipeline completo sobre la ventana reciente de una variable."""
    q = s.query(Captura).filter_by(variable=d.variable).order_by(Captura.id)
    if d.dispositivo:
        q = q.filter_by(dispositivo=d.dispositivo)
    filas = q.all()
    valores = [f.valor for f in filas]
    if not valores:
        return {"ok": False, "motivo": "no hay capturas para esta variable",
                "solicitud": "carga el historial demo o captura datos primero"}

    res = deteccion.analizar(valores, d.variable, max(8, min(d.ventana, 60)),
                             d.umbral)
    if not res.get("ok"):
        return {"ok": False, **res}

    umbral = d.umbral
    fusion_res = fusion.fusionar(res["scores"], umbral,
                                 float(res["ventana_utilizada"][-1]))
    alerta_id = None
    if d.crear_alerta and fusion_res["consenso"]:
        alerta = Alerta(
            dispositivo=filas[-1].dispositivo, variable=d.variable,
            tipo="anomalia", severidad=fusion_res["severidad"],
            valor=float(res["ventana_utilizada"][-1]), umbral=umbral,
            puntaje=fusion_res["puntaje"],
            algoritmos=fusion_res["algoritmos"],
            votos=f"{fusion_res['votos_conteo']}/3",
            mensaje=f"{fusion_res['clasificacion']} · {d.variable} en "
                    f"{filas[-1].dispositivo}",
        )
        s.add(alerta)
        s.commit()
        _registrar(s, "ALERTA_CREADA",
                   f"{d.variable} en {alerta.dispositivo}: {alerta.severidad}")
        alerta_id = alerta.id
    elif d.crear_alerta:
        _registrar(s, "DETECCION", f"{d.variable}: analizada, sin alerta")

    return {"ok": True, "variable": d.variable, "ventana": d.ventana,
            "preproceso": res["preproceso"],
            "scores": res["scores"], "detalle": res["detalle"],
            "fusion": fusion_res, "alerta_id": alerta_id,
            "serie": res["ventana_utilizada"],
            "scatter": res.get("scatter", []),
            "reconstruccion": res.get("reconstruccion"),
            "puntos_anomalos": res.get("puntos_anomalos", []),
            "decision_ocsvm": res.get("decision_ocsvm"),
            "frontera": res.get("frontera")}


@router.get("/api/deteccion/ventana")
def ventana_actual(variable: str = "temperatura", ventana: int = 30,
                   s=Depends(get_sesion)):
    filas = s.query(Captura).filter_by(variable=variable) \
        .order_by(Captura.id).all()
    valores = [f.valor for f in filas]
    if not valores:
        return {"ok": False, "motivo": "sin capturas"}
    umbral = None
    for f in filas:
        if f.umbral:
            umbral = f.umbral
            break
    from ..servicios import preproceso
    return {"ok": True, "variable": variable,
            "resumen": preproceso.resumen(valores, max(8, min(ventana, 60)),
                                          umbral),
            "serie": valores[-60:]}


# ------------------------------ alertas ------------------------------
@router.get("/api/alertas")
def listar_alertas(limite: int = 30, s=Depends(get_sesion)):
    filas = s.query(Alerta).order_by(Alerta.id.desc()).limit(limite).all()
    return {"alertas": [{
        "id": a.id, "dispositivo": a.dispositivo, "variable": a.variable,
        "tipo": a.tipo, "severidad": a.severidad, "valor": a.valor,
        "umbral": a.umbral, "puntaje": a.puntaje,
        "algoritmos": a.algoritmos, "votos": a.votos, "mensaje": a.mensaje,
        "leida": a.leida, "hora": a.creada_en.isoformat() + "Z"}
        for a in filas]}


@router.post("/api/alertas/simular")
def alerta_simular(variable: str = "temperatura", severidad: str = "media",
                   s=Depends(get_sesion)):
    alerta = Alerta(dispositivo="sensor-demo-01", variable=variable,
                    tipo="simulada", severidad=severidad,
                    valor=88.0 if variable == "temperatura" else 1.0,
                    umbral=80.0 if variable == "temperatura" else None,
                    puntaje=0.8, algoritmos="OCSVM+OCNN+IsolationForest",
                    votos="3/3", mensaje="Alerta simulada para probar el sistema")
    s.add(alerta)
    s.commit()
    _registrar(s, "ALERTA_SIMULADA", f"{variable}: {severidad}")
    return {"ok": True, "alerta": {
        "id": alerta.id, "variable": variable, "severidad": severidad}}


@router.post("/api/alertas/{id}/leer")
def alerta_leer(id: int, s=Depends(get_sesion)):
    a = s.get(Alerta, id)
    if a is None:
        return {"ok": False, "motivo": "alerta no encontrada"}
    a.leida = True
    s.commit()
    _registrar(s, "AUDITORIA_ALERTA", f"alerta {id} de {a.variable} leída")
    return {"ok": True, "id": id, "leida": True}


@router.get("/api/alertas/metricas")
def alertas_metricas(s=Depends(get_sesion)):
    filas = s.query(Alerta).all()
    sev = {"info": 0, "media": 0, "alta": 0, "critica": 0}
    for a in filas:
        sev[a.severidad] = sev.get(a.severidad, 0) + 1
    puntajes = [a.puntaje for a in filas if a.severidad != "info"]
    eventos = s.query(Evento).filter(Evento.tipo.in_(
        ["DETECCION", "ALERTA_CREADA", "ALERTA_SIMULADA"])).all()
    return {"total": len(filas), "por_severidad": sev,
            "activas": sum(1 for a in filas if not a.leida),
            "promedio_puntaje": round(sum(puntajes) / len(puntajes), 3)
            if puntajes else 0.0,
            "detecciones": sum(1 for e in eventos if e.tipo == "DETECCION"),
            "alertas_creadas": sum(1 for e in eventos if e.tipo == "ALERTA_CREADA"),
            "falsas_reducida": sum(1 for e in eventos if e.tipo == "DETECCION"),
            "eventos_total": s.query(Evento).count()}
