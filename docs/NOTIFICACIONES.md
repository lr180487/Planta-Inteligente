# Notificaciones: Gmail y Telegram

Se disparan cuando:

- La temperatura supera el umbral (80 °C por defecto, `UMBRAL_TEMP`).
- Se detecta un **ESP32 nuevo** conectado.
- Se llama manualmente a `POST /api/notificar`.

## Gmail

1. Activa la verificación en 2 pasos de tu cuenta Google.
2. Crea una **contraseña de aplicación** (Seguridad → Contraseñas de aplicaciones).
3. Define en el entorno:

```
GMAIL_USER=tu-correo@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
GMAIL_DESTINO=quien-recibe@ejemplo.com
```

El envío usa SMTP sobre SSL (`smtp.gmail.com:465`).

## Telegram

1. Habla con **@BotFather**, crea un bot y copia el token.
2. Escribe al bot y obtén tu `chat_id` (p. ej. con @userinfobot).

```
TELEGRAM_BOT_TOKEN=123456:ABCDEF
TELEGRAM_CHAT_ID=123456789
```

## Modo simulado

Sin credenciales, cada aviso se guarda en la tabla `notificaciones` con
estado **`simulado`** (o `error` si el envío falla), para poder auditar el
flujo sin enviar nada real.
