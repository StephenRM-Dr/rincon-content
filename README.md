# rincon-content

Producción semanal de contenido para **@rincondigitalnet**. La publicación sigue siendo manual; todo lo demás se genera solo.

## Workflow

```
Lunes 05:23 (GitHub Actions, gratis)
│
├─ 1. BRIEF ─────────── Lee `brief.md` de Drive (si no existe, siembra el default)
│                       ↳ Claude lo ajusta vía conector de Drive según resultados
├─ 2. INVESTIGACIÓN ─── Gemini + Google Search → `_tendencias.md` con fuentes
├─ 3. PLAN ──────────── Gemini (JSON validado con Pydantic) → `_plan.json`
│                       2 carruseles · 1 reel · 1+ story set · mezcla 70/20/10
├─ 4. RENDER ────────── Plantillas HTML de marca → PNG (Playwright)
│                       carrusel 1080×1350 · story/portada reel 1080×1920
└─ 5. DRIVE ─────────── Sube por carpeta de semana / post
```

Tú: revisas en Drive, grabas el reel con el guion, publicas.
Claude: revisa captions, corrige y actualiza `brief.md` con lo que funcionó.

## Estructura en Drive

```
Rincón Digital · Contenido/
├── brief.md
└── 2026-S45_02-11/
    ├── _tendencias.md
    ├── _plan.json
    ├── 01_carrusel_que-hay-hoy/     slide_01..06.png · caption.txt · meta.json
    ├── 02_carrusel_haz-la-cuenta/
    ├── 03_reel_pedido-en-30-segundos/  portada.png · guion.md · caption.txt
    └── 04_story_demo-gratis/
```

## Setup

```bash
pip install -e .
python -m playwright install chromium
cp .env.example .env
```

1. **Gemini**: crea la key en https://aistudio.google.com/apikey → `GEMINI_API_KEY`.
2. **Drive (rclone, sin Google Cloud)**: instala rclone y corre `rclone config` → remote `gdrive`, tipo `drive`, client id/secret vacíos, scope `drive`, auto config `y`. Prueba: `rclone lsd gdrive:`.
3. **GitHub**: Settings → Secrets → `GEMINI_API_KEY` y `RCLONE_CONF` (contenido completo de `rclone config file`). Opcionales en Variables: `GEMINI_MODEL`, `POSTS_POR_SEMANA`.

> `drive.py` + `scripts/drive_auth.py` quedan como alternativa si algún día usas un proyecto propio de Google Cloud.

## Uso

```bash
python -m rcontent --dry-run --plan fixtures/plan_ejemplo.json   # solo render, sin APIs
python -m rcontent --dry-run                                     # Gemini, sin Drive
python -m rcontent                                               # completo
```

## Plantillas

`src/rcontent/templates/slide.html` — layouts: `portada`, `punto`, `lista`, `profit`, `comparacion`, `cta`. `**texto**` resalta en ámbar.

## Límites

- Free tier de Gemini: texto + grounding gratis; generación de imágenes no (por eso las slides son plantillas).
- Scope `drive.file`: la app solo ve lo que ella crea. No muevas la carpeta raíz fuera de "Mi unidad".
