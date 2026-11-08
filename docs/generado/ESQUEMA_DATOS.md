# Esquema de datos (generado)

## Esquema SQL (tal como se crea en la base de datos)

```sql
CREATE TABLE alertas (
	id INTEGER NOT NULL, 
	dispositivo VARCHAR(120), 
	variable VARCHAR(60), 
	tipo VARCHAR(60), 
	severidad VARCHAR(20), 
	valor FLOAT, 
	umbral FLOAT, 
	puntaje FLOAT, 
	algoritmos VARCHAR(200), 
	votos VARCHAR(20), 
	mensaje VARCHAR(255), 
	leida BOOLEAN, 
	creada_en DATETIME, 
	PRIMARY KEY (id)
);

CREATE TABLE capturas (
	id INTEGER NOT NULL, 
	dispositivo VARCHAR(120), 
	variable VARCHAR(60), 
	valor FLOAT, 
	umbral FLOAT, 
	fuente VARCHAR(30), 
	creada_en DATETIME, 
	PRIMARY KEY (id)
);

CREATE TABLE dispositivos (
	chip_id VARCHAR(64) NOT NULL, 
	nombre VARCHAR(120), 
	tipo VARCHAR(60), 
	wifi VARCHAR(120), 
	ip VARCHAR(64), 
	estado VARCHAR(20), 
	creado_en DATETIME, 
	ultimo_contacto DATETIME, 
	PRIMARY KEY (chip_id)
);

CREATE TABLE eventos (
	id INTEGER NOT NULL, 
	tipo VARCHAR(60), 
	detalle TEXT, 
	creado_en DATETIME, 
	PRIMARY KEY (id)
);

CREATE TABLE lecturas (
	id INTEGER NOT NULL, 
	dispositivo VARCHAR(64), 
	temperatura FLOAT, 
	humedad FLOAT, 
	nivel FLOAT, 
	creada_en DATETIME, 
	PRIMARY KEY (id)
);

CREATE TABLE notificaciones (
	id INTEGER NOT NULL, 
	canal VARCHAR(20), 
	destino VARCHAR(160), 
	asunto VARCHAR(200), 
	mensaje TEXT, 
	estado VARCHAR(20), 
	creada_en DATETIME, 
	PRIMARY KEY (id)
);

CREATE TABLE plc_modbus (
	id INTEGER NOT NULL, 
	nombre VARCHAR(120), 
	ip VARCHAR(64), 
	puerto INTEGER, 
	unidad INTEGER, 
	direccion INTEGER, 
	tipo_registro VARCHAR(20), 
	intervalo_s INTEGER, 
	estado VARCHAR(20), 
	ultimo_valor VARCHAR(60), 
	ultimo_contacto DATETIME, 
	creado_en DATETIME, 
	PRIMARY KEY (id)
);

```

## Esquemas de entrada/salida (Pydantic, app/schemas.py)

### `AnalisisIn`

```json
{
  "description": "Ejecución del pipeline de detección sobre una variable.",
  "properties": {
    "variable": {
      "default": "temperatura",
      "title": "Variable",
      "type": "string"
    },
    "dispositivo": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Dispositivo"
    },
    "ventana": {
      "default": 30,
      "title": "Ventana",
      "type": "integer"
    },
    "umbral": {
      "anyOf": [
        {
          "type": "number"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Umbral"
    },
    "crear_alerta": {
      "default": true,
      "title": "Crear Alerta",
      "type": "boolean"
    }
  },
  "title": "AnalisisIn",
  "type": "object"
}
```

### `AsistenteIn`

```json
{
  "properties": {
    "pregunta": {
      "default": "",
      "title": "Pregunta",
      "type": "string"
    },
    "web": {
      "default": false,
      "title": "Web",
      "type": "boolean"
    }
  },
  "title": "AsistenteIn",
  "type": "object"
}
```

### `CapturaIn`

```json
{
  "description": "Captura multivariable desde sensores/SCADA/ESP32.",
  "properties": {
    "dispositivo": {
      "default": "sensor-scada-01",
      "title": "Dispositivo",
      "type": "string"
    },
    "variables": {
      "additionalProperties": {
        "type": "number"
      },
      "default": {},
      "title": "Variables",
      "type": "object"
    },
    "umbrales": {
      "additionalProperties": {
        "type": "number"
      },
      "default": {},
      "title": "Umbrales",
      "type": "object"
    }
  },
  "title": "CapturaIn",
  "type": "object"
}
```

### `DispositivoIn`

```json
{
  "properties": {
    "chip_id": {
      "title": "Chip Id",
      "type": "string"
    },
    "nombre": {
      "default": "",
      "title": "Nombre",
      "type": "string"
    },
    "tipo": {
      "default": "",
      "title": "Tipo",
      "type": "string"
    },
    "wifi": {
      "default": "",
      "title": "Wifi",
      "type": "string"
    },
    "ip": {
      "default": "",
      "title": "Ip",
      "type": "string"
    },
    "conectado": {
      "default": true,
      "title": "Conectado",
      "type": "boolean"
    }
  },
  "required": [
    "chip_id"
  ],
  "title": "DispositivoIn",
  "type": "object"
}
```

### `LecturaIn`

```json
{
  "properties": {
    "dispositivo": {
      "default": "sensor-tanque-01",
      "title": "Dispositivo",
      "type": "string"
    },
    "temperatura": {
      "anyOf": [
        {
          "type": "number"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Temperatura"
    },
    "humedad": {
      "anyOf": [
        {
          "type": "number"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Humedad"
    },
    "nivel": {
      "anyOf": [
        {
          "type": "number"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Nivel"
    }
  },
  "title": "LecturaIn",
  "type": "object"
}
```

### `MqttMsgIn`

```json
{
  "description": "Mensaje capturado de un tema MQTT.",
  "properties": {
    "topic": {
      "default": "planta/sensores/scada",
      "title": "Topic",
      "type": "string"
    },
    "payload": {
      "default": "",
      "title": "Payload",
      "type": "string"
    }
  },
  "title": "MqttMsgIn",
  "type": "object"
}
```

### `NotificarIn`

```json
{
  "properties": {
    "asunto": {
      "default": "Aviso de Planta Inteligente",
      "title": "Asunto",
      "type": "string"
    },
    "mensaje": {
      "default": "",
      "title": "Mensaje",
      "type": "string"
    },
    "canales": {
      "default": [
        "gmail",
        "telegram"
      ],
      "items": {
        "type": "string"
      },
      "title": "Canales",
      "type": "array"
    }
  },
  "title": "NotificarIn",
  "type": "object"
}
```

### `PlcIn`

```json
{
  "properties": {
    "nombre": {
      "default": "PLC principal",
      "title": "Nombre",
      "type": "string"
    },
    "ip": {
      "default": "192.0.2.10",
      "title": "Ip",
      "type": "string"
    },
    "puerto": {
      "default": 502,
      "title": "Puerto",
      "type": "integer"
    },
    "unidad": {
      "default": 1,
      "title": "Unidad",
      "type": "integer"
    },
    "direccion": {
      "default": 0,
      "title": "Direccion",
      "type": "integer"
    },
    "tipo_registro": {
      "default": "holding",
      "title": "Tipo Registro",
      "type": "string"
    },
    "intervalo_s": {
      "default": 5,
      "title": "Intervalo S",
      "type": "integer"
    }
  },
  "title": "PlcIn",
  "type": "object"
}
```

### `SincronizarIn`

```json
{
  "$defs": {
    "DispositivoIn": {
      "properties": {
        "chip_id": {
          "title": "Chip Id",
          "type": "string"
        },
        "nombre": {
          "default": "",
          "title": "Nombre",
          "type": "string"
        },
        "tipo": {
          "default": "",
          "title": "Tipo",
          "type": "string"
        },
        "wifi": {
          "default": "",
          "title": "Wifi",
          "type": "string"
        },
        "ip": {
          "default": "",
          "title": "Ip",
          "type": "string"
        },
        "conectado": {
          "default": true,
          "title": "Conectado",
          "type": "boolean"
        }
      },
      "required": [
        "chip_id"
      ],
      "title": "DispositivoIn",
      "type": "object"
    }
  },
  "properties": {
    "dispositivos": {
      "default": [],
      "items": {
        "$ref": "#/$defs/DispositivoIn"
      },
      "title": "Dispositivos",
      "type": "array"
    }
  },
  "title": "SincronizarIn",
  "type": "object"
}
```
