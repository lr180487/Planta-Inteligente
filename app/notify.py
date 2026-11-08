"""Notificaciones: Gmail (SMTP) y Telegram (Bot API).

Sin credenciales en el entorno, las notificaciones se registran como
"simuladas" en la base de datos para poder probar el flujo completo.
"""
import smtplib
from email.mime.text import MIMEText

import httpx

from . import config
from .db import Notificacion, sesion


def _registrar(canal, destino, asunto, mensaje, estado):
    s = sesion()
    try:
        s.add(Notificacion(canal=canal, destino=destino, asunto=asunto,
                           mensaje=mensaje, estado=estado))
        s.commit()
    finally:
        s.close()


def enviar_gmail(asunto, mensaje, destino=None):
    destino = destino or config.GMAIL_DESTINO or config.GMAIL_USER
    if not (config.GMAIL_USER and config.GMAIL_APP_PASSWORD and destino):
        _registrar("gmail", destino or "(sin destino)", asunto, mensaje, "simulado")
        return {"canal": "gmail", "estado": "simulado",
                "detalle": "Faltan GMAIL_USER / GMAIL_APP_PASSWORD / GMAIL_DESTINO"}
    try:
        msg = MIMEText(mensaje, "plain", "utf-8")
        msg["Subject"] = asunto
        msg["From"] = config.GMAIL_USER
        msg["To"] = destino
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as srv:
            srv.login(config.GMAIL_USER, config.GMAIL_APP_PASSWORD)
            srv.send_message(msg)
        _registrar("gmail", destino, asunto, mensaje, "enviado")
        return {"canal": "gmail", "estado": "enviado", "destino": destino}
    except Exception as e:  # red caída, claves inválidas, etc.
        _registrar("gmail", destino, asunto, mensaje, "error")
        return {"canal": "gmail", "estado": "error", "detalle": str(e)[:200]}


def enviar_telegram(mensaje):
    if not (config.TELEGRAM_BOT_TOKEN and config.TELEGRAM_CHAT_ID):
        _registrar("telegram", config.TELEGRAM_CHAT_ID or "(sin chat)", "", mensaje, "simulado")
        return {"canal": "telegram", "estado": "simulado",
                "detalle": "Faltan TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID"}
    try:
        r = httpx.post(
            f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": config.TELEGRAM_CHAT_ID, "text": mensaje}, timeout=10)
        ok = r.status_code == 200
        _registrar("telegram", config.TELEGRAM_CHAT_ID, "", mensaje,
                   "enviado" if ok else "error")
        return {"canal": "telegram", "estado": "enviado" if ok else "error"}
    except Exception as e:
        _registrar("telegram", config.TELEGRAM_CHAT_ID, "", mensaje, "error")
        return {"canal": "telegram", "estado": "error", "detalle": str(e)[:200]}


def notificar(asunto, mensaje, canales=("gmail", "telegram")):
    salida = []
    if "gmail" in canales:
        salida.append(enviar_gmail(asunto, mensaje))
    if "telegram" in canales:
        salida.append(enviar_telegram(f"{asunto}\n{mensaje}"))
    return salida
