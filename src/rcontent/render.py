import json
import re
from pathlib import Path

from jinja2 import Environment, PackageLoader, select_autoescape
from markupsafe import Markup, escape
from playwright.sync_api import sync_playwright

from rcontent.models import Formato, PlanSemanal, Post
from rcontent.settings import settings

SIZES = {Formato.carrusel: (1080, 1350), Formato.story: (1080, 1920), Formato.reel: (1080, 1920)}


def _hl(texto: str) -> Markup:
    # **palabra** → resaltado ámbar
    return Markup(re.sub(r"\*\*(.+?)\*\*", r'<span class="hl">\1</span>', str(escape(texto))))


env = Environment(loader=PackageLoader("rcontent", "templates"), autoescape=select_autoescape())
env.filters["hl"] = _hl
TPL = env.get_template("slide.html")


def carpeta_post(i: int, p: Post) -> str:
    return f"{i:02d}_{p.formato.value}_{p.slug}"


def _caption(p: Post) -> str:
    tags = " ".join(f"#{t.lstrip('#')}" for t in p.hashtags)
    return f"{p.caption.strip()}\n\n{tags}\n"


def _guion_md(p: Post) -> str:
    out = [f"# Guion — {p.hook}", "", f"**Objetivo:** {p.objetivo}", "", "| Tiempo | Visual | Texto en pantalla | Voz |", "|---|---|---|---|"]
    out += [f"| {t.segundo} | {t.visual} | {t.texto_pantalla} | {t.voz or '—'} |" for t in p.guion]
    return "\n".join(out) + "\n"


def render_plan(plan: PlanSemanal, out_dir: Path) -> Path:
    semana_dir = out_dir / plan.semana
    semana_dir.mkdir(parents=True, exist_ok=True)
    (semana_dir / "_plan.json").write_text(plan.model_dump_json(indent=2), encoding="utf-8")

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        for i, post in enumerate(plan.posts, 1):
            d = semana_dir / carpeta_post(i, post)
            d.mkdir(exist_ok=True)
            w, h = SIZES[post.formato]
            page = browser.new_page(viewport={"width": w, "height": h})
            for j, s in enumerate(post.slides, 1):
                html = TPL.render(s=s, idx=j, total_slides=len(post.slides), w=w, h=h, tall=h > 1400,
                                  cta=post.cta, handle=settings.ig_handle)
                page.set_content(html, wait_until="load")
                page.evaluate("document.fonts.ready")
                nombre = "portada.png" if post.formato == Formato.reel else f"slide_{j:02d}.png"
                page.screenshot(path=str(d / nombre))
            page.close()

            (d / "caption.txt").write_text(_caption(post), encoding="utf-8")
            meta = post.model_dump(mode="json", exclude={"slides", "guion", "caption", "hashtags"})
            (d / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
            if post.guion:
                (d / "guion.md").write_text(_guion_md(post), encoding="utf-8")
        browser.close()
    return semana_dir
