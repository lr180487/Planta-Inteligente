"""Configuración por variables de entorno (con valores seguros por defecto).

Al importar, carga primero el archivo .env de la raíz del backend
(planta-backend/.env) sin pisar variables que ya vengan del sistema.
Todo es opcional: sin credenciales, cada capa usa su respaldo local
(SQLite, LRU en memoria, ejecución local, avisos simulados).
"""
import os


def _cargar_env():
    ruta = os.path.join(os.path.dirname(__file__), "..", ".env")
    try:
        with open(ruta, encoding="utf8") as f:
            for linea in f:
                linea = linea.strip()
                if not linea or linea.startswith("#") or "=" not in linea:
                    continue
                clave, _, valor = linea.partition("=")
                os.environ.setdefault(clave.strip(), valor.strip())
    except FileNotFoundError:
        pass  # sin .env: todo respaldo local


_cargar_env()


def env(nombre, defecto=""):
    return os.environ.get(nombre, defecto).strip()


# Base de datos: si DATABASE_URL apunta a Postgres se usa Postgres; en caso
# contrario (o si Postgres no responde) se cae automáticamente a SQLite.
DATABASE_URL = env("DATABASE_URL", "")            # postgresql://usuario:clave@host:5432/planta
SQLITE_PATH = env("SQLITE_PATH") or os.path.join(os.path.dirname(__file__), "..", "planta.db")

# Caché: Upstash (REST) si hay credenciales; si no, LRU en memoria.
UPSTASH_URL = env("UPSTASH_REDIS_REST_URL", "")
UPSTASH_TOKEN = env("UPSTASH_REDIS_REST_TOKEN", "")
LRU_MAXSIZE = int(env("LRU_MAXSIZE", "256"))

# Worker: Celery si hay broker; QStash si hay token; si no, ejecución local.
CELERY_BROKER_URL = env("CELERY_BROKER_URL", env("REDIS_URL", ""))
QSTASH_TOKEN = env("QSTASH_TOKEN", "")
QSTASH_DESTINO = env("QSTASH_DESTINO", "")        # URL pública del endpoint /api/tareas/qstash

# Notificaciones
GMAIL_USER = env("GMAIL_USER", "")
GMAIL_APP_PASSWORD = env("GMAIL_APP_PASSWORD", "")
GMAIL_DESTINO = env("GMAIL_DESTINO", "")
TELEGRAM_BOT_TOKEN = env("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = env("TELEGRAM_CHAT_ID", "")

# Detección de ESP32: se considera "recién conectado" si no se le veía hace más de esto.
ESP32_VENTANA_S = int(env("ESP32_VENTANA_S", "120"))
UMBRAL_TEMP = float(env("UMBRAL_TEMP", "80"))

# Búsqueda web: Tavily como principal; DuckDuckGo como respaldo sin clave.
TAVILY_API_KEY = env("TAVILY_API_KEY", "")
BUSQUEDA_MAX = int(env("BUSQUEDA_MAX", "5"))
