"""Fusión y validación de resultados.

Combina los scores de OCSVM, OCNN e Isolation Forest:
  - consenso: cada algoritmo vota anomalía si su score >= 0.55
  - puntuación: suma ponderada (0.3 / 0.4 / 0.3)
  - reducción de falsas alarmas: se confirma con >= 2 votos o puntaje >= 0.72
  - severidad: info / media / alta / critica
"""
from __future__ import annotations

from .deteccion import ALGORIMOS, PESOS

VOTO_UMBRAL = 0.55      # score mínimo para que un algoritmo vote anomalía
CONSENSO_UMBRAL = 0.72  # puntaje mínimo de fusión para confirmar
SEV_POR_DEFECTO = "media"


def fusionar(scores: dict, umbral: float | None = None,
             valor: float | None = None) -> dict:
    votos = {}
    for a in ALGORIMOS:
        votos[a] = bool(scores.get(a, 0) >= VOTO_UMBRAL)
    votos_conteo = sum(votos.values())
    puntaje = sum(PESOS[a] * scores.get(a, 0) for a in ALGORIMOS)
    puntaje = round(float(puntaje), 3)

    # Reducción de falsas alarmas: se confirma con consenso o puntaje alto
    confirmada = votos_conteo >= 2 or puntaje >= CONSENSO_UMBRAL

    # Clasificación de severidad
    if not confirmada:
        severidad = "info"
    elif votos_conteo == 3 or puntaje >= 0.85:
        severidad = "critica"
    elif votos_conteo >= 2 and puntaje >= CONSENSO_UMBRAL:
        severidad = "alta"
    else:
        severidad = SEV_POR_DEFECTO

    # Si la lectura supera un umbral físico, escala la severidad
    if umbral is not None and valor is not None and valor > umbral:
        if severidad == "info":
            severidad = "media"
        elif severidad == "media":
            severidad = "alta"

    algoritmos = "+".join(a.upper() if a != "if" else "IsolationForest"
                          for a in ALGORIMOS if votos[a])
    return {
        "puntaje": puntaje,
        "votos": {a: votos[a] for a in ALGORIMOS},
        "votos_conteo": votos_conteo,
        "consenso": confirmada,
        "falsas_reducida": not confirmada,
        "severidad": severidad,
        "algoritmos": algoritmos or "—",
        "clasificacion": _clasificar(severidad),
        "umbral": umbral,
        "cumple_umbral": (umbral is not None and valor is not None
                          and valor <= umbral) if umbral is not None else None,
    }


def _clasificar(sev: str) -> str:
    return {
        "info": "Normal · sin alerta",
        "media": "Alerta media · monitorear",
        "alta": "Alerta alta · intervenir",
        "critica": "Alerta crítica · actuar ya",
    }.get(sev, sev)
