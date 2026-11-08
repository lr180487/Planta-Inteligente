# Sistema multiagente

El Análisis Inteligente funciona como un sistema de agentes especializados
que se reparten el trabajo antes de responder al usuario.

## Agentes

| Agente | Rol | Entrada | Salida |
|---|---|---|---|
| 🧭 Planificador | Descompone la pregunta en pasos | Pregunta del usuario | Plan de análisis |
| 📥 Recolector | Junta lecturas de campo, proceso y servidor | Plan | Datos crudos verificados |
| 🧮 Calculista | Promedios, máximos, tendencias y comparaciones | Datos | Cifras calculadas |
| 💬 Respondedor | Redacta la respuesta en lenguaje simple | Cifras | Respuesta borrador |
| ✅ Verificador | Contrasta cada cifra con la BD antes de entregar | Borrador + BD | Respuesta aprobada |

## Flujo

```
Pregunta ─▶ Planificador ─▶ Recolector ─▶ Calculista ─▶ Respondedor ─▶ Verificador ─▶ Usuario
```

El Verificador es obligatorio: si una cifra no coincide con lo guardado en
la base de datos, la respuesta se corrige antes de mostrarse. Por eso el
resumen del Dashboard muestra el sello **"verificado ✅ · confianza ALTA"**.

## Respaldo del asistente

En Configuración se define un servicio principal y uno de **respaldo**:
si el principal no responde, el sistema cambia automáticamente al de
respaldo sin interrumpir al usuario (y puede avisar del cambio).

## Archivos de esta documentación

- [ARQUITECTURA.md](ARQUITECTURA.md) — mapa general del sistema
- [API.md](API.md) — endpoints del backend
- [DATOS_Y_RESPALDOS.md](DATOS_Y_RESPALDOS.md) — BD, caché y worker
- [NOTIFICACIONES.md](NOTIFICACIONES.md) — Gmail y Telegram
- [ESP32.md](ESP32.md) — conexión y detección de dispositivos
- [DESPLIEGUE.md](DESPLIEGUE.md) — cómo publicar todo
