# CAPTURA DE DATOS — pipeline de ingesta, detección y alertas

Documento del módulo 04 (Servidor y Base de Datos · `backend.html`).

## Flujo completo

```
CAPTURA DE DATOS
  ESP32 · PLC · MQTT · Sensores · SCADA
  Temperatura, humedad, presión, vibración, corriente, caudal y variables de proceso
      ↓
PREPROCESAMIENTO
  Pandas · NumPy · normalización
  Limpieza, valores faltantes, ventanas temporales y extracción de características
      ↓
ALGORITMOS
  OCSVM (fronteras normales) · OCNN (patrones complejos) · Isolation Forest (aislamiento rápido)
      ↓
FUSIÓN Y VALIDACIÓN DE RESULTADOS
  Consenso · puntuaciones · umbrales
  Reducción de falsas alarmas y clasificación de severidad
      ↓
SISTEMA DE ALERTAS
  FastAPI · PostgreSQL · Dashboard
  MQTT · notificaciones · historial · auditoría
```

## Captura (router `app/routers/alertas.py`)

| Endpoint | Descripción |
|---|---|
| `POST /api/captura/sensores` | Captura multivariable desde sensores/SCADA (`CapturaIn`: dispositivo + variables + umbrales) |
| `POST /api/captura/scada` | Igual, marcando la fuente como `scada` |
| `POST /api/captura/esp32` | Igual, marcando la fuente como `esp32` |
| `POST /api/captura/mqtt` | Mensaje MQTT: `{topic, payload}` — payload número o JSON `{variable: valor}` |
| `POST /api/captura/plc` | Lee cada PLC conectado (Modbus TCP) y guarda su valor como captura |
| `GET /api/captura/series?variable=&limit=` | Serie temporal de una variable (para gráficos) |
| `GET /api/captura/fuentes` | Conteos por fuente + dispositivos conectados |

Cada captura se guarda en la tabla `capturas` (modelo `Captura`: dispositivo,
variable, valor, umbral, fuente, fecha) y se registra un `Evento` (auditoría).

## Preprocesamiento (`app/servicios/preproceso.py`)

- **Limpieza**: valores nulos/no finitos se interpolan linealmente; la serie
  de detección (`valores`) NO lleva filtro mediano para no borrar picos
  anómalos — el filtro mediano k=3 se aplica solo a `valores_limpios`,
  usado para estadísticas y medición de ruido
- **Valores faltantes**: interpolación lineal (con extrapolación por la media)
- **Ventanas temporales**: ventanas deslizantes de tamaño configurable (20/30/60)
- **Extracción de características**: media, desviación, mínimo, máximo,
  pendiente (regresión lineal), RMS, ruido de primera diferencia, picos (>2.5σ)
- **Normalización**: min-max a [0, 1] para OCSVM y OCNN

## Detección (`app/servicios/deteccion.py`, `app/servicios/ocnn.py`)

Tres algoritmos, cada uno con score 0..1 (0 = normal, 1 = anómalo):

1. **OCSVM** — `OneClassSVM(RBF, nu=0.05)` sobre las características. Aprende
   la frontera de lo normal; puntos fuera de la frontera son anómalos.
2. **OCNN** — One-Class CNN: autoencoder convolucional 1D escrito en NumPy
   (conv → ReLU → maxpool → dense → reconstrucción). Aprendizaje por
   reconstrucción: una ventana anómala se reconstruye mal y el error de
   reconstrucción (comparado con el de las normales) da el score. El
   backprop analítico está verificado contra gradiente numérico
   (`tests/test_ocnn.py`).
3. **Isolation Forest** — árboles de aislamiento sobre la ventana raw; los
   puntos atípicos se aislán rápido.

**Entrenamiento por período base**: los modelos se entrenan sobre los
primeros 75 % de la serie (período base) y puntajan la ventana reciente
(últimos 25 %), para que las anomalías recientes no contaminen el entrenamiento.
Los modelos se cachean en memoria por (variable, ventana, cantidad de puntos).

`POST /api/deteccion/analizar` — ejecuta el pipeline completo:
preproceso → 3 algoritmos → fusión → (si hay consenso) crea `Alerta`.

`GET /api/deteccion/ventana?variable=&ventana=` — resumen de preprocesamiento
de la ventana actual (para el panel visual).

`POST /api/deteccion/series-demo` — genera 120 puntos × 6 variables con
anomalías en los últimos 12 puntos (limpia el histórico demo previo para no
contaminar el período base).

## Fusión y validación (`app/servicios/fusion.py`)

- **Votos**: cada algoritmo vota anomalía si su score ≥ 0,55
- **Puntaje de fusión**: suma ponderada (OCSVM 0,3 · OCNN 0,4 · IF 0,3)
- **Reducción de falsas alarmas**: se confirma con ≥ 2 votos o puntaje ≥ 0,72;
  si no, la detección se descarta y se registra como "falsas alarmas reducidas"
- **Severidad**: `info` (sin alerta) · `media` · `alta` · `critica`
  (3/3 votos o puntaje ≥ 0,85). Un valor que supere un umbral físico escala
  la severidad.
- **Clasificación**: la fusión devuelve la clasificación textual
  ("Normal · sin alerta" … "Alerta crítica · actuar ya")

## Sistema de alertas (tabla `alertas`)

| Endpoint | Descripción |
|---|---|
| `GET /api/alertas?limit=` | Listar alertas (dispositivo, variable, severidad, valor, puntaje, votos, algoritmos, hora, leída) |
| `POST /api/alertas/simular` | Crear una alerta demo |
| `POST /api/alertas/{id}/leer` | Marcar como leída (registra `AUDITORIA_ALERTA`) |
| `GET /api/alertas/metricas` | Totales, por severidad, activas, promedio de puntaje, detecciones y falsas alarmas reducidas |

Las alertas confirmadas crean un `Evento` (`ALERTA_CREADA`); las detecciones
sin consenso registran `DETECCION` (eso es lo que se cuenta como "falsas
alarmas reducidas").

## Frontend (`iot-plataforma/backend.html`)

Página **CAPTURA DE DATOS** con el pipeline de 5 etapas: captura (fuentes +
formularios SCADA/MQTT/PLC + historial demo), preprocesamiento (ventana +
características + gráfico), algoritmos (OCSVM/OCNN/Isolation Forest con
barra de score), fusión (votos, severidad, falsas alarmas) y alertas
(tabla con Leer + auditoría). Refresca automáticamente cada 20 s.

## Pruebas

- `tests/test_ocnn.py` — gradiente analítico vs numérico y convergencia del
  autoencoder convolucional
- `tests/test_rag.py` — RAG (sin cambios)
- Endpoints verificados por curl: serie demo, análisis (scores + fusión +
  alerta), alertas, métricas
