"""Base de datos: motor y sesión.

Postgres si DATABASE_URL apunta a uno que responde; respaldo automático a
SQLite. Los modelos (tablas) viven en app/modelos.py; aquí se re-exportan
para compatibilidad con los imports existentes (from ..db import ...).
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from . import config
from .base import Base  # noqa: F401  (re-exportada para compatibilidad)


def _motor():
    """Intenta Postgres; si falla en 3 s, cae a SQLite."""
    if config.DATABASE_URL.startswith("postgres"):
        try:
            motor = create_engine(config.DATABASE_URL, pool_pre_ping=True,
                                  connect_args={"connect_timeout": 3})
            with motor.connect() as c:
                c.execute(text("SELECT 1"))
            return motor, "postgres"
        except Exception:
            pass  # respaldo a SQLite
    ruta = config.SQLITE_PATH
    motor = create_engine(f"sqlite:///{ruta}", connect_args={"check_same_thread": False})
    return motor, "sqlite"


engine, TIPO_BD = _motor()

# Registrar los modelos y crear las tablas que falten (import al final para
# evitar el ciclo db -> modelos -> db: modelos solo necesita Base).
from . import modelos  # noqa: E402
from .modelos import (Alerta, Captura, Dispositivo, Evento, Lectura,  # noqa: E402,F401
                      Notificacion, PlcModbus)

Base.metadata.create_all(engine)


def _migrar():
    """Añade columnas nuevas a tablas existentes (SQLite no lo hace solo)."""
    with engine.connect() as c:
        try:
            if TIPO_BD == "sqlite":
                cols = [r[1] for r in c.execute(text("PRAGMA table_info(plc_modbus)"))]
                if "power" not in cols:
                    c.execute(text("ALTER TABLE plc_modbus ADD COLUMN power BOOLEAN DEFAULT 1"))
                    c.execute(text("UPDATE plc_modbus SET power = 1 WHERE power IS NULL"))
            else:
                existe = c.execute(text(
                    "SELECT 1 FROM information_schema.columns "
                    "WHERE table_name='plc_modbus' AND column_name='power'")).fetchone()
                if not existe:
                    c.execute(text("ALTER TABLE plc_modbus ADD COLUMN power BOOLEAN DEFAULT TRUE"))
            c.commit()
        except Exception:
            c.rollback()


_migrar()
Sesion = sessionmaker(bind=engine, expire_on_commit=False)


def sesion():
    return Sesion()
