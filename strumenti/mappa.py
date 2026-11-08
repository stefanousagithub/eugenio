"""Mappa leggera dei paesi visitati: un SVG statico generato in build, niente librerie né tile.

Dati: strumenti/mondo-110m.json (world-atlas 2.0.2, licenza ISC, confini Natural Earth 1:110m, pubblico dominio).
Proiezione Equal Earth: le aree restano proporzionate e il mondo ha una forma morbida, senza i poli enormi.
I paesi si scrivono in italiano nel CMS (campo «Paese»); NOMI li traduce nei nomi del file.
"""
import json
import math
import pathlib

DATI = pathlib.Path(__file__).resolve().parent / "mondo-110m.json"

NOMI = {
    "afghanistan": "Afghanistan", "albania": "Albania", "algeria": "Algeria", "argentina": "Argentina", "armenia": "Armenia",
    "australia": "Australia", "austria": "Austria", "azerbaigian": "Azerbaijan", "bahamas": "Bahamas", "bangladesh": "Bangladesh",
    "belgio": "Belgium", "belize": "Belize", "bhutan": "Bhutan", "bielorussia": "Belarus", "bolivia": "Bolivia",
    "bosnia": "Bosnia and Herz.", "bosnia erzegovina": "Bosnia and Herz.", "bosnia ed erzegovina": "Bosnia and Herz.", "botswana": "Botswana", "brasile": "Brazil",
    "bulgaria": "Bulgaria", "cambogia": "Cambodia", "camerun": "Cameroon", "canada": "Canada", "cile": "Chile", "cina": "China",
    "cipro": "Cyprus", "colombia": "Colombia", "corea del sud": "South Korea", "costa rica": "Costa Rica", "croazia": "Croatia",
    "cuba": "Cuba", "danimarca": "Denmark", "ecuador": "Ecuador", "egitto": "Egypt", "el salvador": "El Salvador",
    "emirati arabi uniti": "United Arab Emirates", "emirati arabi": "United Arab Emirates", "estonia": "Estonia", "etiopia": "Ethiopia",
    "filippine": "Philippines", "finlandia": "Finland", "francia": "France", "georgia": "Georgia", "germania": "Germany",
    "ghana": "Ghana", "giamaica": "Jamaica", "jamaica": "Jamaica", "giappone": "Japan", "giordania": "Jordan", "grecia": "Greece",
    "groenlandia": "Greenland", "guatemala": "Guatemala", "honduras": "Honduras", "india": "India", "indonesia": "Indonesia",
    "iran": "Iran", "irlanda": "Ireland", "islanda": "Iceland", "israele": "Israel", "italia": "Italy", "kazakistan": "Kazakhstan",
    "kenya": "Kenya", "kirghizistan": "Kyrgyzstan", "laos": "Laos", "lettonia": "Latvia", "libano": "Lebanon", "lituania": "Lithuania",
    "lussemburgo": "Luxembourg", "macedonia": "Macedonia", "macedonia del nord": "Macedonia", "madagascar": "Madagascar",
    "malesia": "Malaysia", "marocco": "Morocco", "messico": "Mexico", "moldavia": "Moldova", "mongolia": "Mongolia",
    "montenegro": "Montenegro", "mozambico": "Mozambique", "myanmar": "Myanmar", "birmania": "Myanmar", "namibia": "Namibia",
    "nepal": "Nepal", "nicaragua": "Nicaragua", "norvegia": "Norway", "nuova zelanda": "New Zealand", "oman": "Oman",
    "paesi bassi": "Netherlands", "olanda": "Netherlands", "pakistan": "Pakistan", "panama": "Panama", "paraguay": "Paraguay",
    "perù": "Peru", "peru": "Peru", "polonia": "Poland", "portogallo": "Portugal", "regno unito": "United Kingdom",
    "inghilterra": "United Kingdom", "scozia": "United Kingdom", "repubblica ceca": "Czechia", "cechia": "Czechia",
    "repubblica dominicana": "Dominican Rep.", "romania": "Romania", "russia": "Russia", "senegal": "Senegal", "serbia": "Serbia",
    "slovacchia": "Slovakia", "slovenia": "Slovenia", "spagna": "Spain", "sri lanka": "Sri Lanka", "stati uniti": "United States of America",
    "usa": "United States of America", "sudafrica": "South Africa", "svezia": "Sweden", "svizzera": "Switzerland",
    "tagikistan": "Tajikistan", "taiwan": "Taiwan", "tanzania": "Tanzania", "thailandia": "Thailand", "tunisia": "Tunisia",
    "turchia": "Turkey", "turkmenistan": "Turkmenistan", "ucraina": "Ukraine", "uganda": "Uganda", "ungheria": "Hungary",
    "uruguay": "Uruguay", "uzbekistan": "Uzbekistan", "venezuela": "Venezuela", "vietnam": "Vietnam", "zambia": "Zambia",
    "zimbabwe": "Zimbabwe", "arabia saudita": "Saudi Arabia", "qatar": "Qatar", "kosovo": "Kosovo",
}

LARGHEZZA = 1000
A1, A2, A3, A4, M = 1.340264, -0.081106, 0.000893, 0.003796, math.sqrt(3) / 2


def equal_earth(lon, lat):
    l, p = math.radians(lon), math.radians(lat)
    t = math.asin(M * math.sin(p))
    t2, t6 = t * t, t ** 6
    x = l * math.cos(t) / (M * (A1 + 3 * A2 * t2 + t6 * (7 * A3 + 9 * A4 * t2)))
    y = t * (A1 + A2 * t2 + t6 * (A3 + A4 * t2))
    return x, y


X_MAX = equal_earth(180, 0)[0]
SCALA = LARGHEZZA / (2 * X_MAX)
LAT_ALTO, LAT_BASSO = 84, -57  # niente Antartide, poco Artico: la mappa resta bassa
Y_ALTO = equal_earth(0, LAT_ALTO)[1]
ALTEZZA = round((Y_ALTO - equal_earth(0, LAT_BASSO)[1]) * SCALA)


def _punto(lon, lat):
    x, y = equal_earth(lon, lat)
    return (x + X_MAX) * SCALA, (Y_ALTO - y) * SCALA


def _archi(topo):
    sx, sy = topo["transform"]["scale"]
    tx, ty = topo["transform"]["translate"]
    archi = []
    for arco in topo["arcs"]:
        x = y = 0
        punti = []
        for dx, dy in arco:
            x += dx; y += dy
            punti.append((x * sx + tx, y * sy + ty))
        archi.append(punti)
    return archi


def _anello(indici, archi):
    punti = []
    for i in indici:
        tratto = archi[i] if i >= 0 else archi[~i][::-1]
        punti.extend(tratto if not punti else tratto[1:])
    return punti


def _percorso(geom, archi):
    """Ritorna (d, riquadro del pezzo più grande): il riquadro serve per il ritaglio e per i pallini dei paesi piccoli."""
    poligoni = geom["arcs"] if geom["type"] == "MultiPolygon" else [geom["arcs"]]
    pezzi, principale, area_max = [], None, -1
    for poligono in poligoni:
        for n_anello, anello in enumerate(poligono):
            # longitudini rese continue: i contorni che passano il meridiano 180 (Russia, Fiji) non tagliano la mappa
            continui, spost, prec_lon = [], 0, None
            for lon, lat in _anello(anello, archi):
                if prec_lon is not None and abs(lon + spost - prec_lon) > 180:
                    spost += 360 if prec_lon > lon + spost else -360
                prec_lon = lon + spost
                continui.append((prec_lon, lat))
            pts = [_punto(lon, max(LAT_BASSO, min(LAT_ALTO, lat))) for lon, lat in continui]
            if n_anello == 0:  # il contorno esterno: misuro il pezzo più grande del paese
                xs0, ys0 = [p[0] for p in pts], [p[1] for p in pts]
                riq = (min(xs0), min(ys0), max(xs0), max(ys0))
                area = (riq[2] - riq[0]) * (riq[3] - riq[1])
                if area > area_max:
                    area_max, principale = area, riq
            out, prec = [], None
            for x, y in pts:
                q = (round(x), round(y))  # al pixel: basta anche per la mappa espansa
                if q != prec:
                    out.append(q); prec = q
            xs, ys = [q[0] for q in out], [q[1] for q in out]
            if len(out) < 3 or (max(xs) - min(xs) < 3 and max(ys) - min(ys) < 3):
                continue  # isole più piccole di un paio di pixel: non si vedrebbero
            # coordinate relative (l): stringa più corta
            d = f"M{out[0][0]} {out[0][1]}l" + " ".join(f"{x1 - x0} {y1 - y0}" for (x0, y0), (x1, y1) in zip(out, out[1:]))
            pezzi.append(d + "z")
    return "".join(pezzi), principale


def traduci(nome):
    """Nome italiano (come lo scrive Eugenio) → nome nel file della mappa, o None."""
    return NOMI.get((nome or "").strip().lower())


def mappa_svg(categorie, titolo="Mappa dei paesi visitati"):
    """categorie: {nome italiano: classe} con classe tra "gruppo", "mio", "prossimo" (in quest'ordine di priorità).
    Ritorna (svg, sconosciuti). L'SVG ha il viewBox ritagliato sull'area visitata e in data-intero quello del mondo intero."""
    topo = json.loads(DATI.read_text(encoding="utf-8"))
    archi = _archi(topo)
    sconosciuti, classi = [], {}
    priorita = {"gruppo": 0, "mio": 1, "prossimo": 2}
    for nome, cls in categorie.items():
        en = traduci(nome)
        if not en:
            sconosciuti.append(nome)
        elif en not in classi or priorita[cls] < priorita[classi[en]]:
            classi[en] = cls
    terra, colorati, pallini, riquadri = [], [], [], []
    for g in topo["objects"]["countries"]["geometries"]:
        nome = g["properties"]["name"]
        if nome == "Antarctica" or "arcs" not in g:
            continue
        d, riq = _percorso(g, archi)
        cls = classi.get(nome)
        if not cls:
            terra.append(d)
            continue
        colorati.append(f'<path class="{cls}" d="{d}"><title>{nome}</title></path>')
        if riq:
            riquadri.append(riq)
            if riq[2] - riq[0] < 9 and riq[3] - riq[1] < 9:  # paese piccolo (Giamaica, Cipro, Montenegro): un pallino lo rende visibile
                cx, cy = (riq[0] + riq[2]) / 2, (riq[1] + riq[3]) / 2
                pallini.append(f'<circle class="{cls} pallino-mappa" cx="{cx:.0f}" cy="{cy:.0f}" r="4.5"/>')
    # ritaglio: l'area dei paesi colorati con un margine, non più stretta di 2:1
    if riquadri:
        x0, y0 = min(r[0] for r in riquadri), min(r[1] for r in riquadri)
        x1, y1 = max(r[2] for r in riquadri), max(r[3] for r in riquadri)
        m = max(x1 - x0, y1 - y0) * .08 + 10
        x0, y0, x1, y1 = max(0, x0 - m), max(0, y0 - m), min(LARGHEZZA, x1 + m), min(ALTEZZA, y1 + m)
        w, h = x1 - x0, y1 - y0
        if w < 2 * h:
            cx = (x0 + x1) / 2; w = min(LARGHEZZA, 2 * h); x0 = max(0, min(LARGHEZZA - w, cx - w / 2))
        else:
            cy = (y0 + y1) / 2; h = min(ALTEZZA, w / 2); y0 = max(0, min(ALTEZZA - h, cy - h / 2))
        vb = f"{x0:.0f} {y0:.0f} {w:.0f} {h:.0f}"
    else:
        vb = f"0 0 {LARGHEZZA} {ALTEZZA}"
    svg = (f'<svg class="mappa" viewBox="{vb}" data-intero="0 0 {LARGHEZZA} {ALTEZZA}" role="img" aria-label="{titolo}" overflow="hidden">'
           f'<path class="terra" d="{"".join(terra)}"/>{"".join(colorati)}{"".join(pallini)}</svg>')
    return svg, sconosciuti
