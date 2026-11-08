# Datos y respaldos

## Base de datos: Postgres → SQLite

- Si `DATABASE_URL` (formato `postgresql://...`) responde en menos de 3 s,
  se usa **Postgres** con SQLAlchemy.
- Si no está definida o no responde, se crea **`planta.db` (SQLite)** junto
  al backend. Las tablas son las mismas: `dispositivos`, `lecturas`,
  `eventos`, `notificaciones`.

## Caché: Upstash → LRU

- Con `UPSTASH_REDIS_REST_URL` y `UPSTASH_REDIS_REST_TOKEN` se usa
  **Upstash** por su API REST.
- Sin credenciales, una **LRU en memoria** de 256 claves guarda las últimas
  lecturas (`ultima:<dispositivo>`, `lecturas:<n>`).

## Worker: Celery → QStash → local

- Con broker (`CELERY_BROKER_URL`, p. ej. Redis) las tareas van a **Celery**
  (`celery -A app.worker worker`).
- Si hay `QSTASH_TOKEN` y `QSTASH_DESTINO`, las tareas se publican con
  **QStash** hacia `POST /api/tareas/qstash`.
- Sin ninguno, las tareas se ejecutan **al momento en un hilo**: el flujo
  completo (alarmas y avisos) funciona igual en modo demo.

Consulta qué modo está activo en `GET /api/salud`.
