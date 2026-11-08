"""Caché: Upstash (REST) si hay credenciales; respaldo LRU en memoria."""
import json
from collections import OrderedDict

import httpx

from . import config


class LRUCache:
    """LRU sencillo y seguro para un solo proceso."""

    def __init__(self, maxsize=256):
        self.maxsize = maxsize
        self._d = OrderedDict()

    def get(self, clave):
        if clave not in self._d:
            return None
        self._d.move_to_end(clave)
        return self._d[clave]

    def set(self, clave, valor, ttl=None):
        self._d[clave] = valor
        self._d.move_to_end(clave)
        while len(self._d) > self.maxsize:
            self._d.popitem(last=False)

    def delete(self, clave):
        self._d.pop(clave, None)


class UpstashCache:
    """Upstash Redis vía API REST."""

    def __init__(self, url, token):
        self.url = url.rstrip("/")
        self.h = {"Authorization": f"Bearer {token}"}

    def get(self, clave):
        try:
            r = httpx.get(f"{self.url}/get/{clave}", headers=self.h, timeout=3)
            res = r.json().get("result")
            return json.loads(res) if res else None
        except Exception:
            return None

    def set(self, clave, valor, ttl=None):
        try:
            httpx.post(f"{self.url}/set/{clave}", headers=self.h,
                       content=json.dumps(valor), timeout=3)
        except Exception:
            pass

    def delete(self, clave):
        try:
            httpx.post(f"{self.url}/del/{clave}", headers=self.h, timeout=3)
        except Exception:
            pass


def crear_cache():
    if config.UPSTASH_URL and config.UPSTASH_TOKEN:
        try:
            c = UpstashCache(config.UPSTASH_URL, config.UPSTASH_TOKEN)
            c.set("__ping__", "ok")
            return c, "upstash"
        except Exception:
            pass  # respaldo LRU
    return LRUCache(config.LRU_MAXSIZE), "lru"


cache, TIPO_CACHE = crear_cache()
