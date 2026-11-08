"""PLC por Modbus TCP/IP: conexión real por socket y lectura de registros.

Modbus TCP = cabecera MBAP (7 bytes) + PDU (función + datos), puerto 502
habitual. Se soporta leer 1 registro/bobina:
  0x03 registros holding · 0x04 registros de entrada
  0x01 bobinas · 0x02 entradas discretas
Si el PLC no responde, se informa el motivo (sin inventar datos).
"""
import socket
import struct
import time

FUNCIONES = {"holding": 0x03, "entrada": 0x04, "bobina": 0x01, "discreta": 0x02}


def leer_registro(ip, puerto, unidad, direccion, tipo_registro="holding", timeout=2.5):
    """Lee 1 valor del PLC. Devuelve (ok, valor, mensaje, latencia_ms)."""
    fc = FUNCIONES.get(tipo_registro, 0x03)
    inicio = time.time()
    try:
        with socket.create_connection((ip, int(puerto)), timeout=timeout) as sock:
            sock.settimeout(timeout)
            # MBAP: transacción 1, protocolo 0, longitud 6, unidad
            pdu = struct.pack(">HH", int(direccion), 1)  # dirección + cantidad
            peticion = struct.pack(">HHHB", 1, 0, 2 + len(pdu), int(unidad)) + bytes([fc]) + pdu
            sock.sendall(peticion)
            cabecera = sock.recv(7)
            if len(cabecera) < 7:
                return False, None, "El equipo respondió con una cabecera incompleta.", _ms(inicio)
            _tid, _proto, longitud, _uid = struct.unpack(">HHHB", cabecera)
            cuerpo = b""
            while len(cuerpo) < longitud - 1:
                trozo = sock.recv(longitud - 1 - len(cuerpo))
                if not trozo:
                    break
                cuerpo += trozo
            latencia = _ms(inicio)
            if not cuerpo:
                return False, None, "El equipo no envió datos de respuesta.", latencia
            if cuerpo[0] & 0x80:  # excepción Modbus
                cod = cuerpo[1] if len(cuerpo) > 1 else 0
                return False, None, f"El PLC devolvió un error Modbus (código {cod}).", latencia
            if fc in (0x03, 0x04):
                if len(cuerpo) < 4:
                    return False, None, "Respuesta de registro incompleta.", latencia
                valor = struct.unpack(">H", cuerpo[2:4])[0]
            else:  # bobinas/discretas: bit 0 del primer byte de datos
                valor = (cuerpo[2] & 0x01) if len(cuerpo) > 2 else 0
            return True, valor, "Lectura correcta.", latencia
    except socket.timeout:
        return False, None, f"Sin respuesta de {ip}:{puerto} (tiempo de espera agotado). Revisa que el PLC esté encendido y en la misma red.", _ms(inicio)
    except ConnectionRefusedError:
        return False, None, f"Conexión rechazada por {ip}:{puerto}: el equipo responde, pero no acepta Modbus TCP en ese puerto.", _ms(inicio)
    except OSError as e:
        return False, None, f"No se pudo conectar con {ip}:{puerto}: {e.strerror or e}. Revisa la dirección y la red.", _ms(inicio)


def _ms(inicio):
    return int((time.time() - inicio) * 1000)


def probar(ip, puerto, unidad, direccion, tipo_registro):
    ok, valor, mensaje, latencia = leer_registro(ip, puerto, unidad, direccion, tipo_registro)
    return {"ok": ok, "valor": valor, "mensaje": mensaje, "latencia_ms": latencia}
