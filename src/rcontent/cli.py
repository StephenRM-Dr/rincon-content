import argparse
from datetime import date, timedelta
from importlib.resources import files
from pathlib import Path

from rcontent.models import PlanSemanal
from rcontent.render import render_plan
from rcontent.settings import settings


def semana_label(d: date) -> str:
    lunes = d - timedelta(days=d.weekday())
    y, w, _ = lunes.isocalendar()
    return f"{y}-S{w:02d}_{lunes:%d-%m}"


def main():
    ap = argparse.ArgumentParser(prog="rcontent", description="Produce el contenido semanal de @rincondigitalnet")
    ap.add_argument("--dry-run", action="store_true", help="No sube a Drive")
    ap.add_argument("--plan", type=Path, help="Usa un plan JSON existente (salta Gemini)")
    ap.add_argument("--semana", help="Etiqueta de semana (default: semana actual)")
    ap.add_argument("--out", type=Path, default=Path("out"))
    ap.add_argument("--brief", type=Path, help="Archivo de brief local (lo usa el workflow con rclone)")
    a = ap.parse_args()

    semana = a.semana or semana_label(date.today())
    drive = None
    root = None
    if not a.dry_run:
        if not settings.drive_ok:
            raise SystemExit("Faltan credenciales GDRIVE_* (o usa --dry-run)")
        from rcontent.drive import Drive

        drive = Drive()
        root = drive.folder(settings.gdrive_root_name)

    # 1. Brief: Drive manda; si no existe, se siembra con el default
    brief = files("rcontent").joinpath("brief_default.md").read_text(encoding="utf-8")
    if a.brief and a.brief.exists():
        brief = a.brief.read_text(encoding="utf-8")
    if drive:
        remoto = drive.read_text("brief.md", root)
        if remoto:
            brief = remoto
        else:
            drive.write_text("brief.md", root, brief)
    print(f"▸ Semana {semana}")

    # 2-3. Investigación + plan
    tendencias = ""
    if a.plan:
        plan = PlanSemanal.model_validate_json(a.plan.read_text(encoding="utf-8"))
        plan.semana = semana
    else:
        from rcontent.planner import planificar
        from rcontent.research import investigar

        print("▸ Investigando tendencias (Gemini + Google Search)…")
        tendencias, fuentes = investigar(brief)
        print(f"  {len(fuentes)} fuentes")
        print("▸ Planificando semana…")
        plan = planificar(brief, tendencias, semana)

    # 4. Render
    print(f"▸ Renderizando {len(plan.posts)} posts…")
    semana_dir = render_plan(plan, a.out)
    if tendencias:
        (semana_dir / "_tendencias.md").write_text(tendencias, encoding="utf-8")

    # 5. Drive
    if drive:
        print("▸ Subiendo a Drive…")
        fid = drive.upload_tree(semana_dir, root)
        print(f"✓ https://drive.google.com/drive/folders/{fid}")
    else:
        print(f"✓ Local: {semana_dir.resolve()}")


if __name__ == "__main__":
    main()
