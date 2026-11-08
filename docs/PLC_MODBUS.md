# PLC por Modbus TCP/IP

En **Monitoreo en Campo** (`campo.html`), debajo de «Conectar dispositivos
y sensores ESP32», hay una tarjeta
«🏭 Dispositivos PLC · Modbus TCP/IP» para agregar PLC de la planta.

## Desde la web
1. Escribe nombre, **dirección IP**, **puerto** (habitual 502), **n.º de equipo**
   (unit id / esclavo), el **dato a leer** (registro, registro de solo lectura,
   salida o entrada encendida/apagada), su número y cada cuántos segundos
   consultarlo.
2. **🔌 Probar conexión**: prueba sin guardar y muestra el valor leído y la
   latencia, o el motivo del fallo (sin respuesta, conexión rechazada…).
3. **➕ Agregar PLC**: lo guarda y hace la primera lectura. Queda en la lista
   con su estado y última lectura, con botones **Leer ahora** y **Borrar**.
   También aparece en la lista general de dispositivos como
   `PLC · Modbus TCP/IP`.
4. **💾 Guardar cambios**: guarda los datos del formulario en el navegador
   (`iot_plc_cfg`), como el resto de páginas.

## API
| Método | Ruta | Qué hace |
|---|---|---|
| GET | `/api/plc` | Lista los PLC agregados con estado y última lectura |
| POST | `/api/plc/probar` | Prueba la conexión con los datos dados, sin guardar |
| POST | `/api/plc` | Agrega el PLC, lo guarda y hace la primera lectura |
| POST | `/api/plc/{id}/probar` | Lee ahora un PLC guardado y actualiza su estado |
| DELETE | `/api/plc/{id}` | Borra el PLC (y su reflejo en dispositivos) |

## Cómo funciona por dentro
- `app/servicios/plc.py`: abre un socket TCP contra IP:puerto y envía una
  petición **Modbus TCP** real (cabecera MBAP + función de lectura 0x03/0x04
  para registros, 0x01/0x02 para bobinas/entradas discretas), con tiempo de
  espera de 2,5 s. Si el PLC no responde, se informa el motivo; **no se
  inventan valores**.
- `app/routers/plc.py`: guarda el PLC en la tabla `plc_modbus`
  (`app/db.py`), registra el evento `CONEXION_PLC` y lo refleja en la tabla
  general de dispositivos (`plc-{id}`).
- Modelos de entrada en `app/schemas.py` (`PlcIn`).

Ejemplo:
```bash
curl -X POST http://localhost:8000/api/plc \
  -H 'Content-Type: application/json' \
  -d '{"nombre":"PLC envasado","ip":"192.0.2.50","puerto":502,"unidad":1,
       "direccion":0,"tipo_registro":"holding","intervalo_s":5}'
```
