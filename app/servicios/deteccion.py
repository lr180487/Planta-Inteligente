"""Detección de anomalías: OCSVM · OCNN · Isolation Forest.

Pipeline:
  1. se toma la ventana reciente de una variable (capturas guardadas)
  2. preproceso: limpieza, valores faltantes, ventanas, características
  3. los tres algoritmos devuelven un score 0..1 (0=normal, 1=anómalo):
       OCSVM        -> OneClassSVM (frontera normal en características)
       OCNN         -> autoencoder convolucional (error de reconstrucción)
       IsolationForest -> aislar puntos atípicos rápido
  4. la fusión (servicios/fusion.py) decide consensuso + severidad

Los modelos se entrenan sobre ventanas recientes; se cachean por
(variable, ventana, cantidad de puntos) para no reentrenar en cada clic.
"""
from __future__ import annotations

import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM

from . import preproceso
from .ocnn import OCNN

ALGORIMOS = ("ocsvm", "ocnn", "if")
PESOS = {"ocsvm": 0.3, "ocnn": 0.4, "if": 0.3}

_cache = {}


def _caracteristicas_ventanas(vents: np.ndarray) -> np.ndarray:
    """Ventanas -> filas de características (media, std, min, max, pen, rms, ruido, picos)."""
    return np.stack([preproceso.caracteristicas(w) for w in vents])


def _entrenar_y_puntajar(vents: np.ndarray, variable: str, ventana: int):
    """Entrena los tres algoritmos y puntaja cada ventana."""
    feats = _caracteristicas_ventanas(vents)
    scores = {}

    # ---- OCSVM: OneClassSVM (RBF) sobre características ----
    oc = OneClassSVM(kernel="rbf", nu=0.05, gamma="scale")
    oc.fit(feats)
    dec = oc.decision_function(feats)
    escala = max(float(np.abs(dec).max()), 1e-6)
    oc_scores = np.clip(-dec / escala, 0, 1)
    scores["ocsvm"] = oc_scores

    # ---- OCNN: autoencoder convolucional sobre ventanas normalizadas ----
    n = vents.shape[1]
    ocnn = OCNN(n)
    norm = np.stack([preproceso.normalizar(list(w)) for w in vents])
    ocnn.fit(norm, epochs=250, lr=0.04)
    rec = ocnn.forward(norm)
    errs = np.mean((rec - norm) ** 2, axis=1)
    mu, sd = float(np.mean(errs)), float(np.std(errs)) + 1e-6
    ocnn_scores = np.clip(1 / (1 + np.exp(-1.5 * (errs - mu) / sd)), 0, 1)
    scores["ocnn"] = ocnn_scores

    # ---- Isolation Forest sobre las ventanas raw ----
    ifo = IsolationForest(contamination=0.05, n_estimators=100, random_state=7)
    ifo.fit(vents)
    ss = ifo.score_samples(vents)
    escala_if = max(float(np.abs(ss).max()), 1e-6)
    if_scores = np.clip(-ss / escala_if, 0, 1)
    scores["if"] = if_scores

    return scores, {"ocsvm": oc, "ocnn": ocnn, "if": ifo}, {
        "ocsvm_escala": escala, "ocnn_mu": mu, "ocnn_sd": sd,
        "if_escala": escala_if}


def _predecir(vent: np.ndarray, modelos, meta) -> tuple:
    """Puntajes de una ventana nueva con los modelos entrenados."""
    feat = np.asarray(preproceso.caracteristicas(vent), dtype="float64")
    oc = modelos["ocsvm"]
    dec = float(oc.decision_function(feat[None, :])[0])
    oc_score = float(np.clip(-dec / meta["ocsvm_escala"], 0, 1))

    norm = preproceso.normalizar(list(vent))
    ocnn = modelos["ocnn"]
    rec = ocnn.forward(np.array([norm]))[0]
    err = float(np.mean((rec - np.array(norm)) ** 2))
    ocnn_score = float(np.clip(
        1 / (1 + np.exp(-1.5 * (err - meta["ocnn_mu"]) / meta["ocnn_sd"])), 0, 1))

    ifo = modelos["if"]
    ss = float(ifo.score_samples(vent[None, :])[0])
    if_score = float(np.clip(-ss / meta["if_escala"], 0, 1))
    scores = {"ocsvm": oc_score, "ocnn": ocnn_score, "if": if_score}
    return scores, rec, dec


def analizar(valores: list[float | None], variable: str, ventana: int,
             umbral: float | None = None) -> dict:
    """Análisis completo sobre una serie: preproceso + 3 algoritmos.

    Los modelos se entrenan sobre el PERÍODO BASE (primeros 75% de la
    serie) y puntajan la ventana RECIENTE (últimos 25%), para que las
    anomalías recientes no contaminen el entrenamiento.
    """
    limpia = preproceso.limpiar(valores)
    valores_limpios = limpia["valores"]
    vents = preproceso.ventanas(valores_limpios, ventana)
    if len(vents) < 3:
        return {"ok": False, "motivo": "necesito más historial",
                "ventanas": len(vents),
                "solicitud": f"cargar más puntos de {variable} "
                              f"(necesito al menos {ventana * 3})"}

    n_base = max(vents.shape[0] // 4, 4)
    base = vents[:-n_base] if n_base else vents
    reciente = vents[-1]

    clave = (variable, ventana, len(valores_limpios))
    if clave in _cache:
        scores, modelos, meta = _cache[clave]
    else:
        scores, modelos, meta = _entrenar_y_puntajar(base, variable, ventana)
        _cache.clear()  # solo el último modelo porVariable
        _cache[clave] = (scores, modelos, meta)

    pred, rec, dec_test = _predecir(reciente, modelos, meta)
    stats = preproceso.resumen(valores, ventana, umbral)

    # --- datos para las gráficas ---
    # scatter: últimas 10 ventanas en (media, desviación) + anomalia por OCSVM
    scatter = []
    for w in vents[-10:]:
        c = preproceso.caracteristicas(w)
        d = float(modelos["ocsvm"].decision_function(
            np.asarray([c], dtype="float64"))[0])
        scatter.append({"x": round(float(c[0]), 2), "y": round(float(c[1]), 2),
                        "ocsvm": bool(d < 0)})
    # reconstrucción del OCNN sobre la ventana reciente (en escala original)
    mi, ma = float(np.min(reciente)), float(np.max(reciente))
    recon_espacio = [round(float(r) * (ma - mi) + mi, 2) for r in rec]
    reconstruccion = {"original": [round(float(v), 2) for v in reciente],
                      "recon": recon_espacio}
    # puntos anómalos en la ventana: desvío > 2.5σ respecto al período base
    base_vals = np.concatenate(base) if len(base) else reciente
    mu_b = float(np.mean(base_vals))
    sd_b = float(np.std(base_vals)) or 1e-6
    puntos_anomalos = [i for i, v in enumerate(reciente)
                       if abs(v - mu_b) > 2.5 * sd_b]

    # frontera OCSVM: rejilla en (media, desviación) con las demás
    # características fijas en la ventana testeada (corte 2D del
    # decision_function). La isolínea d=0 es la frontera normal.
    frontera = None
    if scatter:
        xs = [p["x"] for p in scatter]
        ys = [p["y"] for p in scatter]
        x0, x1 = float(np.min(xs)), float(np.max(xs))
        y0, y1 = float(np.min(ys)), float(np.max(ys))
        dx = (x1 - x0) / 28 or 1.0
        dy = (y1 - y0) / 28 or 1.0
        feat_rest = np.asarray(preproceso.caracteristicas(reciente),
                               dtype="float64")[2:]  # min, max, pen, rms, ruido, picos
        grid = []
        for ix in range(29):
            row = []
            for iy in range(29):
                feat = np.concatenate([[x0 + ix * dx, y0 + iy * dy], feat_rest])
                d = float(modelos["ocsvm"].decision_function(feat[None, :])[0])
                row.append(round(d, 2))
            grid.append(row)
        frontera = {"x0": round(x0, 2), "y0": round(y0, 2),
                    "dx": round(dx, 3), "dy": round(dy, 3),
                    "nx": 29, "ny": 29, "d": grid}

    return {"ok": True, "variable": variable, "ventana": ventana,
            "preproceso": stats, "ventana_utilizada": reciente.tolist(),
            "base_ventanas": int(len(base)),
            "scores": {a: round(float(pred[a]), 3) for a in ALGORIMOS},
            "detalle": {a: {
                "ocsvm": "frontera normal (OneClassSVM RBF)",
                "ocnn": "patrones complejos (autoencoder convolucional)",
                "if": "aislamiento rápido (Isolation Forest)",
            }[a] for a in ALGORIMOS},
            "umbral": umbral,
            "scatter": scatter, "reconstruccion": reconstruccion,
            "puntos_anomalos": puntos_anomalos,
            "decision_ocsvm": round(dec_test, 3),
            "frontera": frontera}
