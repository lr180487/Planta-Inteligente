# API (FastAPI)

> Lista completa y siempre al día (generada desde el código):
> [generado/ENDPOINTS.md](generado/ENDPOINTS.md) · especificación
> [generado/openapi.json](generado/openapi.json) · modelos en
> [generado/MODELOS.md](generado/MODELOS.md) y esquema en
> [generado/ESQUEMA_DATOS.md](generado/ESQUEMA_DATOS.md).


Documentación interactiva automática en `/docs` (Swagger) al arrancar el servidor.

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/salud` | Estado y qué respaldo está activo (BD, caché, worker) |
| GET | `/api/estado` | Contadores: dispositivos, conectados, lecturas, eventos |
| POST | `/api/lecturas` | Guarda una lectura; si supera el umbral, encola alarma |
| GET | `/api/lecturas?limite=20` | Últimas lecturas (con caché) |
| POST | `/api/dispositivos/sincronizar` | Sincroniza los ESP32 del navegador; detecta nuevos |
| GET | `/api/dispositivos` | Todos los dispositivos conocidos |
| POST | `/api/esp32/anunciar` | Un ESP32 anuncia que se conectó a la Wi-Fi |
| POST | `/api/esp32/heartbeat` | Latido para mantenerlo "conectado" |
| GET | `/api/esp32/conectados` | ESP32 conectados ahora |
| GET/POST/DELETE | `/api/plc`, `/api/plc/{id}` | PLC por Modbus TCP/IP (ver PLC_MODBUS.md) |
| POST | `/api/plc/probar`, `/api/plc/{id}/probar` | Probar conexión / leer ahora un PLC |
| POST | `/api/notificar` | Envía aviso por Gmail y/o Telegram (encolado) |
| POST | `/api/tareas/qstash` | Receptor de tareas QStash |
| GET | `/api/eventos` | Últimos eventos (conexiones, alarmas) |
| POST | `/api/captura/sensores` · `/api/captura/scada` · `/api/captura/esp32` | Captura multivariable (ver CAPTURA_DATOS.md) |
| POST | `/api/captura/mqtt` | Captura de un mensaje MQTT (payload número o JSON) |
| POST | `/api/captura/plc` | Lee cada PLC conectado y guarda su valor |
| GET | `/api/captura/series` · `/api/captura/fuentes` | Serie temporal / conteos por fuente |
| POST | `/api/deteccion/analizar` | Pipeline completo: preproceso + OCSVM/OCNN/Isolation Forest + fusión |
| GET | `/api/deteccion/ventana` | Resumen de preprocesamiento de la ventana actual |
| POST | `/api/deteccion/series-demo` | Genera el historial de ejemplo con anomalías |
| GET | `/api/alertas` · `/api/alertas/metricas` | Listar alertas / métricas del sistema |
| POST | `/api/alertas/simular` · `/api/alertas/{id}/leer` | Alerta demo / marcar leída (auditoría) |

## Ejemplo

```bash
curl -X POST http://localhost:8000/api/esp32/anunciar \
  -H "Content-Type: application/json" \
  -d '{"chip_id":"ESP32-7F3A21","nombre":"Sensor del tanque 02","tipo":"Temperatura","wifi":"PlantaWiFi"}'
# -> {"ok":true,"detectado_nuevo":true}
```
