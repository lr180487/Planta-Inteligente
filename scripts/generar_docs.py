"""Genera la documentación del backend DESDE el código (sin desfasajes).

Salidas en docs/:
  ENDPOINTS.md       rutas reales de la app FastAPI (método, ruta, resumen)
  MODELOS.md         tablas y columnas de app/modelos.py
  ESQUEMA_DATOS.md   esquema SQL (CREATE TABLE) + esquemas JSON de app/schemas.py
  openapi.json       especificación OpenAPI completa de la app

Uso:  python3 scripts/generar_docs.py
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from app import modelos, schemas  # noqa: E402
from app.db import Base  # noqa: E402
from app.main import app  # noqa: E402

DOCS = pathlib.Path(__file__).resolve().parent.parent / "docs" / "generado"
DOCS.mkdir(exist_ok=True)


def endpoints():
    spec = app.openapi()
    filas = []
    for ruta, ops in spec.get("paths", {}).items():
        if not ruta.startswith("/api"):
            continue
        for metodo, op in ops.items():
            resumen = (op.get("description") or op.get("summary") or "").strip().split("\n")[0]
            filas.append((ruta, metodo.upper(), ", ".join(op.get("tags", [])), resumen))
    filas.sort()
    out = ["# Endpoints de la API (generado desde el código)\n",
           "Mismo origen que el frontend: `http://localhost:8000`. "
           "Generado con `python3 scripts/generar_docs.py`; no editar a mano.\n",
           "| Método | Ruta | Grupo | Qué hace |", "|---|---|---|---|"]
    for ruta, m, grupo, resumen in filas:
        out.append(f"| {m} | `{ruta}` | {grupo} | {resumen} |")
    out.append(f"\nTotal: **{len(filas)} endpoints** `/api/*`. "
               "Especificación completa en `docs/generado/openapi.json`.\n")
    return "\n".join(out)


def modelos_md():
    out = ["# Modelos de datos (generado desde app/modelos.py)\n",
           "Tablas SQLAlchemy. Motor: Postgres con respaldo a SQLite "
           "(`app/db.py`). No editar a mano.\n"]
    for tabla in Base.metadata.sorted_tables:
        clase = next((c for c in vars(modelos).values()
                      if isinstance(c, type) and getattr(c, "__tablename__", "") == tabla.name), None)
        doc = (clase.__doc__ or "").strip() if clase else ""
        out.append(f"## `{tabla.name}`" + (f" — {doc}" if doc else "") + "\n")
        out.append("| Columna | Tipo | Clave | Nulo | Por defecto |")
        out.append("|---|---|---|---|---|")
        for col in tabla.columns:
            clave = "PK" if col.primary_key else ("FK" if col.foreign_keys else "")
            arg = getattr(col.default, "arg", None) if col.default is not None else None
            defecto = "" if arg is None else (getattr(arg, "__name__", None) or str(arg))
            out.append(f"| `{col.name}` | {col.type} | {clave} | "
                       f"{'sí' if col.nullable else 'no'} | {defecto} |")
        out.append("")
    return "\n".join(out)


def esquema_md():
    from sqlalchemy.schema import CreateTable
    from app.db import engine
    out = ["# Esquema de datos (generado)\n",
           "## Esquema SQL (tal como se crea en la base de datos)\n", "```sql"]
    for tabla in Base.metadata.sorted_tables:
        out.append(str(CreateTable(tabla).compile(engine)).strip() + ";\n")
    out.append("```\n\n## Esquemas de entrada/salida (Pydantic, app/schemas.py)\n")
    for nombre in dir(schemas):
        clase = getattr(schemas, nombre)
        if isinstance(clase, type) and hasattr(clase, "model_json_schema") and clase.__module__ == schemas.__name__:
            out.append(f"### `{nombre}`\n\n```json")
            out.append(json.dumps(clase.model_json_schema(), indent=2, ensure_ascii=False))
            out.append("```\n")
    return "\n".join(out)


if __name__ == "__main__":
    (DOCS / "ENDPOINTS.md").write_text(endpoints(), encoding="utf8")
    (DOCS / "MODELOS.md").write_text(modelos_md(), encoding="utf8")
    (DOCS / "ESQUEMA_DATOS.md").write_text(esquema_md(), encoding="utf8")
    (DOCS / "openapi.json").write_text(json.dumps(app.openapi(), indent=2, ensure_ascii=False), encoding="utf8")
    print("Generados: docs/generado/ENDPOINTS.md · docs/generado/MODELOS.md · docs/generado/ESQUEMA_DATOS.md · docs/generado/openapi.json")
