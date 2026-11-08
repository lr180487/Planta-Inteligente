# Endpoints de la API (generado desde el código)

Mismo origen que el frontend: `http://localhost:8000`. Generado con `python3 scripts/generar_docs.py`; no editar a mano.

| Método | Ruta | Grupo | Qué hace |
|---|---|---|---|
| GET | `/api/alertas` | captura | Listar Alertas |
| GET | `/api/alertas/metricas` | captura | Alertas Metricas |
| POST | `/api/alertas/simular` | captura | Alerta Simular |
| POST | `/api/alertas/{id}/leer` | captura | Alerta Leer |
| POST | `/api/asistente` | asistente | Asistente |
| GET | `/api/asistente/ver` | asistente | Página HTML con el resultado de preguntar a la documentación (pestaña nueva). |
| GET | `/api/buscar` | asistente | Búsqueda web: Tavily primero; si falla o no hay clave, DuckDuckGo. |
| POST | `/api/captura/esp32` | captura | Captura Esp32 |
| GET | `/api/captura/fuentes` | captura | Captura Fuentes |
| POST | `/api/captura/mqtt` | captura | Un mensaje MQTT: payload número o JSON {variable: valor}. |
| POST | `/api/captura/plc` | captura | Lee cada PLC conectado y guarda su valor como captura. |
| POST | `/api/captura/scada` | captura | Captura Scada |
| POST | `/api/captura/sensores` | captura | Captura Sensores |
| GET | `/api/captura/series` | captura | Captura Series |
| POST | `/api/deteccion/analizar` | captura | Ejecuta el pipeline completo sobre la ventana reciente de una variable. |
| POST | `/api/deteccion/series-demo` | captura | Genera un historial de ejemplo con anomalías para probar el pipeline. |
| GET | `/api/deteccion/ventana` | captura | Ventana Actual |
| GET | `/api/dispositivos` | dispositivos | Dispositivos |
| POST | `/api/dispositivos/sincronizar` | dispositivos | Sincronizar |
| GET | `/api/documentos` | documentos | Listar Documentos |
| POST | `/api/documentos` | documentos | Agregar Documento |
| POST | `/api/documentos/subir` | documentos | Sube PDF, Word, Excel, CSV, JSON, .md o .txt y lo suma al RAG. |
| DELETE | `/api/documentos/{nombre}` | documentos | Borrar Documento |
| GET | `/api/documentos/{nombre}` | documentos | Contenido de un documento: vista previa y base para editar. |
| PUT | `/api/documentos/{nombre}` | documentos | Actualizar Documento |
| GET | `/api/documentos/{nombre}/compartir` | documentos | Datos para compartir un documento: enlace de descarga directo. |
| GET | `/api/documentos/{nombre}/descargar` | documentos | Enlace para compartir: descarga el documento en texto (.md). |
| GET | `/api/documentos/{nombre}/ver` | documentos | Página HTML del documento: se abre en una pestaña nueva tras cargarlo. |
| POST | `/api/esp32/anunciar` | dispositivos | Un ESP32 real llamaría a este endpoint al unirse a la Wi-Fi. |
| GET | `/api/esp32/conectados` | dispositivos | Esp32 Conectados |
| POST | `/api/esp32/heartbeat` | dispositivos | Heartbeat |
| GET | `/api/estado` | sistema | Estado |
| GET | `/api/eventos` | sistema | Eventos |
| GET | `/api/lecturas` | lecturas | Listar Lecturas |
| POST | `/api/lecturas` | lecturas | Crear Lectura |
| POST | `/api/notificar` | notificaciones | Notificar Api |
| GET | `/api/plc` | plc | Listar |
| POST | `/api/plc` | plc | Agregar |
| POST | `/api/plc/probar` | plc | Prueba la conexión con los datos del formulario, sin guardar. |
| DELETE | `/api/plc/{plc_id}` | plc | Borrar |
| POST | `/api/plc/{plc_id}/probar` | plc | Probar Guardado |
| GET | `/api/rag` | asistente | Busca fragmentos relevantes en la documentación del proyecto. |
| GET | `/api/salud` | sistema | Salud |
| POST | `/api/tareas/qstash` | notificaciones | Destino para QStash cuando no hay Celery. |

Total: **44 endpoints** `/api/*`. Especificación completa en `docs/generado/openapi.json`.
