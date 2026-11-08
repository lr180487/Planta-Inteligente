"""Lógica de dispositivos ESP32: registro, detección de nuevos y eventos."""
from .. import config, tasks
from ..db import Dispositivo, Evento
from ..deps import ahora
from ..worker import tarea_notificar


def registrar_evento(s, tipo, detalle):
    s.add(Evento(tipo=tipo, detalle=detalle))


def avisar_nuevo_esp32(nombre_o_chip):
    tasks.enviar_tarea("notificar", tarea_notificar.run,
                       "📡 Nuevo ESP32 conectado",
                       f"Se detectó el dispositivo {nombre_o_chip} en la planta.")


def tocar_dispositivo(s, d):
    """Crea/actualiza un ESP32. Devuelve True si es una conexión NUEVA."""
    disp = s.get(Dispositivo, d.chip_id)
    t = ahora()
    nuevo = False
    if disp is None:
        disp = Dispositivo(chip_id=d.chip_id, creado_en=t)
        s.add(disp)
        nuevo = True
    elif disp.estado != "conectado" or \
            (t - (disp.ultimo_contacto or t)).total_seconds() > config.ESP32_VENTANA_S:
        nuevo = True
    disp.nombre, disp.tipo = d.nombre or disp.nombre, d.tipo or disp.tipo
    disp.wifi, disp.ip = d.wifi or disp.wifi, d.ip or disp.ip
    disp.estado = "conectado" if d.conectado else "desconectado"
    disp.ultimo_contacto = t
    return nuevo
