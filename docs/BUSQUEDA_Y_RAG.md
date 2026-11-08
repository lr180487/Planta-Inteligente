# Búsqueda web (Tavily → DuckDuckGo) y RAG

## Búsqueda web
- **Principal: Tavily.** Si existe la variable `TAVILY_API_KEY`, las búsquedas van
  a `https://api.tavily.com/search` (con respuesta breve cuando la hay).
- **Respaldo: DuckDuckGo.** Sin clave, o si Tavily falla, se consulta la página
  pública de resultados de DuckDuckGo y se extraen título, enlace y resumen.
- Los resultados se guardan en caché (Upstash o LRU) para no repetir búsquedas.
- Endpoint: `GET /api/buscar?q=...&limite=5`
  → `{fuente, respuesta_breve, resultados:[{titulo, url, resumen}]}`.

## RAG (documentación del proyecto)
- Se indexan los `.md` de `docs/` con estas reglas (versión corregida):
  - **Un fragmento por sección** (cada encabezado con su título), de ~480 caracteres.
  - Las **tablas Markdown van fila a fila** y sin la fila de cabecera: antes, una
    sola tabla con todos los endpoints coincidía con cualquier pregunta.
  - Se **ignoran los bloques de código**.
  - Normalización del español: sin acentos y con raíz de palabra, para que
    *detecta/detección*, *conectado/conexión* o *despliego/despliegue* coincidan.
  - Puntuación **BM25** (con normalización por longitud), bonificación x1,7 si el
    término está en el título de la sección, sinónimos del dominio
    (aviso→notificación, alarma→umbral…) y coincidencias parciales de raíz.
  - **Cobertura mínima**: un fragmento solo se devuelve si cubre al menos la
    mitad de los términos de la pregunta, y se aplica un corte de relevancia.
    Si la documentación no habla del tema, la respuesta es “sin resultados”
    en vez de un fragmento cualquiera.
- Endpoints:
  - `GET /api/rag?q=...&k=3` → fragmentos relevantes con su fuente.
  - `POST /api/asistente` `{pregunta, web}` → combina la última lectura de la
    planta, los fragmentos de la documentación y, si se pide (`web: true` o la
    pregunta incluye “busca/en internet/en la web”), resultados web.
- El asistente no inventa cifras: si no hay datos, lo dice.

## Dónde se usa
En **Análisis Inteligente** (`ia.html`), panel “Búsqueda web y conocimiento del
proyecto”: botón **Buscar en la web** y botón **Preguntar con la documentación**.
El estado (proveedor activo y documentos indexados) sale de `GET /api/salud`.

## Configuración
En `.env` (ver `.env.ejemplo`):
```
TAVILY_API_KEY=tvly-...       # opcional; sin clave se usa DuckDuckGo
BUSQUEDA_MAX=5
```

## Agregar documentos (desde la web)
En **Análisis Inteligente → “Agregar documentos al conocimiento”** se puede:
- Pegar un texto con nombre (**se guarda como .md**), o **subir un archivo**:
  PDF, Word (.doc/.docx), Excel (.xlsx/.xls), CSV, JSON, .md o .txt.
  El sistema extrae el texto (páginas del PDF, párrafos y tablas de Word,
  hojas de Excel fila a fila, filas del CSV, claves del JSON) y lo guarda
  convertido a `.md` con el formato en el nombre (p. ej. `informe_pdf.md`),
  para que dos archivos con el mismo nombre y distinto formato no se pisen.
- Ver los documentos propios con sus fragmentos y **borrarlos**.

Por dentro: los archivos van a la carpeta `documentos/` del backend y el
índice RAG (que vigila cambios por fecha/tamaño) los incorpora sin reiniciar.
Es un CRUD completo: `GET /api/documentos` (listar),
`POST /api/documentos` (crear pegando texto),
`POST /api/documentos/subir` (crear desde archivo),
`GET /api/documentos/{nombre}` (leer: vista previa y editar),
`PUT /api/documentos/{nombre}` (actualizar),
`DELETE /api/documentos/{nombre}` (borrar) y
`GET /api/documentos/{nombre}/descargar` + `/compartir` (enlace para
compartir/descargar el documento).

## Resultados en pestaña nueva
- Al **cargar un documento** (subir un archivo o guardar), el frontend abre una
  pestaña nueva con `GET /api/documentos/{nombre}/ver`: página con el nombre,
  fragmentos y tamaño, y el contenido con formato (títulos, negritas, listas).
  Cada documento también tiene un botón “↗ Pestaña nueva”.
- Al **preguntar a la documentación** (botón “💬 Preguntar a la documentación”),
  se abre una pestaña nueva con `GET /api/asistente/ver?q=...`: página con la
  pregunta, la respuesta, las fuentes citadas (documento, sección y relevancia)
  y los datos de la planta si aplican. El resultado también sigue visible en
  `ia.html`, con un enlace “↗ Ver resultados en una pestaña nueva”.
En las citas, los fragmentos de estos documentos llevan `origen: "usuario"`.
