from google.genai import types

from rcontent.gemini import generate
from rcontent.models import PlanSemanal
from rcontent.settings import settings

PROMPT = """Eres el director creativo de @rincondigitalnet. Diseña el plan de contenido de la semana {semana}.

BRIEF:
{brief}

INVESTIGACIÓN DE ESTA SEMANA:
{tendencias}

Entrega exactamente {n} posts con esta mezcla:
- 2 carruseles (uno de curiosidad/valor y uno de profit "haz la cuenta")
- 1 reel (demo o detrás de cámara, con guion toma a toma y 1 slide 'portada')
- {extra}

Reglas de slides:
- Carrusel: 5-8 slides. Slide 1 = layout 'portada' con el gancho. Último = layout 'cta'.
- Profit: usa layout 'profit' con filas de cálculo (supuesto → resultado) y 'total'. Primera fila debe aclarar que es ejemplo. Matemática correcta.
- 'comparacion': filas con etiqueta=antes y valor=después (3-4 filas).
- Títulos máx 9 palabras, cuerpo máx 30. Resalta 1-3 palabras clave con **asteriscos**.
- Español neutro venezolano, tuteo. Sin jerga técnica.
- Caption: primera línea = gancho distinto al de la portada; párrafos cortos; termina con el CTA. Sin hashtags dentro.
- Profit y venta no pueden ser más de la mitad de los posts."""


def planificar(brief: str, tendencias: str, semana: str) -> PlanSemanal:
    n = max(settings.posts_por_semana, 3)
    extra_n = n - 3
    extra = f"{extra_n} post(s) más: al menos 1 story set de 3-5 frames (pilar venta o prueba)" if extra_n else "nada más"
    cfg = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_json_schema=PlanSemanal.model_json_schema(),
        temperature=0.8,
    )
    resp = generate(settings.gemini_model, PROMPT.format(semana=semana, brief=brief, tendencias=tendencias, n=n, extra=extra), cfg)
    plan = PlanSemanal.model_validate_json(resp.text)
    plan.semana = semana
    return plan
