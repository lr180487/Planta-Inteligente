"""CRUD de documentos del conocimiento (RAG): crear, leer, actualizar,
borrar, vista previa (leer) y compartir (descargar con enlace)."""
from fastapi import APIRouter, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel

from ..servicios import documentos

router = APIRouter(tags=["documentos"])


class DocumentoIn(BaseModel):
    nombre: str = ""
    contenido: str = ""


@router.get("/api/documentos")
def listar_documentos():
    return documentos.listar()


@router.post("/api/documentos")
def agregar_documento(d: DocumentoIn):
    try:
        return documentos.guardar(d.nombre, d.contenido)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/api/documentos/subir")
async def subir_documento(archivo: UploadFile):
    """Sube PDF, Word, Excel, CSV, JSON, .md o .txt y lo suma al RAG."""
    from ..servicios.documentos import _FORMATOS as FORMATOS
    nombre = archivo.filename or "documento"
    if not nombre.lower().endswith(FORMATOS):
        raise HTTPException(status_code=400,
                            detail="Formato no admitido. Usa PDF, Word "
                                   "(.doc/.docx), Excel (.xlsx/.xls), CSV, "
                                   "JSON, .md o .txt.")
    datos = await archivo.read()
    try:
        return documentos.guardar_archivo(nombre, datos)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/api/documentos/{nombre}")
def leer_documento(nombre: str):
    """Contenido de un documento: vista previa y base para editar."""
    try:
        return documentos.leer(nombre)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/api/documentos/{nombre}")
def actualizar_documento(nombre: str, d: DocumentoIn):
    try:
        return documentos.actualizar(nombre, d.contenido)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/api/documentos/{nombre}/descargar")
def descargar_documento(nombre: str):
    """Enlace para compartir: descarga el documento en texto (.md)."""
    try:
        ruta, seguro = documentos.ruta_descarga(nombre)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return FileResponse(ruta, media_type="text/markdown", filename=seguro)


@router.get("/api/documentos/{nombre}/ver")
def ver_documento(nombre: str):
    """Página HTML del documento: se abre en una pestaña nueva tras cargarlo."""
    import html as _html
    import re as _re
    try:
        doc = documentos.leer(nombre)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    bloques = []
    for linea in doc["contenido"].splitlines():
        ln = _html.escape(linea)
        ln = _re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", ln)
        m = _re.match(r"#{1,3}\s+(.*)", ln)
        if m:
            bloques.append(f"<h2>{m.group(1)}</h2>")
        elif ln.strip().startswith("- "):
            bloques.append(f"<p class='li'>• {ln.strip()[2:]}</p>")
        elif ln.strip():
            ln = _re.sub(r"(https?://[^\s]+)", r"<a href='\1' target='_blank' rel='noopener'>\1</a>", ln)
            bloques.append(f"<p>{ln}</p>")
    cuerpo = "\n".join(bloques)
    kb = max(1, doc["bytes"] // 1024)
    return HTMLResponse(f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{_html.escape(nombre)} · Documento cargado · Planta Inteligente</title>
<style>
body{{font-family:Inter,system-ui,Arial,sans-serif;background:#f8fbff;color:#0f2237;margin:0;line-height:1.65}}
.barra{{background:#fff;border-bottom:1px solid #e0eaf6;padding:12px 20px;display:flex;gap:10px;align-items:center;flex-wrap:wrap}}
.logo{{font-weight:800}} .logo span{{background:#2563eb;color:#fff;border-radius:9px;padding:5px 9px}}
.chip{{font-size:.78rem;font-weight:700;background:#eff6ff;color:#1d4ed8;border:1px solid #dbeafe;border-radius:99px;padding:5px 10px}}
main{{max-width:860px;margin:22px auto;padding:0 18px 50px}}
.tarjeta{{background:#fff;border:1px solid #e0eaf6;border-radius:12px;padding:22px 26px}}
h1{{font-size:1.25rem;margin:0 0 4px}} h2{{font-size:1.02rem;margin:18px 0 5px;color:#0f2237}}
p{{margin:5px 0;color:#21344d}} p.li{{margin-left:14px}}
a{{color:#2563eb}}
.ok{{background:#ecfdf5;border:1px solid #a7f3d0;color:#065f46;border-radius:10px;padding:11px 14px;font-size:.9rem;margin-bottom:16px}}
</style></head><body>
<div class="barra"><span class="logo"><span>⚙️</span> Planta Inteligente</span>
<span class="chip">✅ Documento cargado correctamente</span>
<span class="chip">{doc["fragmentos"]} fragmento(s) en el conocimiento</span>
<span class="chip">{kb} KB</span></div>
<main><div class="ok">Este documento ya forma parte del conocimiento: puedes volver a la pestaña anterior y preguntarle al asistente sobre su contenido.</div>
<div class="tarjeta"><h1>📄 {_html.escape(nombre)}</h1>{cuerpo}</div></main>
</body></html>""")


@router.get("/api/documentos/{nombre}/compartir")
def compartir_documento(nombre: str):
    """Datos para compartir un documento: enlace de descarga directo."""
    try:
        documentos.leer(nombre)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    from urllib.parse import quote
    return {"nombre": nombre,
            "enlace": f"/api/documentos/{quote(nombre)}/descargar",
            "texto": f"Te comparto el documento «{nombre}» de Planta Inteligente."}


@router.delete("/api/documentos/{nombre}")
def borrar_documento(nombre: str):
    try:
        return documentos.eliminar(nombre)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
