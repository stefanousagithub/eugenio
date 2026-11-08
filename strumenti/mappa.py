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
    "bosnia": "Bosnia and Herz.", "bosnia ed erzegovina": "Bosnia and Herz.", "botswana": "Botswana", "brasile": "Brazil",
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
    poligoni = geom["arcs"] if geom["type"] == "MultiPolygon" else [geom["arcs"]]
    pezzi = []
    for poligono in poligoni:
        for anello in poligono:
            # longitudini rese continue: i contorni che passano il meridiano 180 (Russia, Fiji) non tagliano la mappa
            continui, spost, prec_lon = [], 0, None
            for lon, lat in _anello(anello, archi):
                if prec_lon is not None and abs(lon + spost - prec_lon) > 180:
                    spost += 360 if prec_lon > lon + spost else -360
                prec_lon = lon + spost
                continui.append((prec_lon, lat))
            pts = [_punto(lon, max(LAT_BASSO, min(LAT_ALTO, lat))) for lon, lat in continui]
            out, prec = [], None
            for x, y in pts:
                q = (round(x), round(y))  # al pixel: la mappa si vede larga al massimo ~560px
                if q != prec:
                    out.append(q); prec = q
            xs, ys = [q[0] for q in out], [q[1] for q in out]
            if len(out) < 3 or (max(xs) - min(xs) < 3 and max(ys) - min(ys) < 3):
                continue  # isole più piccole di un paio di pixel: non si vedrebbero
            # coordinate relative (l): stringa più corta
            d = f"M{out[0][0]} {out[0][1]}l" + " ".join(f"{x1 - x0} {y1 - y0}" for (x0, y0), (x1, y1) in zip(out, out[1:]))
            pezzi.append(d + "z")
    return "".join(pezzi)


def mappa_svg(visitati, prossimi=(), titolo="Paesi visitati"):
    """Ritorna (svg, sconosciuti): l'SVG della mappa e i nomi di paese che non so tradurre."""
    topo = json.loads(DATI.read_text(encoding="utf-8"))
    archi = _archi(topo)
    sconosciuti = []

    def inglese(nomi):
        out = set()
        for n in nomi:
            chiave = (n or "").strip().lower()
            if not chiave:
                continue
            if chiave in NOMI:
                out.add(NOMI[chiave])
            else:
                sconosciuti.append(n)
        return out

    visti, futuri = inglese(visitati), inglese(prossimi) - inglese(visitati)
    terra, colorati = [], []
    for g in topo["objects"]["countries"]["geometries"]:
        nome = g["properties"]["name"]
        if nome == "Antarctica" or "arcs" not in g:
            continue
        d = _percorso(g, archi)
        if nome in visti:
            colorati.append(f'<path class="visto" d="{d}"/>')
        elif nome in futuri:
            colorati.append(f'<path class="prossimo" d="{d}"/>')
        else:
            terra.append(d)
    svg = (f'<svg class="mappa" viewBox="0 0 {LARGHEZZA} {ALTEZZA}" role="img" aria-label="{titolo}" overflow="hidden">'
           f'<path class="terra" d="{"".join(terra)}"/>{"".join(colorati)}</svg>')
    return svg, sconosciuti
