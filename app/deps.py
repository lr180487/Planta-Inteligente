"""Dependencias compartidas de FastAPI (sesión de BD por petición)."""
import datetime as dt

from .db import sesion


def ahora():
    return dt.datetime.utcnow()


def get_sesion():
    """Sesión de BD de vida corta: se cierra al terminar la petición."""
    s = sesion()
    try:
        yield s
    finally:
        s.close()
