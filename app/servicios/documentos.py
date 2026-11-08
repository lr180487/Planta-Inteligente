"""Documentos agregados por el usuario para el RAG.

Formatos aceptados al subir: PDF, Word (.docx y .doc), Excel (.xlsx/.xls),
CSV, JSON, Markdown y texto plano. De cada archivo se extrae el texto y se
guarda convertido a `.md` en la carpeta `documentos/` del backend; el
índice RAG lo incorpora solo ( detecta el cambio por fecha y tamaño).
"""
import csv
import io
import json
import os
import re

from .. import rag

_CARPETA = rag._DOCS_USUARIO
_MAX_CARACTERES = 400_000
_FORMATOS = (".pdf", ".doc", ".docx", ".xlsx", ".xls",
             ".csv", ".json", ".md", ".txt")


def _nombre_seguro(nombre, forzar_md=False):
    """Nombre de archivo simple y seguro: sin rutas ni caracteres raros."""
    nombre = os.path.basename((nombre or "").strip())
    nombre = re.sub(r"[^A-Za-z0-9áéíóúñüÁÉÍÓÚÑÜ _.-]+", "", nombre).strip()
    if not nombre:
        raise ValueError("El documento necesita un nombre.")
    if forzar_md:
        nombre = re.sub(r"\.[A-Za-z0-9]+$", "", nombre) + ".md"
    elif not nombre.lower().endswith((".md", ".txt")):
        nombre += ".md"
    return nombre


def _conteo(nombre):
    return sum(1 for f in rag.indexar() if f["fuente"] == nombre)


# ------------------------- extracción de texto -------------------------
def _de_pdf(datos):
    from pypdf import PdfReader
    lector = PdfReader(io.BytesIO(datos))
    partes = []
    for i, pagina in enumerate(lector.pages, 1):
        texto = (pagina.extract_text() or "").strip()
        if texto:
            partes.append(f"## Página {i}\n\n{texto}")
    return "\n\n".join(partes)


def _de_docx(datos):
    import docx
    doc = docx.Document(io.BytesIO(datos))
    partes = [p.text for p in doc.paragraphs if p.text.strip()]
    for tabla in doc.tables:  # cada fila de tabla, una línea
        for fila in tabla.rows:
            celdas = [c.text.strip() for c in fila.cells if c.text.strip()]
            if celdas:
                partes.append(" — ".join(celdas))
    return "\n\n".join(partes)


def _de_doc_legado(datos):
    """Word antiguo (.doc binario): intenta docx y, si no, rescata el texto."""
    try:
        return _de_docx(datos)
    except Exception:
        pass
    crudo = datos.decode("latin-1", errors="ignore")
    trozos = re.findall(r"[ -ÿ]{25,}", crudo)
    limpios = [t.strip() for t in trozos
               if sum(c.isalpha() for c in t) > 15 and " " in t]
    return "\n".join(dict.fromkeys(limpios))


def _filas_a_texto(filas, titulo):
    lineas = [f"## {titulo}"] if titulo else []
    for fila in filas:
        celdas = [str(c).strip() for c in fila if c is not None and str(c).strip()]
        if celdas:
            lineas.append(" — ".join(celdas))
    return "\n".join(lineas)


def _de_excel(datos, nombre):
    partes = []
    if nombre.lower().endswith(".xls"):
        import xlrd
        libro = xlrd.open_workbook(file_contents=datos)
        for hoja in libro.sheets():
            filas = (hoja.row_values(i) for i in range(hoja.nrows))
            partes.append(_filas_a_texto(filas, f"Hoja: {hoja.name}"))
    else:
        import openpyxl
        libro = openpyxl.load_workbook(io.BytesIO(datos), read_only=True,
                                       data_only=True)
        for hoja in libro.worksheets:
            partes.append(_filas_a_texto(hoja.iter_rows(values_only=True),
                                         f"Hoja: {hoja.title}"))
    return "\n\n".join(p for p in partes if p.strip())


def _decodificar(datos):
    for cod in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            return datos.decode(cod)
        except UnicodeDecodeError:
            continue
    return datos.decode("utf-8", errors="replace")


def _de_csv(datos):
    texto = _decodificar(datos)
    try:
        dialecto = csv.Sniffer().sniff(texto[:3000], delimiters=",;\t|")
    except csv.Error:
        dialecto = csv.excel
    filas = list(csv.reader(io.StringIO(texto), dialecto))
    return _filas_a_texto(filas, "Datos de la tabla")


def _aplanar_json(valor, prefijo="", salida=None):
    """Convierte un JSON en líneas 'clave: valor' fáciles de citar."""
    if salida is None:
        salida = []
    if isinstance(valor, dict):
        for k, v in valor.items():
            if isinstance(v, (dict, list)):
                salida.append(f"{prefijo}{k}:")
                _aplanar_json(v, prefijo + "  ", salida)
            else:
                salida.append(f"{prefijo}{k}: {v}")
    elif isinstance(valor, list):
        for v in valor:
            if isinstance(v, (dict, list)):
                _aplanar_json(v, prefijo, salida)
            else:
                salida.append(f"{prefijo}- {v}")
    else:
        salida.append(f"{prefijo}{valor}")
    return salida


def _de_json(datos):
    datos_json = json.loads(_decodificar(datos))
    if isinstance(datos_json, list) and datos_json and isinstance(datos_json[0], dict):
        # Lista de registros: una línea por registro, campo: valor
        lineas = []
        for reg in datos_json:
            lineas.append(" — ".join(f"{k}: {v}" for k, v in reg.items()
                                     if not isinstance(v, (dict, list))))
        return "\n".join(lineas)
    lineas = []
    _aplanar_json(datos_json, "", lineas)
    return "\n".join(lineas)


_EXTRACTORES = {
    ".pdf": lambda d, n: _de_pdf(d),
    ".docx": lambda d, n: _de_docx(d),
    ".doc": lambda d, n: _de_doc_legado(d),
    ".xlsx": _de_excel,
    ".xls": _de_excel,
    ".csv": lambda d, n: _de_csv(d),
    ".json": lambda d, n: _de_json(d),
    ".md": lambda d, n: _decodificar(d),
    ".txt": lambda d, n: _decodificar(d),
}


def extraer_texto(nombre, datos):
    ext = os.path.splitext(nombre or "")[1].lower()
    if ext not in _EXTRACTORES:
        raise ValueError("Formato no admitido. Usa PDF, Word (.doc/.docx), "
                         "Excel (.xlsx/.xls), CSV, JSON, .md o .txt.")
    try:
        return _EXTRACTORES[ext](datos, nombre)
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"No se pudo leer el archivo ({ext}): {e}")


# ------------------------------ guardado ------------------------------
def _guardar(nombre_md, contenido, origen=""):
    contenido = (contenido or "").strip()
    if len(contenido) < 40:
        raise ValueError("Del documento se extrajo muy poco texto "
                         "(mínimo 40 caracteres). Si es un PDF escaneado "
                         "como imagen, primero hay que pasarlo a texto.")
    if len(contenido) > _MAX_CARACTERES:
        contenido = contenido[:_MAX_CARACTERES]
    ruta = os.path.join(_CARPETA, nombre_md)
    with open(ruta, "w", encoding="utf8") as f:
        f.write(contenido + "\n")
    rag._indice["huella"] = None  # fuerza reindexar en la próxima consulta
    return {"ok": True, "nombre": nombre_md,
            "formato_origen": origen or nombre_md.rsplit(".", 1)[-1],
            "caracteres": len(contenido),
            "fragmentos": _conteo(nombre_md),
            "estado": rag.estado_rag()}


def guardar(nombre, contenido):
    """Documento pegado como texto desde la web."""
    return _guardar(_nombre_seguro(nombre), contenido, "texto")


def guardar_archivo(nombre, datos):
    """Archivo subido (PDF/Word/Excel/CSV/JSON/md/txt): extrae y guarda."""
    ext = os.path.splitext(nombre or "")[1].lower()
    texto = extraer_texto(nombre, datos)
    # El nombre guardado incluye el formato de origen (informe_pdf.md) para
    # que informe.pdf e informe.xlsx no se sobreescriban entre sí.
    base = re.sub(r"\.[A-Za-z0-9]+$", "", os.path.basename(nombre))
    nombre_md = _nombre_seguro(f"{base}_{ext.lstrip('.')}", forzar_md=True)
    titulo = base
    if not texto.lstrip().startswith("#"):
        texto = f"# {titulo}\n\n{texto}"
    return _guardar(nombre_md, texto, ext.lstrip("."))


def listar():
    salida = []
    if os.path.isdir(_CARPETA):
        for nombre in sorted(os.listdir(_CARPETA)):
            if nombre.endswith((".md", ".txt")):
                ruta = os.path.join(_CARPETA, nombre)
                salida.append({"nombre": nombre,
                               "bytes": os.path.getsize(ruta),
                               "fragmentos": _conteo(nombre)})
    return {"documentos": salida, "estado": rag.estado_rag()}


def eliminar(nombre):
    nombre = _nombre_seguro(nombre)
    ruta = os.path.join(_CARPETA, nombre)
    if not os.path.isfile(ruta):
        raise ValueError("Ese documento no existe.")
    os.remove(ruta)
    rag._indice["huella"] = None
    return {"ok": True, "nombre": nombre, "estado": rag.estado_rag()}


def leer(nombre):
    """Contenido completo de un documento (para vista previa y edición)."""
    nombre = _nombre_seguro(nombre)
    ruta = os.path.join(_CARPETA, nombre)
    if not os.path.isfile(ruta):
        raise ValueError("Ese documento no existe.")
    with open(ruta, encoding="utf8", errors="replace") as f:
        contenido = f.read()
    return {"nombre": nombre, "contenido": contenido,
            "bytes": os.path.getsize(ruta), "fragmentos": _conteo(nombre)}


def actualizar(nombre, contenido):
    """Reemplaza el contenido de un documento existente (CRUD: Update)."""
    nombre = _nombre_seguro(nombre)
    ruta = os.path.join(_CARPETA, nombre)
    if not os.path.isfile(ruta):
        raise ValueError("Ese documento no existe.")
    contenido = (contenido or "").strip()
    if len(contenido) < 40:
        raise ValueError("El contenido es muy corto (mínimo 40 caracteres).")
    if len(contenido) > _MAX_CARACTERES:
        contenido = contenido[:_MAX_CARACTERES]
    with open(ruta, "w", encoding="utf8") as f:
        f.write(contenido + "\n")
    rag._indice["huella"] = None
    return {"ok": True, "nombre": nombre, "caracteres": len(contenido),
            "fragmentos": _conteo(nombre), "estado": rag.estado_rag()}


def ruta_descarga(nombre):
    """Ruta física del documento para descargarlo/compartirlo."""
    nombre = _nombre_seguro(nombre)
    ruta = os.path.join(_CARPETA, nombre)
    if not os.path.isfile(ruta):
        raise ValueError("Ese documento no existe.")
    return ruta, nombre
