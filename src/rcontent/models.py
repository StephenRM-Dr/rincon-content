from enum import Enum

from pydantic import BaseModel, Field


class Pilar(str, Enum):
    curiosidad = "curiosidad"
    valor = "valor"
    profit = "profit"
    prueba = "prueba"
    venta = "venta"


class Formato(str, Enum):
    carrusel = "carrusel"  # 1080x1350, 5-8 slides
    reel = "reel"          # guion + portada 1080x1920
    story = "story"        # 3-5 frames 1080x1920


class Layout(str, Enum):
    portada = "portada"
    punto = "punto"
    lista = "lista"
    profit = "profit"
    comparacion = "comparacion"
    cta = "cta"


class Fila(BaseModel):
    etiqueta: str
    valor: str


class Slide(BaseModel):
    layout: Layout
    kicker: str | None = Field(None, description="Etiqueta corta en mayúsculas sobre el título")
    titulo: str = Field(description="Máx 9 palabras. Usa **texto** para resaltar en ámbar")
    cuerpo: str | None = Field(None, description="Máx 30 palabras")
    items: list[str] = Field(default_factory=list, description="Solo layout lista: 3-5 ítems cortos")
    filas: list[Fila] = Field(default_factory=list, description="profit: cálculo línea a línea; comparacion: etiqueta=antes, valor=después")
    total: Fila | None = Field(None, description="Solo profit: resultado destacado")


class Toma(BaseModel):
    segundo: str = Field(description="Rango, ej. 0-3s")
    visual: str
    texto_pantalla: str
    voz: str | None = None


class Post(BaseModel):
    slug: str = Field(description="kebab-case, máx 5 palabras")
    formato: Formato
    pilar: Pilar
    dia_sugerido: str = Field(description="lunes..domingo + hora, ej. 'martes 12:00'")
    hook: str
    objetivo: str = Field(description="Qué debe sentir/hacer quien lo ve")
    slides: list[Slide] = Field(default_factory=list, description="carrusel 5-8; story 3-5; reel 1 (portada)")
    guion: list[Toma] = Field(default_factory=list, description="Solo reel: 4-8 tomas, 15-35s total")
    caption: str = Field(description="Primera línea = gancho. Máx 1200 caracteres, sin hashtags")
    hashtags: list[str] = Field(description="8-15, sin #, mezcla local + nicho")
    cta: str


class PlanSemanal(BaseModel):
    semana: str
    tema_central: str
    posts: list[Post]
