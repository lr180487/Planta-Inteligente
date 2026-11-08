"""Modelos de datos (tablas SQLAlchemy).

Separados de app/db.py: aquí solo se declara QUÉ se guarda; el motor, la
sesión y el respaldo Postgres->SQLite viven en app/db.py. La documentación
generada (docs/MODELOS.md y docs/ESQUEMA_DATOS.md) se construye leyendo
estas mismas clases, así que nunca queda desfasada.
"""
import datetime as dt

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text

from .base import Base


class Dispositivo(Base):
    """Dispositivo conocido (ESP32, PLC reflejado, sensores)."""
    __tablename__ = "dispositivos"
    chip_id = Column(String(64), primary_key=True)
    nombre = Column(String(120), default="")
    tipo = Column(String(60), default="")
    wifi = Column(String(120), default="")
    ip = Column(String(64), default="")
    estado = Column(String(20), default="conectado")  # conectado | desconectado
    creado_en = Column(DateTime, default=dt.datetime.utcnow)
    ultimo_contacto = Column(DateTime, default=dt.datetime.utcnow)


class PlcModbus(Base):
    """PLC agregado desde Monitoreo en Campo (Modbus TCP/IP)."""
    __tablename__ = "plc_modbus"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(120), default="")
    ip = Column(String(64), default="")
    puerto = Column(Integer, default=502)
    unidad = Column(Integer, default=1)          # id de esclavo / unit id
    direccion = Column(Integer, default=0)       # dirección del registro a leer
    tipo_registro = Column(String(20), default="holding")
    intervalo_s = Column(Integer, default=5)     # cada cuánto consultar
    power = Column(Boolean, default=True)        # encendido/apagado del módulo
    estado = Column(String(20), default="sin probar")  # conectado | sin respuesta
    ultimo_valor = Column(String(60), default="")
    ultimo_contacto = Column(DateTime, nullable=True)
    creado_en = Column(DateTime, default=dt.datetime.utcnow)


class Captura(Base):
    """Captura de datos multivariable (sensores/SCADA/PLC/MQTT/ESP32).

    Una fila = una variable medida en un instante: temperatura, humedad,
    presión, vibración, corriente, caudal y cualquier otra variable de
    proceso. Es la tabla base del pipeline de CAPTURA DE DATOS.
    """
    __tablename__ = "capturas"
    id = Column(Integer, primary_key=True, autoincrement=True)
    dispositivo = Column(String(120), index=True)
    variable = Column(String(60), index=True)
    valor = Column(Float)
    umbral = Column(Float)
    fuente = Column(String(30), default="scada")  # esp32 | plc | mqtt | sensores | scada
    creada_en = Column(DateTime, default=dt.datetime.utcnow, index=True)


class Lectura(Base):
    """Lectura de sensores guardada (con fecha, para histórico)."""
    __tablename__ = "lecturas"
    id = Column(Integer, primary_key=True, autoincrement=True)
    dispositivo = Column(String(64), index=True)
    temperatura = Column(Float, nullable=True)
    humedad = Column(Float, nullable=True)
    nivel = Column(Float, nullable=True)
    creada_en = Column(DateTime, default=dt.datetime.utcnow, index=True)


class Evento(Base):
    """Hechos relevantes: conexiones, alarmas, PLC agregados..."""
    __tablename__ = "eventos"
    id = Column(Integer, primary_key=True, autoincrement=True)
    tipo = Column(String(60), index=True)          # CONEXION_ESP32, ALARMA, ...
    detalle = Column(Text, default="")
    creado_en = Column(DateTime, default=dt.datetime.utcnow, index=True)


class Notificacion(Base):
    """Aviso enviado o simulado (Gmail/Telegram) con su resultado."""
    __tablename__ = "notificaciones"
    id = Column(Integer, primary_key=True, autoincrement=True)
    canal = Column(String(20))                     # gmail | telegram
    destino = Column(String(160), default="")
    asunto = Column(String(200), default="")
    mensaje = Column(Text, default="")
    estado = Column(String(20), default="simulado")  # enviado | simulado | error
    creada_en = Column(DateTime, default=dt.datetime.utcnow)


class Alerta(Base):
    """Alerta del sistema de detección (alarma confirmada por la fusión)."""
    __tablename__ = "alertas"
    id = Column(Integer, primary_key=True, autoincrement=True)
    dispositivo = Column(String(120), index=True)
    variable = Column(String(60), index=True)
    tipo = Column(String(60), default="anomalia")  # anomalia | umbral
    severidad = Column(String(20), default="media")  # info | media | alta | critica
    valor = Column(Float)
    umbral = Column(Float)
    puntaje = Column(Float, default=0.0)           # score de fusión 0..1
    algoritmos = Column(String(200), default="")   # OCSVM+OCNN+IsolationForest
    votos = Column(String(20), default="")         # votos de los algoritmos, ej. "2/3"
    mensaje = Column(String(255), default="")
    leida = Column(Boolean, default=False)
    creada_en = Column(DateTime, default=dt.datetime.utcnow, index=True)
