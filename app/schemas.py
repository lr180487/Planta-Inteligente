"""Modelos de entrada/salida de la API (Pydantic)."""
from pydantic import BaseModel


class LecturaIn(BaseModel):
    dispositivo: str = "sensor-tanque-01"
    temperatura: float | None = None
    humedad: float | None = None
    nivel: float | None = None


class DispositivoIn(BaseModel):
    chip_id: str
    nombre: str = ""
    tipo: str = ""
    wifi: str = ""
    ip: str = ""
    conectado: bool = True


class SincronizarIn(BaseModel):
    dispositivos: list[DispositivoIn] = []


class NotificarIn(BaseModel):
    asunto: str = "Aviso de Planta Inteligente"
    mensaje: str = ""
    canales: list[str] = ["gmail", "telegram"]


class AsistenteIn(BaseModel):
    pregunta: str = ""
    web: bool = False


class PlcIn(BaseModel):
    nombre: str = "PLC principal"
    ip: str = "192.0.2.10"
    puerto: int = 502
    unidad: int = 1
    direccion: int = 0
    tipo_registro: str = "holding"   # holding | entrada | bobina | discreta
    intervalo_s: int = 5
    power: bool = True               # encendido/apagado del módulo


# ------------------------------ CAPTURA DE DATOS ------------------------------
class CapturaIn(BaseModel):
    """Captura multivariable desde sensores/SCADA/ESP32."""
    dispositivo: str = "sensor-scada-01"
    variables: dict[str, float] = {}
    umbrales: dict[str, float] = {}


class MqttMsgIn(BaseModel):
    """Mensaje capturado de un tema MQTT."""
    topic: str = "planta/sensores/scada"
    payload: str = ""


class AnalisisIn(BaseModel):
    """Ejecución del pipeline de detección sobre una variable."""
    variable: str = "temperatura"
    dispositivo: str | None = None
    ventana: int = 30
    umbral: float | None = None
    crear_alerta: bool = True
