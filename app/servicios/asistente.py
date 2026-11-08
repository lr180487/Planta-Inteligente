"""Asistente con contexto: datos de la planta + RAG (+ web si se pide).

No inventa cifras: solo redacta con lo encontrado y, si no hay datos,
lo dice. El dato de planta solo se incluye si la pregunta trata de la
planta (si no, contamina respuestas ajenas).
"""
from .. import rag, search
from ..db import Dispositivo, Lectura

_PALABRAS_PLANTA = ("temperatura", "planta", "dispositivo", "esp32",
                    "lectura", "sensor", "tanque", "humedad", "nivel")
_PALABRAS_WEB = ("busca", "buscar", "internet", "web", "en línea", "en linea")


def responder(s, pregunta, web=False):
    pregunta = (pregunta or "").strip()
    salida = {"pregunta": pregunta}

    # 1) Contexto de la planta (última lectura guardada)
    ultima = s.query(Lectura).order_by(Lectura.id.desc()).first()
    conectados = s.query(Dispositivo).filter_by(estado="conectado").count()
    salida["planta"] = {
        "ultima_temperatura": ultima.temperatura if ultima else None,
        "ultima_humedad": ultima.humedad if ultima else None,
        "ultima_nivel": ultima.nivel if ultima else None,
        "dispositivos_conectados": conectados,
    }

    # 2) Contexto documental (RAG)
    salida["documentacion"] = rag.buscar(pregunta) if pregunta else []

    # 3) Contexto web (a petición o si la pregunta lo pide)
    pide_web = web or any(p in pregunta.lower() for p in _PALABRAS_WEB)
    salida["web"] = search.buscar_web(pregunta) if (pide_web and pregunta) else None

    # Redacción solo con lo encontrado
    partes = []
    if any(p in pregunta.lower() for p in _PALABRAS_PLANTA) \
            and salida["planta"]["ultima_temperatura"] is not None:
        partes.append(f"En la planta, la última temperatura guardada es "
                      f"{salida['planta']['ultima_temperatura']} °C, con "
                      f"{conectados} dispositivo(s) conectado(s).")
    if salida["documentacion"]:
        # Primera frase legible: evita fragmentos que sean filas de tabla
        elegido = next((f for f in salida["documentacion"]
                        if " — " not in f["texto"][:60] and len(f["texto"]) > 80),
                       salida["documentacion"][0])
        partes.append("Según la documentación del proyecto: "
                      + elegido["texto"][:280].replace("\n", " "))
    if salida.get("web") and salida["web"].get("resultados"):
        r0 = salida["web"]["resultados"][0]
        partes.append(f"En la web ({salida['web']['fuente']}): {r0['titulo']} — "
                      f"{r0['resumen'][:180]}")
    salida["respuesta"] = " ".join(partes) if partes else (
        "No encontré datos para esa pregunta todavía: ni lecturas guardadas, "
        "ni coincidencias en la documentación.")
    return salida
