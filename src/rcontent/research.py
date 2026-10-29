from datetime import date

from google.genai import types

from rcontent.gemini import generate
from rcontent.settings import settings

PROMPT = """Eres el investigador de contenido de una agencia de automatización para negocios pequeños.
Fecha: {hoy}. Región: San Cristóbal (Táchira, Venezuela) y Cúcuta (Colombia).

BRIEF DE LA MARCA:
{brief}

Investiga en la web (últimos 30 días cuando sea posible) y entrega en markdown:

## Tendencias de formato
Formatos de Reels/carruseles que están funcionando en Instagram para negocios de comida y servicios locales en LATAM. Qué estructura tienen (gancho, duración, estilo).

## Conversación del sector
Temas, quejas o cambios que hoy preocupan a dueños de restaurantes/delivery en Venezuela y Colombia (WhatsApp Business, apps de delivery y comisiones, pagos, costos, horas pico).

## Ángulos de automatización
5 ángulos que despierten curiosidad sobre automatizar pedidos, atención o cobros, sin sonar a venta.

## Ganchos
12 ganchos de primera línea (máx 12 palabras cada uno), en español venezolano neutro.

## Fechas y eventos
Fechas comerciales o eventos de las próximas 3 semanas aprovechables.

Reglas: cita solo lo que encuentres; si un dato no tiene fuente, no lo pongas como dato. Sé concreto."""


def investigar(brief: str) -> tuple[str, list[dict]]:
    """Devuelve (markdown de tendencias, fuentes[{titulo,url}])."""
    cfg = types.GenerateContentConfig(
        tools=[types.Tool(google_search=types.GoogleSearch())],
        temperature=0.6,
    )
    resp = generate(settings.gemini_model_research, PROMPT.format(hoy=date.today().isoformat(), brief=brief), cfg)

    fuentes: list[dict] = []
    gm = resp.candidates[0].grounding_metadata if resp.candidates else None
    for ch in (gm.grounding_chunks or []) if gm else []:
        if ch.web and ch.web.uri:
            fuentes.append({"titulo": ch.web.title or ch.web.uri, "url": ch.web.uri})

    md = resp.text or ""
    if fuentes:
        md += "\n\n## Fuentes\n" + "\n".join(f"- [{f['titulo']}]({f['url']})" for f in fuentes)
    return md, fuentes
