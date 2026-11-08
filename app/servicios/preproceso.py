"""Preprocesamiento de series temporales (Pandas · NumPy · normalización).

Capa del pipeline CAPTURA DE DATOS:
  - limpieza de ruido (filtro mediano)
  - valores faltantes (interpolación lineal)
  - ventanas temporales deslizantes
  - extracción de características (media, desviación, pendiente, RMS, picos…)

Todo lo que entra aquí es una lista de números (o None); sale un dict
estructurado con las estadísticas listas para la detección.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

VARIABLES = ("temperatura", "humedad", "presion", "vibracion",
             "corriente", "caudal")


def _serie(valores: list[float | None]) -> pd.Series:
    s = pd.Series([None if v is None or not np.isfinite(v) else float(v)
                   for v in valores], dtype="float64")
    return s


def limpiar(valores: list[float | None]) -> dict:
    """Limpieza: interpolar faltantes y medir el ruido.

    - `valores`: serie interpolada (sin filtro mediano) — es la que entra en
      la detección, porque el filtro mediano eliminaría los picos anómalos
      que queremos detectar.
    - `valores_limpios`: serie con filtro mediano k=3 — solo para medir el
      ruido y las estadísticas de limpieza.
    """
    s = _serie(valores)
    faltantes = int(s.isna().sum())
    # valores nulos o no finitos: interpolación lineal (extrapolar con la
    # media de los bordes cuando no hay dos puntos)
    s = s.interpolate(method="linear", limit_direction="both")
    if s.isna().any():
        s = s.fillna(float(np.nanmean(s.values)) if len(s) else 0.0)
    media = float(s.mean())
    # Filtro mediano k=3: únicamente para medir el ruido recorrido
    limpia = s.rolling(3, center=True, min_periods=1).median()
    ruido = float(np.mean(np.abs(s.values - limpia.values)))
    return {"total": int(len(s)), "faltantes": faltantes,
            "interpolados": faltantes,
            "valores": [float(v) for v in s.values],
            "valores_limpios": [float(v) for v in limpia.values],
            "media": media, "ruido": ruido}


def ventanas(valores: list[float], tamano: int) -> np.ndarray:
    """Ventanas temporales deslizantes (N x tamano)."""
    v = np.asarray(valores, dtype="float64")
    if len(v) < tamano:
        if len(v) == 0:
            return np.zeros((0, tamano))
        tamano = len(v)
    return np.array([v[i:i + tamano] for i in range(0, len(v) - tamano + 1)])


def caracteristicas(w: np.ndarray) -> list[float]:
    """Extracción de características de una ventana: estadística + forma."""
    x = np.asarray(w, dtype="float64").ravel()
    media = float(np.mean(x))
    desviacion = float(np.std(x))
    rms = float(np.sqrt(np.mean(x ** 2)))
    # pendiente de regresión lineal (tendencia)
    pendiente = float(np.polyfit(np.arange(len(x)), x, 1)[0]) if len(x) > 1 else 0.0
    # ruido de primera diferencia
    ruido = float(np.mean(np.abs(np.diff(x)))) if len(x) > 1 else 0.0
    # picos: desviaciones > 2.5σ sobre la media de la ventana
    picos = int(np.sum(np.abs(x - media) > 2.5 * desviacion)) if desviacion > 0 else 0
    return [media, desviacion, float(np.min(x)), float(np.max(x)),
            pendiente, rms, ruido, picos]


def normalizar(valores: list[float]) -> list[float]:
    """Normalización min-max a [0, 1] (caer bien al OCSVM y al OCNN)."""
    v = np.asarray(valores, dtype="float64")
    mi, ma = float(np.min(v)), float(np.max(v))
    if ma - mi < 1e-9:
        return [0.5] * len(v)
    return [float((x - mi) / (ma - mi)) for x in v]


def resumen(valores: list[float | None], ventana: int, umbral: float | None) -> dict:
    """Resumen completo de preprocesamiento sobre la serie received."""
    limpia = limpiar(valores)
    valores_limpios = limpia["valores"]
    vents = ventanas(valores_limpios, ventana)
    stats = {
        "total": limpia["total"],
        "faltantes": limpia["faltantes"],
        "interpolados": limpia["interpolados"],
        "ruido": limpia["ruido"],
        "ventanas": int(len(vents)),
        "caracteristicas": None,
        "umbral": umbral,
    }
    if len(vents) >= 1:
        stats["caracteristicas"] = {
            "media": round(vents[-1].mean(), 3),
            "desviacion": round(vents[-1].std(), 3),
            "min": round(float(vents[-1].min()), 3),
            "max": round(float(vents[-1].max()), 3),
            "pendiente": round(float(np.polyfit(np.arange(ventana), vents[-1], 1)[0]), 4),
            "rms": round(float(np.sqrt(np.mean(vents[-1] ** 2))), 3),
        }
    if umbral is not None and stats["caracteristicas"]:
        c = stats["caracteristicas"]
        stats["cumple_umbral"] = c["media"] <= umbral
    return stats
