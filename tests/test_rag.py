
"""Evaluación del RAG: cada pregunta debe citar el documento correcto
y los temas no documentados deben devolver lista vacía.

Ejecutar:
    uv run pytest tests/test_rag.py -v
    uv run python tests/test_rag.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import rag  # noqa: E402


CASOS = [
    ("¿Cómo se detecta un ESP32 conectado?", "ESP32.md"),
    ("¿Qué pasa si la temperatura supera el umbral?", "NOTIFICACIONES.md"),
    ("¿Cómo activo las notificaciones de Telegram?", "NOTIFICACIONES.md"),
    ("¿Qué agentes forman el sistema multiagente?", "MULTIAGENTE.md"),
    ("¿Qué hace el agente Verificador?", "MULTIAGENTE.md"),
    (
        "¿Cómo se guarda una lectura y qué respaldo hay si falla Postgres?",
        "DATOS_Y_RESPALDOS.md",
    ),
    ("¿Cómo despliego el proyecto?", "DESPLIEGUE.md"),
    ("¿Qué respaldo hay si Upstash no responde?", "DATOS_Y_RESPALDOS.md"),
    (
        "¿Cómo funciona el RAG y la búsqueda web con Tavily?",
        "BUSQUEDA_Y_RAG.md",
    ),
]

SIN_RESULTADO = [
    "¿Cómo preparo una receta de cocina al horno?",
    "¿Cuál es el broker MQTT y los temas?",
    "¿Quién ganó el mundial de fútbol?",
]


def test_fuente_correcta():
    """El primer resultado debe proceder del documento esperado."""
    for pregunta, esperada in CASOS:
        resultados = rag.buscar(pregunta, 3)

        assert resultados, f"Sin resultados para: {pregunta}"

        fuente_obtenida = resultados[0]["fuente"]

        assert fuente_obtenida == esperada, (
            f"{pregunta}: esperaba {esperada}, "
            f"llegó {fuente_obtenida}"
        )


def test_sin_resultado_si_no_esta_documentado():
    """Las preguntas fuera del conocimiento documental deben rechazarse."""
    for pregunta in SIN_RESULTADO:
        resultados = rag.buscar(pregunta, 3)

        assert resultados == [], (
            f"Devolvió fragmentos para un tema no documentado: {pregunta}"
        )


def test_texto_sin_markdown():
    """Los resultados no deben contener marcas Markdown sin limpiar."""
    for pregunta, _ in CASOS:
        resultados = rag.buscar(pregunta, 3)

        for fragmento in resultados:
            texto = fragmento["texto"]
            fuente = fragmento["fuente"]

            assert "**" not in texto and "##" not in texto, (
                f"Markdown sin limpiar en {fuente}: {texto[:60]}"
            )

            assert "```" not in texto, (
                f"Bloque de código Markdown en {fuente}: {texto[:60]}"
            )


def test_fragmentos_con_contenido():
    """Los fragmentos deben tener contenido y no incluir bloques de código."""
    for fragmento in rag.indexar():
        texto = fragmento["texto"]
        fuente = fragmento["fuente"]

        limpio = texto.replace("\n", " ").strip()

        assert len(limpio) >= 40, (
            f"Fragmento sin contenido en {fuente}"
        )

        # No confundir referencias textuales a herramientas como curl
        # con código ejecutable.
        assert "```" not in texto, (
            f"Bloque de código indexado como texto en {fuente}"
        )


def test_primer_resultado_no_es_solo_el_titulo():
    """El primer resultado debe contener información suficiente."""
    for pregunta, _ in CASOS:
        resultados = rag.buscar(pregunta, 1)

        assert resultados, (
            f"Sin resultados para: {pregunta}"
        )

        assert len(resultados[0]["texto"]) >= 60, (
            f"El primer resultado no tiene contenido para: {pregunta}"
        )


if __name__ == "__main__":
    test_fuente_correcta()
    test_sin_resultado_si_no_esta_documentado()
    test_texto_sin_markdown()
    test_fragmentos_con_contenido()
    test_primer_resultado_no_es_solo_el_titulo()

    print(
        f"RAG OK: {len(CASOS)} casos de fuente, "
        f"{len(SIN_RESULTADO)} rechazos correctos, "
        "texto limpio."
    )
