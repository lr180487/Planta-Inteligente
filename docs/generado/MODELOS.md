# Modelos de datos (generado desde app/modelos.py)

Tablas SQLAlchemy. Motor: Postgres con respaldo a SQLite (`app/db.py`). No editar a mano.

## `alertas` — Alerta del sistema de detección (alarma confirmada por la fusión).

| Columna | Tipo | Clave | Nulo | Por defecto |
|---|---|---|---|---|
| `id` | INTEGER | PK | no |  |
| `dispositivo` | VARCHAR(120) |  | sí |  |
| `variable` | VARCHAR(60) |  | sí |  |
| `tipo` | VARCHAR(60) |  | sí | anomalia |
| `severidad` | VARCHAR(20) |  | sí | media |
| `valor` | FLOAT |  | sí |  |
| `umbral` | FLOAT |  | sí |  |
| `puntaje` | FLOAT |  | sí | 0.0 |
| `algoritmos` | VARCHAR(200) |  | sí |  |
| `votos` | VARCHAR(20) |  | sí |  |
| `mensaje` | VARCHAR(255) |  | sí |  |
| `leida` | BOOLEAN |  | sí | False |
| `creada_en` | DATETIME |  | sí | utcnow |

## `capturas` — Captura de datos multivariable (sensores/SCADA/PLC/MQTT/ESP32).

Una fila = una variable medida en un instante: temperatura, humedad,
presión, vibración, corriente, caudal y cualquier otra variable de
proceso. Es la tabla base del pipeline de CAPTURA DE DATOS.

| Columna | Tipo | Clave | Nulo | Por defecto |
|---|---|---|---|---|
| `id` | INTEGER | PK | no |  |
| `dispositivo` | VARCHAR(120) |  | sí |  |
| `variable` | VARCHAR(60) |  | sí |  |
| `valor` | FLOAT |  | sí |  |
| `umbral` | FLOAT |  | sí |  |
| `fuente` | VARCHAR(30) |  | sí | scada |
| `creada_en` | DATETIME |  | sí | utcnow |

## `dispositivos` — Dispositivo conocido (ESP32, PLC reflejado, sensores).

| Columna | Tipo | Clave | Nulo | Por defecto |
|---|---|---|---|---|
| `chip_id` | VARCHAR(64) | PK | no |  |
| `nombre` | VARCHAR(120) |  | sí |  |
| `tipo` | VARCHAR(60) |  | sí |  |
| `wifi` | VARCHAR(120) |  | sí |  |
| `ip` | VARCHAR(64) |  | sí |  |
| `estado` | VARCHAR(20) |  | sí | conectado |
| `creado_en` | DATETIME |  | sí | utcnow |
| `ultimo_contacto` | DATETIME |  | sí | utcnow |

## `eventos` — Hechos relevantes: conexiones, alarmas, PLC agregados...

| Columna | Tipo | Clave | Nulo | Por defecto |
|---|---|---|---|---|
| `id` | INTEGER | PK | no |  |
| `tipo` | VARCHAR(60) |  | sí |  |
| `detalle` | TEXT |  | sí |  |
| `creado_en` | DATETIME |  | sí | utcnow |

## `lecturas` — Lectura de sensores guardada (con fecha, para histórico).

| Columna | Tipo | Clave | Nulo | Por defecto |
|---|---|---|---|---|
| `id` | INTEGER | PK | no |  |
| `dispositivo` | VARCHAR(64) |  | sí |  |
| `temperatura` | FLOAT |  | sí |  |
| `humedad` | FLOAT |  | sí |  |
| `nivel` | FLOAT |  | sí |  |
| `creada_en` | DATETIME |  | sí | utcnow |

## `notificaciones` — Aviso enviado o simulado (Gmail/Telegram) con su resultado.

| Columna | Tipo | Clave | Nulo | Por defecto |
|---|---|---|---|---|
| `id` | INTEGER | PK | no |  |
| `canal` | VARCHAR(20) |  | sí |  |
| `destino` | VARCHAR(160) |  | sí |  |
| `asunto` | VARCHAR(200) |  | sí |  |
| `mensaje` | TEXT |  | sí |  |
| `estado` | VARCHAR(20) |  | sí | simulado |
| `creada_en` | DATETIME |  | sí | utcnow |

## `plc_modbus` — PLC agregado desde Monitoreo en Campo (Modbus TCP/IP).

| Columna | Tipo | Clave | Nulo | Por defecto |
|---|---|---|---|---|
| `id` | INTEGER | PK | no |  |
| `nombre` | VARCHAR(120) |  | sí |  |
| `ip` | VARCHAR(64) |  | sí |  |
| `puerto` | INTEGER |  | sí | 502 |
| `unidad` | INTEGER |  | sí | 1 |
| `direccion` | INTEGER |  | sí | 0 |
| `tipo_registro` | VARCHAR(20) |  | sí | holding |
| `intervalo_s` | INTEGER |  | sí | 5 |
| `estado` | VARCHAR(20) |  | sí | sin probar |
| `ultimo_valor` | VARCHAR(60) |  | sí |  |
| `ultimo_contacto` | DATETIME |  | sí |  |
| `creado_en` | DATETIME |  | sí | utcnow |
