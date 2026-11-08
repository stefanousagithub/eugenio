#!/usr/bin/env python3
"""Genera il sito statico in dist/ a partire dai contenuti modificabili dal CMS.

    python build.py              # build completa
    python build.py --offline    # senza leggere iscritti e posti dal sito di Avventure

Contenuti:  contenuti/profilo.json, contenuti/viaggi.json, contenuti/partenze.json
Foto:       foto/caricate/ (originali caricati dal CMS; qui vengono ridimensionati e ripuliti dai metadati)
Modello:    modello/testa.html + modello/stile.css + modello/corpo.html + modello/script.js

Se un contenuto non è valido la build si ferma con un messaggio in italiano che dice cosa correggere:
il sito online resta quello di prima finché l'errore non viene sistemato.
"""
import argparse
import datetime as dt
import html
import json
import pathlib
import re
import shutil
import sys
import unicodedata
import urllib.request

RADICE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(RADICE / "strumenti"))
from prepara_foto import colore_viaggio, pulita, salva  # noqa: E402
from mappa import mappa_svg  # noqa: E402

DIST = RADICE / "dist"
MESI = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto",
        "settembre", "ottobre", "novembre", "dicembre"]
API_AVVENTURE = ("https://www.viaggiavventurenelmondo.it/api/operative/tours"
                 "?fromDate={giorno}&toDate={giorno}&hasAssignment=1&spg={pagina}")
errori, avvisi = [], []
e = html.escape


def leggi(nome):
    try:
        return json.loads((RADICE / "contenuti" / nome).read_text(encoding="utf-8"))
    except json.JSONDecodeError as ex:
        sys.exit(f"ERRORE: contenuti/{nome} non è un JSON valido (riga {ex.lineno}): {ex.msg}")


def slug(testo):
    t = unicodedata.normalize("NFKD", testo).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-") or "viaggio"


def video_instagram(url, dove):
    """Dal link di un reel o post Instagram ricava l'indirizzo del lettore incorporabile; '' se manca o non è valido."""
    if not (url or "").strip():
        return ""
    m = re.search(r"instagram\.com/(?:[A-Za-z0-9_.]+/)?(reel|reels|p|tv)/([A-Za-z0-9_-]+)", url)
    if not m:
        avvisi.append(f"{dove}: il link del video «{url}» non sembra un reel o un post di Instagram, lo ignoro")
        return ""
    tipo = "reel" if m.group(1) in ("reel", "reels", "tv") else "p"
    return f"https://www.instagram.com/{tipo}/{m.group(2)}/"


def righe_tabellone(testo, larghezza=11, max_righe=3):
    """Scritta del tabellone: righe da al massimo 11 caratteri. Con «/» le righe le decide chi scrive,
    altrimenti si va a capo da soli tra una parola e l'altra (così una meta lunga allunga il tabellone)."""
    if "/" in testo:
        righe = [r.strip().upper() for r in testo.split("/") if r.strip()]
    else:
        righe, riga = [], ""
        for parola in testo.upper().split():
            if riga and len(riga) + 1 + len(parola) > larghezza:
                righe.append(riga); riga = parola
            else:
                riga = f"{riga} {parola}".strip()
        if riga:
            righe.append(riga)
    return [r[:larghezza] for r in righe][:max_righe] or [testo.upper()[:larghezza]]


def colore_valido(c):
    return bool(re.fullmatch(r"#[0-9a-fA-F]{6}", c or ""))


def data_valida(s, dove):
    try:
        return dt.date.fromisoformat(s)
    except (TypeError, ValueError):
        errori.append(f"{dove}: la data «{s}» non è valida (formato AAAA-MM-GG)")
        return None


# ---------- foto ----------
def foto(percorso, nome, dove):
    """Da '/foto/caricate/x.jpg' produce dist/foto/<nome>.webp|.jpg e la miniatura; ritorna le info o None."""
    if not percorso:
        return None
    sorgente = RADICE / percorso.lstrip("/")
    if not sorgente.exists():
        errori.append(f"{dove}: la foto {percorso} non esiste nel repository")
        return None
    img = pulita(sorgente)  # orientamento corretto, nessun metadato (GPS compreso)
    colore, _ = colore_viaggio(img)
    (DIST / "foto" / "mini").mkdir(parents=True, exist_ok=True)
    (w, h), _ = salva(img, 1600, DIST / "foto" / nome, 250)
    (mw, mh), _ = salva(img, 480, DIST / "foto" / "mini" / nome, 40)
    return {"nome": nome, "w": w, "h": h, "mw": mw, "mh": mh, "colore": colore}


def picture(info, cls, alt, extra=""):
    return (f'<picture><source srcset="foto/{info["nome"]}.webp" type="image/webp">'
            f'<img class="{cls}" src="foto/{info["nome"]}.jpg" width="{info["w"]}" height="{info["h"]}" alt="{e(alt)}"{extra}></picture>')


# ---------- iscritti dal sito di Avventure (stessa fonte pubblica usata dal sito di riferimento) ----------
def iscritti_avventure(codice, giorno):
    visti = set()
    for pagina in range(1, 6):
        req = urllib.request.Request(API_AVVENTURE.format(giorno=giorno, pagina=pagina),
                                     headers={"User-Agent": "Mozilla/5.0 (sito personale di un coordinatore)"})
        with urllib.request.urlopen(req, timeout=15) as r:
            risultati = json.load(r)["data"]["results"]
        nuovi = [t for t in risultati if t.get("id") not in visti]
        if not nuovi:
            return None
        for t in nuovi:
            if t.get("code") == codice and isinstance(t.get("pax"), int) and isinstance(t.get("paxMax"), int):
                return t["pax"], t["paxMax"]
            visti.add(t.get("id"))
    return None


# ---------- rendering ----------
def sottotitolo_html(testo):
    s = e(testo)
    return s.replace("Avventure nel Mondo",
                     '<a href="https://www.viaggiavventurenelmondo.it/" target="_blank" rel="noopener">Avventure nel Mondo</a>', 1)


ICONA_MSG = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
             'stroke-linejoin="round" aria-hidden="true"><path d="M21 11.5a8.4 8.4 0 0 1-9 8.4 9 9 0 0 1-4-.9L3 20l1.1-4.2'
             'A8 8 0 0 1 3 11.5 8.4 8.4 0 0 1 12 3a8.4 8.4 0 0 1 9 8.5Z"/></svg>')
ICONA_IG = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="3" y="3" '
            'width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor" stroke="none"/></svg>')
ICONA_MAIL = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
              'stroke-linejoin="round" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg>')
ICONA_BUSSOLA = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
                 'stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="m15.5 8.5-2.1 4.9-4.9 2.1 2.1-4.9 4.9-2.1Z"/></svg>')


def riga_contatto(href, colore, icona, titolo, sotto, cta):
    return (f'        <li><a class="contatto" href="{e(href)}" target="_blank" rel="noopener">'
            f'<span class="contatto-icona" style="--i:{colore}">{icona}</span>'
            f'<span class="testi"><b>{e(titolo)}</b><small>{e(sotto)}</small></span>'
            f'<span class="contatto-cta">{e(cta)}</span></a></li>')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true", help="non leggere iscritti e posti dal sito di Avventure")
    a = ap.parse_args()

    profilo, viaggi, partenze = leggi("profilo.json"), leggi("viaggi.json"), leggi("partenze.json")
    oggi = dt.date.today()
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()

    for campo in ("nome", "sottotitolo", "bio_attacco"):
        if not (profilo.get(campo) or "").strip():
            errori.append(f"Profilo: il campo «{campo}» è vuoto")

    # partenze: quelle già concluse diventano viaggi fatti
    future = []
    for i, p in enumerate(partenze, 1):
        dove = f"Partenza {i} ({p.get('destinazione') or p.get('titolo') or 'senza nome'})"
        dal, al = data_valida(p.get("dal"), dove), data_valida(p.get("al"), dove)
        if not dal or not al:
            continue
        if al < dal:
            errori.append(f"{dove}: il ritorno è prima della partenza")
        if not colore_valido(p.get("colore")):
            p["colore"] = "#2c2c2e"
        if al < oggi:
            viaggi.append({"titolo": p.get("titolo") or p.get("destinazione"), "anno": dal.year, "mese": dal.month,
                           "tour_leader": bool(p.get("tour_leader")), "foto": p.get("foto", ""), "inquadratura": 50,
                           "colore": p["colore"], "frase": "", "scheda": p.get("scheda", ""),
                           "riga": f"Con Avventure nel Mondo{', cod. ' + p['codice'] if p.get('codice') else ''}, "
                                   f"dal {dal.day} {MESI[dal.month - 1]} al {al.day} {MESI[al.month - 1]}."})
            continue
        p["_dal"], p["_al"] = dal, al
        if p.get("codice") and not p.get("posti") and not a.offline:
            try:
                r = iscritti_avventure(f"{dal.year}-{p['codice']}", dal.isoformat())
                if r:
                    p["iscritti"], p["posti"] = r
                    print(f"{dove}: {r[0]} iscritti su {r[1]} dal sito di Avventure")
                else:
                    avvisi.append(f"{dove}: partenza cod. {p['codice']} non trovata sul sito di Avventure")
            except Exception as ex:  # rete, formato cambiato, sito giù: il sito si genera lo stesso
                avvisi.append(f"{dove}: sito di Avventure non raggiungibile ({ex})")
        future.append(p)
    future.sort(key=lambda p: p["_dal"])

    # viaggi fatti, dal più vecchio (il CMS può salvare numeri come testo: li normalizzo)
    for i, v in enumerate(viaggi, 1):
        dove = f"Viaggio {i} ({v.get('titolo') or 'senza titolo'})"
        try:
            v["anno"] = int(v.get("anno"))
            v["mese"] = min(12, max(1, int(v.get("mese") or 1)))
        except (TypeError, ValueError):
            pass
        if not (v.get("titolo") or "").strip():
            errori.append(f"{dove}: manca il titolo")
        if not isinstance(v.get("anno"), int) or not 1950 <= v["anno"] <= oggi.year + 1:
            errori.append(f"{dove}: l'anno «{v.get('anno')}» non è valido")
        if v.get("colore") and not colore_valido(v["colore"]):
            errori.append(f"{dove}: il colore «{v['colore']}» non è valido (formato #RRGGBB)")
    if errori:
        sys.exit("La build si è fermata. Da correggere:\n- " + "\n- ".join(errori))
    viaggi.sort(key=lambda v: (v["anno"], v.get("mese") or 1))

    # slug unici (servono ai link condivisibili #nome-viaggio)
    usati = set()
    for v in viaggi:
        s = base = slug(v["titolo"]); n = 2
        while s in usati:
            s = f"{base}-{n}"; n += 1
        usati.add(s); v["_slug"] = s

    # foto
    oggi_foto = foto(profilo.get("foto_oggi"), "oggi", "Profilo")
    tessere = []
    for v in viaggi:
        info = foto(v.get("foto"), v["_slug"], f"Viaggio {v['titolo']}")
        colore = v.get("colore") or (info and info["colore"]) or "#2c2c2e"
        guida = "si" if v.get("tour_leader") else "no"
        video = video_instagram(v.get("video"), f"Viaggio {v['titolo']}")
        attr = (f'data-slug="{v["_slug"]}" data-titolo="{e(v["titolo"])}" data-anno="{v["anno"]}" data-mese="{v.get("mese") or 1}" '
                f'data-guida="{guida}" data-c="{colore}" data-foto="{v["_slug"] if info else ""}" '
                f'data-pos="{int(v.get("inquadratura") or 50)}" data-riga="{e(v.get("riga", ""))}" data-frase="{e(v.get("frase", ""))}" data-video="{e(video)}"')
        immagine = ""
        if info:
            immagine = (f'<picture><source srcset="foto/mini/{info["nome"]}.webp" type="image/webp"><img src="foto/mini/{info["nome"]}.jpg" '
                        f'width="{info["mw"]}" height="{info["mh"]}" alt="" loading="lazy" decoding="async" '
                        f'style="object-position:{int(v.get("inquadratura") or 50)}% 50%"></picture>')
        badge = '<span class="badge">Tour leader</span>' if v.get("tour_leader") else ""
        tessere.append(f'        <li {attr}><a class="tessera" href="#{v["_slug"]}" style="--c:{colore}">{badge}{immagine}'
                       f'<span class="didascalia"><b>{e(v["titolo"])}</b><span class="anno">{v["anno"]}</span></span></a></li>')

    # crediti delle foto non di Eugenio
    crediti = []
    for v in viaggi:
        if (v.get("credito_foto") or "").strip():
            testo = e(v["credito_foto"].strip())
            if (v.get("link_credito") or "").startswith("https://"):
                testo = f'<a href="{e(v["link_credito"])}" target="_blank" rel="noopener">{testo}</a>'
            crediti.append(testo)

    # partenze future: carta d'imbarco con tabellone a palette e rotta
    blocchi = []
    for p in future:
        dal, al = p["_dal"], p["_al"]
        dest = p.get("destinazione") or p.get("titolo")
        posti = p.get("posti") or ""
        iscr = p.get("iscritti") if p.get("iscritti") not in (None, "") else ""
        try:
            minimo = max(1, int(p.get("minimo") or 3))
        except (TypeError, ValueError):
            minimo = 3
        info_foto = foto(p.get("foto"), f"partenza-{slug(dest)}", f"Partenza {dest}")
        righe = righe_tabellone(p.get("tabellone") or dest)
        data_tab = f"{dal.day} {MESI[dal.month - 1][:3].upper()}"
        testa_tag, testa_fine = ("a", "</a>") if p.get("scheda") else ("div", "</div>")
        href = f' href="{e(p["scheda"])}" target="_blank" rel="noopener"' if p.get("scheda") else ""
        sfondo = ""
        if info_foto:
            sfondo = (f'<picture><source srcset="foto/{info_foto["nome"]}.webp" type="image/webp"><img class="imb-sfondo" '
                      f'src="foto/{info_foto["nome"]}.jpg" width="{info_foto["w"]}" height="{info_foto["h"]}" alt="" loading="lazy" decoding="async"></picture>')
        iscriviti = (f'<a class="pill pieno" href="{e(p["iscrizione"])}" target="_blank" rel="noopener" '
                     f'aria-label="Iscriviti a {e(p.get("titolo") or dest)} del {dal.day} {MESI[dal.month - 1]}, sul sito di Avventure">Iscriviti</a>'
                     if p.get("iscrizione") else "")
        contatto = (f'https://wa.me/{numero_wa(profilo.get("whatsapp"))}?text=' + urllib.request.quote(
            f'Ciao Eugenio, vorrei info su {p.get("titolo") or dest} del {dal.day} {MESI[dal.month - 1]}'
            f'{" (cod. " + p["codice"] + ")" if p.get("codice") else ""}')
            if profilo.get("whatsapp") else f'https://ig.me/m/{e(profilo.get("instagram", ""))}')
        durata = (al - dal).days + 1
        freccia = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" '
                   'stroke-linejoin="round" aria-hidden="true"><path d="m9 6 6 6-6 6"/></svg>') if p.get("scheda") else ""
        tappe = f'<span class="imb-tappe">{e(p["tappe"])}</span>' if p.get("tappe") else ""
        guida = "si" if p.get("tour_leader") else "no"
        ruolo_dt = "Tour leader" if p.get("tour_leader") else "Ruolo"
        ruolo_dd = "Eugenio" if p.get("tour_leader") else "Partecipante"
        aereo = ('<g class="volo-aereo"><path d="M-7-1.2H3L8-.4Q9.6 0 8 .4L3 1.2H-7L-9 4.5H-10.5L-9.2 0-10.5-4.5H-9Z"/>'
                 '<path d="M-1.5-1H2.5L-3.5-8.5H-5.5ZM-1.5 1H2.5L-3.5 8.5H-5.5Z"/></g>')
        blocchi.append(f'''        <li class="imbarco{' con-foto' if info_foto else ''}" data-slug="{slug(dest)}" data-destinazione="{e(dest)}" data-dal="{dal}" data-al="{al}"
            data-guida="{guida}" data-posti="{posti}" data-iscritti="{iscr}" data-minimo="{minimo}" data-codice="{e(p.get('codice') or '')}" data-foto="{info_foto["nome"] if info_foto else ""}"
            data-in-viaggio="{"si" if p.get("mostra_in_viaggio") else "no"}" data-c="{p["colore"]}" style="--c:{p["colore"]}">
          <{testa_tag} class="imb-testa"{href}>
            {sfondo}
            <span class="imb-sopra"><span>Avventure nel Mondo</span><span class="imb-conto"><span data-conto>{dal.day} {MESI[dal.month - 1]}</span>{freccia}</span></span>
            <span class="sr">{e(p.get("titolo") or dest)}, partenza il {dal.day} {MESI[dal.month - 1]} {dal.year}</span>
            <span class="tabellone piccolo" data-flap="{e(data_tab)}" aria-hidden="true">{e(data_tab)}</span>
            <span class="tabellone" data-flap="{e("/".join(righe))}" aria-hidden="true">{"<br>".join(e(r) for r in righe)}</span>
            <span class="imb-rotta">
              <span class="imb-citta"><small>Da</small>{e(p.get("da") or "Roma")}</span>
              <svg class="imb-volo" data-volo aria-hidden="true"><path class="volo-traccia"/><path class="volo-fatto"/><circle class="volo-arrivo" r="4.5"/>{aereo}</svg>
              <span class="imb-citta"><small>A</small>{e(dest)}</span>
            </span>
            {tappe}
            <span class="imb-campi" role="list">
              <span role="listitem"><span class="dt">Ritorno</span><span class="dd" data-data="al">{al.day} {MESI[al.month - 1][:3]}</span></span>
              <span role="listitem"><span class="dt">Durata</span><span class="dd">{durata} giorni</span></span>
              <span role="listitem"><span class="dt">{ruolo_dt}</span><span class="dd">{ruolo_dd}</span></span>
            </span>
          {testa_fine}
          <div class="strappo" aria-hidden="true"></div>
          <div class="imb-tallone">
            <div class="imb-posti">
              <span class="cabina" data-cabina aria-hidden="true" hidden></span>
              <p class="imb-stato" data-stato><strong>Si parte con {minimo} iscritti</strong>{"<span>Cod. " + e(p["codice"]) + "</span>" if p.get("codice") else ""}</p>
            </div>
            <div class="imb-azioni">
              {iscriviti}
              <a class="pill" href="{contatto}" target="_blank" rel="noopener">{ICONA_MSG}Scrivimi per info</a>
            </div>
          </div>
        </li>''')
    partenze_html = ""
    if blocchi:
        titolo_sez = "Prossima partenza" if len(blocchi) == 1 else "Prossime partenze"
        partenze_html = (f'    <section class="sezione" id="partenze" aria-labelledby="t-partenze">\n'
                         f'      <h2 id="t-partenze">{titolo_sez}</h2>\n      <ul class="imbarchi">\n'
                         + "\n".join(blocchi) + "\n      </ul>\n    </section>")

    # numeri: si calcolano dai dati, quindi sono sempre veri
    paesi = {(v.get("paese") or "").strip().lower() for v in viaggi}
    n_guida = sum(1 for v in viaggi if v.get("tour_leader"))
    numeri = f"{len(viaggi)} viaggi"
    if "" not in paesi and len(paesi) > 1:
        numeri += f" in {len(paesi)} paesi"
    if n_guida:
        numeri += f", {n_guida} da tour leader"

    # mappa leggera: paesi visitati pieni, prossima meta tratteggiata
    nomi_visti = sorted({(v.get("paese") or "").strip() for v in viaggi if (v.get("paese") or "").strip()})
    nomi_futuri = [p.get("paese") or p.get("destinazione") or "" for p in future]
    mappa_html = ""
    if len(nomi_visti) >= 3:
        svg, sconosciuti = mappa_svg(nomi_visti, nomi_futuri, f"Mappa dei paesi visitati: {', '.join(nomi_visti)}")
        for n in sconosciuti:
            if n in nomi_visti:
                avvisi.append(f"Mappa: non riconosco il paese «{n}», scrivilo in italiano per intero (es. Repubblica Ceca)")
        prossima = next((n for n in nomi_futuri if n and n not in nomi_visti and n not in sconosciuti), "")
        legenda = (f'<span><i class="pallino"></i>{len(nomi_visti)} paesi</span>'
                   + (f'<span><i class="pallino vuoto"></i>Prossima meta: {e(prossima)}</span>' if prossima else ""))
        mappa_html = f'<figure class="mappa-box">{svg}<figcaption class="mappa-legenda">{legenda}</figcaption></figure>'

    # «Dal gruppo» (frasi vere di partecipanti) e domande: le sezioni compaiono solo se ci sono contenuti
    rec = [r for r in profilo.get("recensioni") or [] if (r.get("testo") or "").strip() and (r.get("nome") or "").strip()]
    recensioni_html = ""
    if rec:
        righe_rec = []
        for r in rec:
            viaggio = f", {e(r['viaggio'].strip())}" if (r.get("viaggio") or "").strip() else ""
            righe_rec.append(f'        <li class="voce-gruppo"><blockquote>{e(r["testo"].strip())}</blockquote>'
                             f'<p class="chi"><b>{e(r["nome"].strip())}</b>{viaggio}</p></li>')
        recensioni_html = ('    <section class="sezione" aria-labelledby="t-gruppo">\n      <h2 id="t-gruppo">Dal gruppo</h2>\n'
                           '      <ul class="gruppo">\n' + "\n".join(righe_rec) + '\n      </ul>\n    </section>')
    dom = [d for d in profilo.get("domande") or [] if (d.get("domanda") or "").strip() and (d.get("risposta") or "").strip()]
    domande_html = ""
    if dom:
        righe_dom = [f'        <details class="domanda"><summary>{e(d["domanda"].strip())}</summary><p>{e(d["risposta"].strip())}</p></details>'
                     for d in dom]
        domande_html = ('    <section class="sezione" aria-labelledby="t-domande">\n      <h2 id="t-domande">Com’è viaggiare con me</h2>\n'
                        '      <div class="domande">\n' + "\n".join(righe_dom) + '\n      </div>\n    </section>')

    # contatti e azione principale
    ig = (profilo.get("instagram") or "").lstrip("@")
    wa = numero_wa(profilo.get("whatsapp"))
    msg = urllib.request.quote(profilo.get("messaggio_whatsapp") or "Ciao, ti scrivo dal tuo sito")
    contatti = []
    if wa:
        contatti.append(riga_contatto(f"https://wa.me/{wa}?text={msg}", "#25d366", ICONA_MSG, "WhatsApp", "Per info sui viaggi", "Scrivi"))
    if ig:
        contatti.append(riga_contatto(f"https://www.instagram.com/{ig}/", "#e1306c", ICONA_IG, "Instagram", f"@{ig}, foto e video dei viaggi", "Segui"))
    if profilo.get("email"):
        contatti.append(riga_contatto(f"mailto:{profilo['email']}", "#0a84ff", ICONA_MAIL, "Email", profilo["email"], "Scrivi"))
    contatti.append(riga_contatto("https://www.viaggiavventurenelmondo.it/", "#3a3a3c", ICONA_BUSSOLA, "Avventure nel Mondo", "Il catalogo dei viaggi di gruppo", "Apri"))
    if wa:
        azione = f'<a class="azione" href="https://wa.me/{wa}?text={msg}" target="_blank" rel="noopener">{ICONA_MSG}Scrivimi su WhatsApp</a>'
    else:
        azione = f'<a class="azione" href="https://ig.me/m/{e(ig)}" target="_blank" rel="noopener">{ICONA_MSG}Scrivimi su Instagram</a>'

    # hero
    if oggi_foto:
        hero = picture(oggi_foto, "scatto is-on", profilo.get("descrizione_foto_oggi") or profilo["nome"],
                       f' id="scatto-a" fetchpriority="high" decoding="async" style="object-position:{int(profilo.get("inquadratura_oggi") or 50)}% 50%"'
                       ' onerror="this.classList.remove(\'is-on\');this.closest(\'.palco\').classList.add(\'senza-foto\')"')
    else:
        hero = '<img class="scatto" id="scatto-a" alt="" hidden>'

    sito = (profilo.get("indirizzo_sito") or "").rstrip("/")
    og = f"{sito}/foto/oggi.jpg" if (sito and oggi_foto) else ("foto/oggi.jpg" if oggi_foto else "")
    jsonld = json.dumps({"@context": "https://schema.org", "@type": "Person", "name": profilo["nome"],
                         "jobTitle": "Tour leader", **({"url": sito} if sito else {}),
                         "sameAs": [f"https://www.instagram.com/{ig}/"] if ig else []}, ensure_ascii=False)
    sostituzioni = {
        "TITOLO": e(profilo["nome"]),
        "DESCRIZIONE": e(profilo.get("descrizione_sito") or profilo["sottotitolo"]),
        "ROBOTS": "" if profilo.get("online_su_google") else '<meta name="robots" content="noindex">',
        "OG_IMAGE": e(og), "JSONLD": jsonld.replace("</", "<\\/"),
        "HERO_FOTO": hero, "NOME": e(profilo["nome"]), "SOTTOTITOLO": sottotitolo_html(profilo["sottotitolo"]),
        "ANNO": str(oggi.year), "RIGA_OGGI": e(profilo.get("riga_oggi", "")), "RIGA_OGGI_ATTR": e(profilo.get("riga_oggi", "")),
        "BIO_ATTACCO": e(profilo["bio_attacco"]), "BIO": e(profilo.get("bio", "")),
        "PARTENZE": partenze_html, "GRIGLIA": "\n".join(tessere), "CONTATTI": "\n".join(contatti),
        "MOTTO": f'<p class="piede-motto" translate="no">{e(profilo["motto"])}</p>' if profilo.get("motto") else "",
        "AZIONE": azione,
        "MAPPA": mappa_html,
        "NUMERI": e(numeri), "RECENSIONI": recensioni_html, "DOMANDE": domande_html,
        "CREDITI": f'<p class="piede-crediti">{"<br>".join(crediti)}</p>' if crediti else "",
    }
    m = RADICE / "modello"
    pagina = (m / "testa.html").read_text(encoding="utf-8") + (m / "stile.css").read_text(encoding="utf-8") \
        + (m / "corpo.html").read_text(encoding="utf-8") + (m / "script.js").read_text(encoding="utf-8") + "\n</script>\n</body>\n</html>\n"
    pagina = re.sub(r"\{\{([A-Z_]+)\}\}", lambda x: sostituzioni[x.group(1)], pagina)
    (DIST / "index.html").write_text(pagina, encoding="utf-8")

    (DIST / ".nojekyll").write_text("")
    if (RADICE / "CNAME").exists():
        shutil.copy(RADICE / "CNAME", DIST / "CNAME")
    robots = "User-agent: *\n" + ("Allow: /\n" if profilo.get("online_su_google") else "Disallow: /\n")
    if sito and profilo.get("online_su_google"):
        robots += f"Sitemap: {sito}/sitemap.xml\n"
        (DIST / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                                          f'<url><loc>{sito}/</loc><lastmod>{oggi}</lastmod></url></urlset>\n')
    (DIST / "robots.txt").write_text(robots)

    for x in avvisi:
        print(f"::warning::{x}")
    print(f"Sito generato in dist/: {len(viaggi)} viaggi, {len(future)} partenze future.")


def numero_wa(n):
    cifre = re.sub(r"\D", "", n or "")
    if not cifre:
        return ""
    return cifre if cifre.startswith("39") and len(cifre) > 10 else "39" + cifre


if __name__ == "__main__":
    main()
