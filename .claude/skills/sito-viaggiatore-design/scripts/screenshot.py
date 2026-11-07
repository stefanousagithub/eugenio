#!/usr/bin/env python3
"""Screenshot di una pagina a più larghezze e in tema scuro/chiaro, per il QA visivo.

Uso:
    python screenshot.py index.html --out shots/
    python screenshot.py http://localhost:8000 --out shots/ --full --reduced-motion

Richiede Playwright (pip install playwright && playwright install chromium).
Il time-lapse dell'hero viene lasciato finire (--attesa, default 4s) prima dello scatto.
"""
import argparse
import pathlib
import sys

from playwright.sync_api import sync_playwright

VISTE = {
    "telefono": {"width": 390, "height": 844, "mobile": True, "scale": 3},
    "tablet": {"width": 820, "height": 1180, "mobile": True, "scale": 2},
    "desktop": {"width": 1440, "height": 900, "mobile": False, "scale": 1},
}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("pagina", help="file HTML locale o URL")
    p.add_argument("--out", default="shots")
    p.add_argument("--viste", default="telefono,tablet,desktop")
    p.add_argument("--temi", default="dark,light")
    p.add_argument("--full", action="store_true", help="pagina intera invece del solo primo schermo")
    p.add_argument("--reduced-motion", action="store_true")
    p.add_argument("--attesa", type=float, default=4.0, help="secondi di attesa prima dello scatto")
    a = p.parse_args()

    url = a.pagina
    if not url.startswith(("http://", "https://", "file://")):
        percorso = pathlib.Path(url).resolve()
        if not percorso.exists():
            sys.exit(f"File non trovato: {percorso}")
        url = percorso.as_uri()

    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        for nome in a.viste.split(","):
            v = VISTE[nome]
            for tema in a.temi.split(","):
                ctx = browser.new_context(
                    viewport={"width": v["width"], "height": v["height"]},
                    device_scale_factor=v["scale"],
                    is_mobile=v["mobile"],
                    has_touch=v["mobile"],
                    color_scheme=tema,
                    reduced_motion="reduce" if a.reduced_motion else "no-preference",
                )
                pagina = ctx.new_page()
                errori = []
                pagina.on("pageerror", lambda e: errori.append(str(e)))
                pagina.goto(url, wait_until="networkidle")
                pagina.wait_for_timeout(int(a.attesa * 1000))
                largo = pagina.evaluate("document.documentElement.scrollWidth > window.innerWidth")
                file = out / f"{nome}-{tema}{'-full' if a.full else ''}.png"
                pagina.screenshot(path=str(file), full_page=a.full)
                stato = "OK"
                if largo:
                    stato = "ATTENZIONE: scroll orizzontale"
                if errori:
                    stato += f" | errori JS: {errori[:3]}"
                print(f"{file}  {stato}")
                ctx.close()
        browser.close()


if __name__ == "__main__":
    main()
