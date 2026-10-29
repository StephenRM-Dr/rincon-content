import time

from google import genai
from google.genai import errors

from rcontent.settings import settings

_client: genai.Client | None = None


def client() -> genai.Client:
    global _client
    if _client is None:
        if not settings.gemini_api_key:
            raise RuntimeError("Falta GEMINI_API_KEY")
        _client = genai.Client(api_key=settings.gemini_api_key)
    return _client


def generate(model: str, contents: str, config, intentos: int = 4):
    # Reintenta 429/5xx con backoff (free tier tiene RPM bajo)
    for i in range(intentos):
        try:
            return client().models.generate_content(model=model, contents=contents, config=config)
        except errors.APIError as e:
            if e.code in (429, 500, 503) and i < intentos - 1:
                time.sleep(15 * (i + 1))
                continue
            raise
