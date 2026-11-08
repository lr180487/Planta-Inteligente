# Arquitectura

```
┌────────────┐   Wi-Fi/MQTT   ┌──────────────┐  HTTP   ┌────────────────┐
│  ESP32 +   │ ─────────────▶ │  FastAPI     │ ◀────── │  Frontend HTML │
│  sensores  │  /api/esp32/*  │  (app/main)  │  /api/* │  (12 páginas)  │
└────────────┘                └──────┬───────┘         └────────────────┘
                                     │
        ┌──────────────┬─────────────┼──────────────┬───────────────┐
        ▼              ▼             ▼              ▼               ▼
   Postgres/SQLite   Upstash/LRU   Celery/QStash  Gmail SMTP    Telegram
   (datos)           (caché)       (tareas)       (correo)      (Bot API)
```

## Principio: cada capa tiene respaldo

Ninguna dependencia externa es obligatoria. Al arrancar, cada capa prueba su
servicio principal con un tiempo límite corto y, si no responde, usa el
respaldo local sin que la aplicación se caiga.

## Flujo de una lectura

1. Un ESP32 (o el simulador) envía `POST /api/lecturas`.
2. La lectura se guarda en BD y la última queda en caché.
3. Se encola `procesar_lectura` (Celery → QStash → local).
4. Si la temperatura supera el umbral (80 °C por defecto), la tarea
   `notificar` avisa por Gmail y Telegram.
5. El frontend consulta `/api/esp32/conectados` cada 10 s y avisa si
   aparece un ESP32 nuevo.
