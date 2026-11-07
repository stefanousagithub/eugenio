#!/usr/bin/env python3
"""Prepara le foto del sito: due tagli (grande e miniatura) in WebP e JPEG, senza metadati,
e calcola il colore di ogni viaggio.

Uso:
    python prepara_foto.py originali/ --out foto/ --json foto/colori.json
    python prepara_foto.py originali/islanda.HEIC.jpg --out foto/

Output per ogni immagine "Islanda 2019.JPG":
    foto/islanda-2019.webp, foto/islanda-2019.jpg          (lato lungo 1600px)
    foto/mini/islanda-2019.webp, foto/mini/islanda-2019.jpg (lato lungo 480px)
e una voce nel JSON: {"islanda-2019": {"colore": "#2f4a5e", "w": 1600, "h": 1200, ...}}

Il colore segue il criterio del sito di riferimento: tinte divise in 18 spicchi da 20 gradi,
vince lo spicchio (con i due vicini) più acceso, purché copra almeno il 6% dei pixel colorati
dell'immagine; la luminosità viene scelta per avere circa 9:1 di contrasto col testo bianco.

Richiede Pillow (pip install pillow).
"""
import argparse
import colorsys
import json
import math
import pathlib
import re
import sys
import unicodedata

from PIL import Image, ImageOps

GRANDE = 1600
MINI = 480
LIMITE_KB = {"grande": 250, "mini": 40}
ESTENSIONI = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"}


def slug(nome):
    nome = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode()
    nome = re.sub(r"[^a-zA-Z0-9]+", "-", nome).strip("-").lower()
    return nome or "foto"


def luminanza(rgb):
    def canale(c):
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (canale(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrasto_col_bianco(rgb):
    return 1.05 / (luminanza(rgb) + 0.05)


def colore_da_tinta(h, saturazione=0.6, obiettivo=9.0):
    # cerca la luminosità HSL più alta che dà ancora il contrasto voluto col bianco
    basso, alto = 0.0, 0.6
    for _ in range(30):
        l = (basso + alto) / 2
        rgb = tuple(round(c * 255) for c in colorsys.hls_to_rgb(h / 360, l, saturazione))
        if contrasto_col_bianco(rgb) >= obiettivo:
            basso = l
        else:
            alto = l
    rgb = tuple(round(c * 255) for c in colorsys.hls_to_rgb(h / 360, basso, saturazione))
    return "#%02x%02x%02x" % rgb


def colore_viaggio(img):
    piccola = img.convert("RGB").resize((64, 64))
    conta = [0] * 18
    croma = [0.0] * 18
    seno = [0.0] * 18
    coseno = [0.0] * 18
    totale = 0
    pixel = piccola.get_flattened_data() if hasattr(piccola, "get_flattened_data") else piccola.getdata()
    for r, g, b in pixel:
        h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        totale += 1
        c = s * v  # croma approssimata
        if c < 0.12 or v < 0.15:
            continue
        i = int(h * 18) % 18
        conta[i] += 1
        croma[i] += c
        seno[i] += math.sin(h * 2 * math.pi) * c
        coseno[i] += math.cos(h * 2 * math.pi) * c
    migliore, punteggio_max = None, 0.0
    for i in range(18):
        vicini = [(i - 1) % 18, i, (i + 1) % 18]
        copertura = sum(conta[j] for j in vicini) / totale
        punteggio = sum(croma[j] for j in vicini)
        if copertura >= 0.06 and punteggio > punteggio_max:
            migliore, punteggio_max = vicini, punteggio
    if migliore is None:
        return "#2c2c2e", None
    tinta = math.degrees(math.atan2(sum(seno[j] for j in migliore), sum(coseno[j] for j in migliore))) % 360
    return colore_da_tinta(tinta), round(tinta)


def pulita(percorso):
    img = Image.open(percorso)
    img = ImageOps.exif_transpose(img)  # applica la rotazione prima di buttare l'EXIF
    if img.mode not in ("RGB", "L"):
        sfondo = Image.new("RGB", img.size, (0, 0, 0))
        if img.mode in ("RGBA", "LA", "P"):
            img = img.convert("RGBA")
            sfondo.paste(img, mask=img.split()[-1])
            img = sfondo
        else:
            img = img.convert("RGB")
    # copia dei soli pixel: niente EXIF, GPS, XMP o profili residui
    img = img.convert("RGB")
    return Image.frombytes("RGB", img.size, img.tobytes())


def salva(img, lato, destinazione, limite_kb):
    copia = img.copy()
    copia.thumbnail((lato, lato), Image.LANCZOS)
    pesi = {}
    for formato, est, qualita in (("WEBP", ".webp", 80), ("JPEG", ".jpg", 82)):
        file = destinazione.with_suffix(est)
        q = qualita
        while True:
            opzioni = {"quality": q}
            if formato == "JPEG":
                opzioni.update(progressive=True, optimize=True)
            else:
                opzioni.update(method=6)
            copia.save(file, formato, **opzioni)
            kb = file.stat().st_size / 1024
            if kb <= limite_kb or q <= 55:
                break
            q -= 5
        pesi[est] = round(kb)
    return copia.size, pesi


def main():
    p = argparse.ArgumentParser()
    p.add_argument("ingresso", help="cartella o singola immagine")
    p.add_argument("--out", default="foto")
    p.add_argument("--json", help="file JSON con colori e dimensioni")
    a = p.parse_args()

    ingresso = pathlib.Path(a.ingresso)
    files = [ingresso] if ingresso.is_file() else sorted(
        f for f in ingresso.iterdir() if f.suffix.lower() in ESTENSIONI)
    if not files:
        sys.exit("Nessuna immagine trovata.")

    out = pathlib.Path(a.out)
    (out / "mini").mkdir(parents=True, exist_ok=True)
    risultati = {}
    if a.json and pathlib.Path(a.json).exists():
        risultati = json.loads(pathlib.Path(a.json).read_text())

    for f in files:
        nome = slug(f.stem)
        img = pulita(f)
        colore, tinta = colore_viaggio(img)
        (w, h), pesi_g = salva(img, GRANDE, out / nome, LIMITE_KB["grande"])
        (mw, mh), pesi_m = salva(img, MINI, out / "mini" / nome, LIMITE_KB["mini"])
        risultati[nome] = {"colore": colore, "tinta": tinta, "w": w, "h": h, "mini_w": mw, "mini_h": mh,
                           "kb": pesi_g, "mini_kb": pesi_m, "originale": f.name}
        avvisi = []
        if max(pesi_g.values()) > LIMITE_KB["grande"]:
            avvisi.append(f"grande {max(pesi_g.values())} KB")
        if max(pesi_m.values()) > LIMITE_KB["mini"]:
            avvisi.append(f"mini {max(pesi_m.values())} KB")
        nota = f"  ATTENZIONE peso: {', '.join(avvisi)}" if avvisi else ""
        print(f"{f.name} -> {nome}  {w}x{h}  colore {colore}{nota}")

    if a.json:
        pathlib.Path(a.json).write_text(json.dumps(risultati, indent=2, ensure_ascii=False))
        print(f"Scritto {a.json}")


if __name__ == "__main__":
    main()
