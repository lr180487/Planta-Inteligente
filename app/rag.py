"""RAG corregido sobre la documentación del proyecto (carpeta docs/).

Mejoras frente a la primera versión:
- Normalización del español: sin acentos y con raíz de palabra
  (detecta/detección/conectado/conexión puntúan como lo mismo).
- Fragmentos por SECCIÓN (cada encabezado es un fragmento), no párrafos
  mezclados de todo el documento.
- Las tablas Markdown se indexan FILA A FILA: antes una sola tabla con
  todos los endpoints coincidía con cualquier pregunta y tapaba lo demás.
- Puntuación BM25 con normalización por longitud, bonificación si el
  término está en el título/encabezado y coincidencia parcial de raíces.
- Umbral mínimo de relevancia: si la documentación no habla del tema,
  devuelve lista vacía en lugar de un fragmento cualquiera.
Sin servicios externos; se reindexa solo si cambia algún archivo.
"""
import difflib
import math
import os
import re
import unicodedata
from collections import Counter

_DOCS = os.path.join(os.path.dirname(__file__), "..", "docs")
# Documentos agregados por el usuario (desde la web): mismo índice RAG.
_DOCS_USUARIO = os.path.join(os.path.dirname(__file__), "..", "documentos")
os.makedirs(_DOCS_USUARIO, exist_ok=True)
_CARPETAS = ((_DOCS, "sistema"), (_DOCS_USUARIO, "usuario"))
_indice = {"huella": None, "fragmentos": []}

_PARADAS = set("""
el la los las un una unos unas de del en y o u a con por para que es se su al lo
como mas pero sus le ya este esta esto estos estas entre cuando muy sin sobre
tambien me hasta hay donde quien quienes cual cuales cuanto cuanta es son ser
fue han he has han hace hacen haciendo hecho poder puede pueden debe deben
cual como cuando donde quien que porque pues bien mal solo sola vez cada otro
todo toda todos todas cosa cosas algo nada alguien nadie siempre nunca
otra otros otras mismo misma eso esa ese aquel aquella ello
""".split())

# Sinónimos del dominio (tras normalizar): amplían la consulta
_SINONIMOS = {
    "aviso": ["notificacion", "alerta"], "avisos": ["notificacion", "alerta"],
    "alerta": ["notificacion", "aviso", "alarma"], "alarma": ["umbral", "notificacion"],
    "conectar": ["conexion", "anunciar"], "conectado": ["conexion"],
    "instalar": ["despliegue", "configurar"], "desplegar": ["despliegue"],
    "guardar": ["almacenar", "base", "datos"], "guardado": ["almacenar"],
    "celery": ["worker", "tarea"], "trabajador": ["worker"],
}


def _sin_acentos(texto):
    return "".join(c for c in unicodedata.normalize("NFD", texto.lower())
                   if unicodedata.category(c) != "Mn")


def _raiz(palabra):
    """Raíz aproximada en español: quita sufijos verbales y plurales."""
    p = palabra
    # Familias que deben coincidir: detección/detecta, conexión/conectado
    p = p.replace("eccion", "ect").replace("xion", "ct")
    for suf in ("aciones", "acion", "uciones", "ucion", "mente", "ando",
                "iendo", "ados", "adas", "idos", "idas", "ado", "ada",
                "ido", "ida", "ares", "eres", "ires", "ar", "er", "ir",
                "es", "s"):
        if p.endswith(suf) and len(p) - len(suf) >= 4:
            p = p[:-len(suf)]
            break
    if len(p) > 4 and p[-1] in "aeo":
        p = p[:-1]
    return p


def _tokens(texto):
    base = _sin_acentos(texto)
    return [_raiz(t) for t in re.findall(r"[a-z0-9]{3,}", base)
            if t not in _PARADAS and _raiz(t) not in _PARADAS]


def _huella():
    datos = []
    for carpeta, origen in _CARPETAS:
        if not os.path.isdir(carpeta):
            continue
        for nombre in sorted(os.listdir(carpeta)):
            if nombre.endswith((".md", ".txt")):
                ruta = os.path.join(carpeta, nombre)
                datos.append((ruta, nombre, origen,
                              os.path.getmtime(ruta), os.path.getsize(ruta)))
    return tuple(datos)


def _fragmentar(nombre, texto):
    """Un fragmento por sección; las tablas van fila a fila."""
    fragmentos = []
    titulo_doc = re.sub(r"\.(md|txt)$", "", nombre).replace("_", " ")
    seccion = titulo_doc
    bufer = []
    en_tabla = [False]  # para saltar la fila de cabecera de cada tabla
    en_codigo = [False]  # dentro de un bloque ``` no se indexa

    def volcar():
        contenido = "\n".join(bufer).strip()
        bufer.clear()
        if len(contenido) < 25:
            return
        # Partir secciones largas en trozos de ~480 caracteres por párrafo
        trozos, actual = [], ""
        for parrafo in re.split(r"\n\s*\n", contenido):
            parrafo = parrafo.strip()
            if not parrafo:
                continue
            if len(actual) + len(parrafo) > 480 and actual:
                trozos.append(actual); actual = parrafo
            else:
                actual = (actual + "\n" + parrafo).strip()
        if actual:
            trozos.append(actual)
        for trozo in trozos:
            limpio = _limpiar(trozo)
            if len(limpio) < 40 or limpio == _limpiar(seccion):
                continue  # título suelto o resto sin contenido: no es citable
            fragmentos.append({"fuente": nombre, "seccion": seccion,
                               "texto": trozo})

    for linea in texto.splitlines():
        if re.match(r"^#{1,3}\s", linea):
            en_tabla[0] = False
            volcar()
            seccion = re.sub(r"^#+\s*", "", linea).strip() or seccion
            # El encabezado identifica la sección; no se mete en el texto,
            # así ningún fragmento es "solo el título" sin contenido.
        elif linea.lstrip().startswith("|") and "---" not in linea:
            # Cada fila de tabla es su propio fragmento (contexto mínimo).
            # La primera fila de cada tabla es la cabecera: no se indexa.
            primera_fila = not en_tabla[0]
            en_tabla[0] = True
            celdas = [c.strip(" `") for c in linea.strip().strip("|").split("|")]
            celdas = [c for c in celdas if c]
            volcar()
            if primera_fila:
                continue
            if len(celdas) >= 2:
                fragmentos.append({
                    "fuente": nombre, "seccion": seccion,
                    "texto": " — ".join(celdas)})
        elif linea.strip().startswith("```"):
            en_tabla[0] = False
            en_codigo[0] = not en_codigo[0]
            continue
        elif en_codigo[0]:
            continue  # dentro de un bloque de código: no se indexa
        else:
            if linea.strip():
                en_tabla[0] = False
            bufer.append(linea)
    volcar()
    return fragmentos


def indexar():
    huella = _huella()
    if _indice["huella"] == huella and _indice["fragmentos"]:
        return _indice["fragmentos"]
    fragmentos = []
    for ruta, nombre, origen, _, _ in huella:
        texto = open(ruta, encoding="utf8", errors="replace").read()
        for frag in _fragmentar(nombre, texto):
            frag["origen"] = origen
            encabezado = frag["fuente"] + " " + frag["seccion"]
            frag["tokens"] = Counter(_tokens(frag["texto"]))
            frag["tokens_titulo"] = Counter(_tokens(encabezado))
            frag["n_tokens"] = max(1, sum(frag["tokens"].values()))
            fragmentos.append(frag)
    _indice.update(huella=huella, fragmentos=fragmentos)
    return fragmentos



def _limpiar(texto):
    """Quita la sintaxis Markdown: la respuesta debe leerse como texto claro."""
    lineas = []
    for ln in texto.splitlines():
        ln = re.sub(r"^#+\s*", "", ln.strip())
        if ln:
            lineas.append(ln)
    s = " ".join(lineas)
    s = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", s)   # [texto](url) -> texto
    s = s.replace("**", "").replace("*", "").replace("`", "")
    return re.sub(r"\s+", " ", s).strip()


def estado_rag():
    fragmentos = indexar()
    return {"documentos": len(set(f["fuente"] for f in fragmentos)),
            "documentos_usuario": len(set(
                f["fuente"] for f in fragmentos if f.get("origen") == "usuario")),
            "fragmentos": len(fragmentos)}


def _similitud(a, b):
    """1 exacto; ~0,85 si comparten raíz/prefijo; 0 si no se parecen."""
    if a == b:
        return 1.0
    comun = 0
    for x, y in zip(a, b):
        if x == y:
            comun += 1
        else:
            break
    if comun >= 5 and min(len(a), len(b)) >= 5:
        return 0.85
    if min(len(a), len(b)) >= 5 and difflib.SequenceMatcher(None, a, b).ratio() > 0.84:
        return 0.8
    return 0.0


def buscar(pregunta, top=3):
    """Fragmentos relevantes de la documentación (BM25 + títulos)."""
    fragmentos = indexar()
    if not fragmentos:
        return []
    consulta = list(dict.fromkeys(_tokens(pregunta)))
    # Expandir sinónimos del dominio
    extra = []
    for t in consulta:
        extra += [_raiz(_sin_acentos(s)) for s in _SINONIMOS.get(t, [])]
    consulta_ext = consulta + [t for t in extra if t not in consulta]
    if not consulta:
        return []

    n = len(fragmentos)
    promedio_len = sum(f["n_tokens"] for f in fragmentos) / n
    df = Counter()
    for f in fragmentos:
        for t in set(f["tokens"]) | set(f["tokens_titulo"]):
            df[t] += 1

    def idf(t):
        return math.log(1 + (n - df.get(t, 0) + 0.5) / (df.get(t, 0) + 0.5))

    k1, b = 1.5, 0.75
    salida = []
    for f in fragmentos:
        puntos = 0.0
        cubiertos = 0  # términos originales de la pregunta presentes aquí
        for t in consulta_ext:
            peso_consulta = 1.0 if t in consulta else 0.55  # sinónimo vale menos
            # Mejor coincidencia del término en este fragmento
            mejor_tf, mejor_sim = 0, 0.0
            for tok, tf in f["tokens"].items():
                sim = _similitud(t, tok)
                if sim > 0 and tf * sim > mejor_tf * max(mejor_sim, 0.01):
                    mejor_tf, mejor_sim = tf, sim
            en_titulo = any(_similitud(t, tok) > 0 for tok in f["tokens_titulo"])
            if mejor_sim == 0 and not en_titulo:
                continue
            if t in consulta:
                cubiertos += 1
            # Si solo está en el título, cuenta como media aparición
            tf = (mejor_tf * mejor_sim) if mejor_sim > 0 else 0.6
            bm25 = idf(t) * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * f["n_tokens"] / promedio_len))
            puntos += peso_consulta * bm25 * (1.7 if en_titulo else 1.0)
        cobertura = cubiertos / len(consulta) if consulta else 0
        if puntos > 0 and cobertura >= 0.5:
            salida.append({"fuente": f["fuente"],
                           "origen": f.get("origen", "sistema"),
                           "seccion": f["seccion"],
                           "texto": _limpiar(f["texto"])[:700],
                           "relevancia": round(puntos, 2)})
    salida.sort(key=lambda x: -x["relevancia"])
    if not salida:
        return []
    # Umbral: fuera lo poco relevante frente al mejor resultado
    corte = max(1.2, salida[0]["relevancia"] * 0.32)
    elegidos, vistos = [], set()
    for f in salida:
        huella_f = (f["fuente"], f["texto"][:80])
        if f["relevancia"] < corte or huella_f in vistos:
            continue
        vistos.add(huella_f)
        elegidos.append(f)
        if len(elegidos) >= top:
            break
    return elegidos
