"""Búsqueda web, RAG y asistente con contexto."""
from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from .. import rag, search
from ..deps import get_sesion
from ..schemas import AsistenteIn
from ..servicios.asistente import responder

router = APIRouter(tags=["asistente"])


@router.get("/api/buscar")
def buscar(q: str = "", limite: int = 5):
    """Búsqueda web: Tavily primero; si falla o no hay clave, DuckDuckGo."""
    return search.buscar_web(q, max(1, min(limite, 10)))

@router.get("/api/asistente/ver")
def asistente_ver(q: str = "", s=Depends(get_sesion)):
    """Página HTML con el resultado de preguntar a la documentación (pestaña nueva)."""
    import html as _html
    d = responder(s, q)
    fragmentos_html = ""
    for f in d["documentacion"]:
        origen = "Documento agregado por el usuario" if f.get("origen") == "usuario" else "Documentación del proyecto"
        fragmentos_html += f"""
      <article class="fuente">
        <div class="f-head">📄 <b>{_html.escape(f['fuente'])}</b>
          <span class="chip">{_html.escape(f['seccion'])}</span>
          <span class="chip gris">{origen}</span>
          <span class="chip gris">Relevancia {f['relevancia']}</span></div>
        <p>{_html.escape(f['texto'])}</p>
      </article>"""
    if not fragmentos_html:
        fragmentos_html = "<p class='sin'>La documentación no menciona ese tema todavía.</p>"
    planta = ""
    if d["planta"]["ultima_temperatura"] is not None:
        planta = (f"<span class='chip'>🌡 Última temperatura guardada: {d['planta']['ultima_temperatura']} °C</span>"
                  f"<span class='chip'>{d['planta']['dispositivos_conectados']} dispositivo(s) conectado(s)</span>")
    return HTMLResponse(f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Resultado de la pregunta · Planta Inteligente</title>
<style>
body{{font-family:Inter,system-ui,Arial,sans-serif;background:#f8fbff;color:#0f2237;margin:0;line-height:1.65}}
.barra{{background:#fff;border-bottom:1px solid #e0eaf6;padding:12px 20px;display:flex;gap:10px;align-items:center;flex-wrap:wrap}}
.logo{{font-weight:800}} .logo span{{background:#2563eb;color:#fff;border-radius:9px;padding:5px 9px}}
.chip{{font-size:.78rem;font-weight:700;background:#eff6ff;color:#1d4ed8;border:1px solid #dbeafe;border-radius:99px;padding:5px 10px}}
.chip.gris{{background:#f8fafc;color:#64748b;border-color:#e2e8f0}}
main{{max-width:880px;margin:22px auto;padding:0 18px 50px}}
.tarjeta{{background:#fff;border:1px solid #e0eaf6;border-radius:12px;padding:22px 26px;margin-bottom:16px}}
h1{{font-size:1.18rem;margin:0 0 8px}} h2{{font-size:1rem;margin:0 0 10px}}
.pregunta{{display:block;background:#eff6ff;border:1px solid #dbeafe;border-radius:10px;padding:12px 15px;font-weight:600}}
.respuesta{{font-size:1rem;color:#21344d}}
.fuente{{border:1px solid #e0eaf6;border-radius:10px;padding:14px 16px;margin-top:10px;background:#f8fbff}}
.f-head{{display:flex;gap:7px;align-items:center;flex-wrap:wrap}}
.fuente p{{margin:8px 0 0;color:#21344d;white-space:pre-wrap}}
.sin{{color:#64748b}}
</style></head><body>
<div class="barra"><span class="logo"><span>⚙️</span> Planta Inteligente</span>
<span class="chip">📚 Resultado de preguntar a la documentación</span>{planta}</div>
<main>
  <section class="tarjeta">
    <h1>Tu pregunta</h1>
    <span class="pregunta">“{_html.escape(d['pregunta'] or '—')}”</span>
    <h2 style="margin-top:18px">Respuesta</h2>
    <p class="respuesta">{_html.escape(d['respuesta'])}</p>
  </section>
  <section class="tarjeta">
    <h2>Fuentes citadas de la documentación</h2>
    {fragmentos_html}
  </section>
</main></body></html>""")


@router.get("/api/rag")
def rag_buscar(q: str = "", k: int = 3):
    """Busca fragmentos relevantes en la documentación del proyecto."""
    return {"fragmentos": rag.buscar(q, max(1, min(k, 6)))}


@router.post("/api/asistente")
def asistente(d: AsistenteIn, s=Depends(get_sesion)):
    return responder(s, d.pregunta, d.web)
