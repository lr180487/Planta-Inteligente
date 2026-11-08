"""Búsqueda web con doble proveedor.

Principal:  Tavily  (si hay TAVILY_API_KEY) — pensado para asistentes.
Respaldo:   DuckDuckGo (página pública de resultados, sin clave).

Si Tavily falla o no hay clave, se usa DuckDuckGo automáticamente.
Los resultados se guardan en caché (Upstash o LRU) unos minutos.
"""
import html as _html
import re
import urllib.parse

import httpx

from . import config
from .cache import cache

_UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) PlantaInteligente/1.0"}


def proveedor_activo():
    return "tavily" if config.TAVILY_API_KEY else "duckduckgo"


def _buscar_tavily(consulta, limite):
    r = httpx.post(
        "https://api.tavily.com/search",
        headers={"Authorization": f"Bearer {config.TAVILY_API_KEY}",
                 "Content-Type": "application/json"},
        json={"query": consulta, "max_results": limite,
              "search_depth": "basic", "include_answer": True},
        timeout=15,
    )
    r.raise_for_status()
    d = r.json()
    resultados = [{"titulo": x.get("title", ""), "url": x.get("url", ""),
                   "resumen": (x.get("content", "") or "")[:320]}
                  for x in d.get("results", [])]
    return {"fuente": "tavily", "respuesta_breve": d.get("answer") or "",
            "resultados": resultados}


def _buscar_duckduckgo(consulta, limite):
    r = httpx.get(
        "https://html.duckduckgo.com/html/",
        params={"q": consulta}, headers=_UA, timeout=15, follow_redirects=True,
    )
    r.raise_for_status()
    cuerpo = r.text
    enlaces = re.findall(
        r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', cuerpo, re.S)
    resumenes = re.findall(r'class="result__snippet"[^>]*>(.*?)</a>', cuerpo, re.S)

    def limpiar(x):
        return _html.unescape(re.sub(r"<[^>]+>", "", x)).strip()

    resultados = []
    for i, (url, titulo) in enumerate(enlaces[:limite]):
        real = url
        if "uddg=" in url:  # DuckDuckGo envuelve la URL destino
            q = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
            real = q.get("uddg", [url])[0]
        resultados.append({
            "titulo": limpiar(titulo), "url": real,
            "resumen": limpiar(resumenes[i])[:320] if i < len(resumenes) else "",
        })
    return {"fuente": "duckduckgo", "respuesta_breve": "", "resultados": resultados}


def buscar_web(consulta, limite=5):
    """Busca primero en Tavily (si hay clave) y cae a DuckDuckGo."""
    consulta = (consulta or "").strip()
    if not consulta:
        return {"fuente": proveedor_activo(), "respuesta_breve": "", "resultados": []}
    clave = f"web:{consulta.lower()}:{limite}"
    guardado = cache.get(clave)
    if guardado is not None:
        guardado = dict(guardado); guardado["desde_cache"] = True
        return guardado
    errores = []
    if config.TAVILY_API_KEY:
        try:
            salida = _buscar_tavily(consulta, limite)
            cache.set(clave, salida)
            return salida
        except Exception as e:  # cae al respaldo
            errores.append(f"tavily: {e}")
    try:
        salida = _buscar_duckduckgo(consulta, limite)
        if errores:
            salida["aviso"] = "Tavily no respondió; se usó DuckDuckGo."
        cache.set(clave, salida)
        return salida
    except Exception as e:
        return {"fuente": "duckduckgo", "respuesta_breve": "",
                "resultados": [], "error": f"No se pudo buscar en la web ({e})"}
