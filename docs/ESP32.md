# Detección de ESP32

## Cómo se detecta una conexión

1. Al unirse a la Wi-Fi, el ESP32 llama a `POST /api/esp32/anunciar`
   con su `chip_id`, nombre, tipo y red.
2. El backend lo busca en la tabla `dispositivos`:
   - Si **no existía**, o estaba desconectado, o no se le veía hace más
     de `ESP32_VENTANA_S` (120 s), se considera **conexión nueva**.
3. Se registra el evento `CONEXION_ESP32`, se encola un aviso
   (Gmail/Telegram) y el frontend, que consulta
   `GET /api/esp32/conectados` cada 10 s, muestra el aviso
   **“📡 Se detectó un ESP32 conectado: …”**.
4. El ESP32 mantiene su estado con `POST /api/esp32/heartbeat`.

## Desde la web (simulador)

En **Monitoreo en Campo → Conectar dispositivos y sensores ESP32**,
al pulsar *Conectar*, el dispositivo se guarda en el navegador y el
sincronizador (`api-sync.js`) lo envía a
`POST /api/dispositivos/sincronizar`, que aplica la misma detección.

## Probar a mano

```bash
curl -X POST http://localhost:8000/api/esp32/anunciar \
  -H "Content-Type: application/json" \
  -d '{"chip_id":"ESP32-PRUEBA1","nombre":"Sensor de prueba","tipo":"Temperatura"}'
curl http://localhost:8000/api/esp32/conectados
```
