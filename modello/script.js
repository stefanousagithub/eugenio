(() => {
"use strict";
const $ = s => document.querySelector(s);
const NBSP = "\u00a0";
const oggi = new Date(); oggi.setHours(0, 0, 0, 0);
const dataISO = s => { const [a, m, g] = s.split("-").map(Number); return new Date(a, m - 1, g); };
const giorni = (a, b) => Math.round((b - a) / 864e5);
const fmt = o => { const f = new Intl.DateTimeFormat("it-IT", o); return d => f.format(d).replace(/\./g, "").replace(/ /g, NBSP); };
const fmtBreve = fmt({ day: "numeric", month: "short" });
const fmtLungo = fmt({ day: "numeric", month: "long" });
const fmtMese = fmt({ month: "short" });
const ridotto = matchMedia("(prefers-reduced-motion: reduce)").matches;
const EASE = "cubic-bezier(.23,1,.32,1)";

/* ---------------- partenze ---------------- */
const futuri = [];
let inCorso = null;
document.querySelectorAll(".imbarco").forEach(li => {
  const d = li.dataset, dal = dataISO(d.dal), al = dataISO(d.al);
  if (al < oggi) { li.remove(); return; } // passata: build.py la sposta tra i viaggi fatti al prossimo aggiornamento
  const mancano = giorni(oggi, dal);
  const conto = li.querySelector("[data-conto]");
  conto.textContent = mancano > 1 ? `tra ${mancano} giorni` : mancano === 1 ? "domani" : "in viaggio";
  li.querySelectorAll("[data-data]").forEach(el => el.textContent = fmtBreve(el.dataset.data === "dal" ? dal : al));
  if (dal <= oggi && d.inViaggio === "si") inCorso = { titolo: d.destinazione, dal, al };
  const posti = +d.posti || 0, iscritti = Math.min(+d.iscritti || 0, posti);
  if (posti) { // mappa dei posti come in cabina: file da 3+3 con il corridoio
    const cab = li.querySelector("[data-cabina]");
    cab.hidden = false;
    for (let i = 0; i < posti; i++) {
      if (i % 6 === 3) cab.append(document.createElement("b"));
      const s = document.createElement("i"); if (i < iscritti) s.className = "preso"; cab.append(s);
    }
    // stesse parole del sito di Avventure: sotto il minimo «Si parte con N iscritti», poi Confermato, Quasi completo, Completo
    const minimo = +d.minimo || 3;
    let stato = `Si parte con ${minimo} iscritti`, cls = "stato-attesa";
    if (iscritti >= posti) { stato = "Completo"; cls = ""; }
    else if (iscritti >= minimo && posti - iscritti <= 3) { stato = "Quasi completo"; cls = ""; }
    else if (iscritti >= minimo) { stato = "Confermato"; cls = "stato-ok"; }
    li.querySelector("[data-stato]").innerHTML = `<strong class="${cls}">${stato}</strong><span>${iscritti} ${iscritti === 1 ? "iscritto" : "iscritti"} su ${posti}${d.codice ? ` · cod.${NBSP}${d.codice}` : ""}</span>`;
  }
  futuri.push({ titolo: d.destinazione, data: dal, guida: d.guida === "si", c: d.c, mancano, slug: d.slug, foto: d.foto || "",
    quando: d.quando || "", descrizione: d.descrizione || "", timbro: d.timbro || "" });
});
const sezPartenze = $("#partenze");
if (sezPartenze && !document.querySelector(".imbarco")) sezPartenze.hidden = true;

/* ---------------- video: il lettore di Instagram si carica solo quando lo si apre, e si scarica alla chiusura ---------------- */
const schermo = $("#schermo"), contVideo = $("#schermo-video");
let tornaA = null;
function apriVideo(url, titolo, colore, da) {
  schermo.style.setProperty("--cv", colore || "#1c1c1e");
  $("#schermo-titolo").textContent = titolo;
  $("#schermo-link").href = url;
  const fr = document.createElement("iframe");
  fr.src = url + "embed/"; fr.title = `Video: ${titolo}`;
  fr.allow = "autoplay; encrypted-media; picture-in-picture; fullscreen"; fr.loading = "eager";
  contVideo.replaceChildren(fr); tornaA = da || null;
  schermo.showModal();
}
$("#schermo-chiudi").addEventListener("click", () => schermo.close());
schermo.addEventListener("click", e => { if (e.target === schermo) schermo.close(); });
schermo.addEventListener("close", () => { contVideo.replaceChildren(); if (tornaA) tornaA.focus(); });
document.querySelectorAll(".scheda-mia[data-video]").forEach(b => b.addEventListener("click", () => apriVideo(b.dataset.video, b.dataset.titolo, b.dataset.c, b)));

/* ---------------- mappa a tutto schermo: il mondo intero, da scorrere col dito, con gli elenchi dei paesi ---------------- */
const mappaSchermo = $("#mappa-schermo");
if (mappaSchermo) {
  const apri = $("#mappa-apri"), grande = $("#mappa-grande");
  apri.addEventListener("click", () => {
    if (!grande.firstChild) {
      const svg = apri.querySelector("svg.mappa").cloneNode(true);
      const [cx, , cw] = svg.getAttribute("viewBox").split(" ").map(Number);
      svg.setAttribute("viewBox", svg.dataset.intero); svg.removeAttribute("aria-label"); svg.setAttribute("aria-hidden", "true");
      grande.append(svg); grande.dataset.centro = (cx + cw / 2) / 1000;
    }
    mappaSchermo.showModal();
    // parte centrata sull'area visitata
    grande.scrollLeft = grande.scrollWidth * +grande.dataset.centro - grande.clientWidth / 2;
  });
  $("#mappa-chiudi").addEventListener("click", () => mappaSchermo.close());
  mappaSchermo.addEventListener("click", e => { if (e.target === mappaSchermo) mappaSchermo.close(); });
  mappaSchermo.addEventListener("close", () => apri.focus());
}

/* ---------------- linea del tempo ---------------- */
const tessere = [...document.querySelectorAll("#griglia > li")];
const fatti = tessere.map(li => ({
  titolo: li.dataset.titolo, anno: +li.dataset.anno, mese: +li.dataset.mese || 1, guida: li.dataset.guida === "si",
  c: li.dataset.c, foto: li.dataset.foto, pos: li.dataset.pos || "50", riga: li.dataset.riga, frase: li.dataset.frase, slug: li.dataset.slug, video: li.dataset.video || "",
  quando: li.dataset.quando || "", timbro: li.dataset.timbro || "", ordine: +li.dataset.ordine || 0
})).sort((a, b) => a.ordine - b.ordine); // la griglia va dal più recente, la linea del tempo dal più vecchio
const prossimo = futuri[0];
const rigaBase = $("#p-riga").dataset.predefinita;
let rigaOggi = rigaBase;
if (inCorso) {
  rigaOggi = `Adesso sono in viaggio: ${inCorso.titolo}, giorno ${giorni(inCorso.dal, oggi) + 1} di ${giorni(inCorso.dal, inCorso.al) + 1}.`;
}
else if (prossimo) {
  // il conto dei giorni si calcola a ogni visita dalla data di oggi
  const tra = prossimo.mancano > 1 ? `tra ${prossimo.mancano}${NBSP}giorni` : "domani";
  rigaOggi = `${rigaBase} Prossima partenza: ${prossimo.titolo}, ${tra}.`;
}
$("#p-riga").textContent = rigaOggi;
const voci = [...fatti,
  { titolo: "Oggi", anno: oggi.getFullYear(), oggi: true, riga: rigaOggi, c: null },
  ...futuri.map(f => ({ titolo: f.titolo, anno: f.data.getFullYear(), futuro: true, data: f.data, guida: f.guida, c: f.c, slug: f.slug,
    foto: f.foto, pos: "50", timbro: f.timbro, quando: `${f.quando} · prossima partenza`,
    riga: f.descrizione || `Prossima tappa: parto il ${fmtLungo(f.data)}${f.guida ? ", da tour leader" : ""}.` }))];
const iOggi = voci.findIndex(v => v.oggi);

if (fatti.length >= 2) {
  const tempo = $("#tempo"), palco = $("#palco"), strati = $("#strati"), titoloPalco = $("#palco-titolo");
  const imgOggi = $("#scatto-a"), imgB = $("#scatto-b"), linea = $("#linea"), testi = $("#p-testi");
  const coloreOggi = getComputedStyle(document.documentElement).getPropertyValue("--oggi").trim();

  // striscia di miniature (come lo scrubber delle app di foto): un fotogramma per viaggio, «oggi» con la foto di Eugenio,
  // le partenze tratteggiate con la data. Si tocca, si trascina col dito, si usa con le frecce della tastiera
  linea.hidden = false; $("#istruzione").hidden = false;
  linea.className = "striscia"; linea.tabIndex = 0;
  // posizioni sulla barra: passo fisso tra un viaggio e l'altro, più spazio per gli anni saltati e prima di «oggi»
  { let x = 0; const pos = [];
    voci.forEach((v, i) => {
      if (i) { x += 1 + Math.max(0, v.anno - voci[i - 1].anno - 1) * .45; if (v.oggi) x += .2; if (v.futuro) x += voci[i - 1].futuro ? .55 : .5; }
      pos.push(x);
    });
    voci.forEach((v, i) => v.x = 4 + pos[i] / (pos[pos.length - 1] || 1) * 92); }
  linea.innerHTML = '<span class="barra"></span>';
  if (futuri.length) { const f = document.createElement("span"); f.className = "barra-futura"; f.style.left = voci[iOggi].x + "%"; linea.append(f); }
  linea.setAttribute("role", "listbox"); linea.setAttribute("aria-label", "I viaggi nel tempo");
  let annoVisto = null;
  const fotogrammi = voci.map((v, i) => {
    const b = document.createElement("span");
    b.className = "fotogramma" + (v.oggi ? " oggi" : "") + (v.futuro ? " partenza" : "") + (v.guida ? " guida" : "");
    b.setAttribute("role", "option"); b.id = `fotogramma-${i}`; b.setAttribute("aria-label", `${v.titolo}, ${v.anno}`);
    b.style.setProperty("--c", v.c || coloreOggi);
    const punto = document.createElement("span"); punto.className = "fotogramma-punto"; b.append(punto);
    let et = "";
    if (v.oggi) et = "oggi"; else if (v.futuro) et = fmtBreve(v.data); else if (v.anno !== annoVisto) { et = String(v.anno); annoVisto = v.anno; }
    const s = document.createElement("span"); s.className = "fotogramma-data"; s.textContent = et; b.append(s);
    b.style.left = v.x + "%";
    linea.append(b); return b;
  });
  // una sola miniatura, a fumetto sopra il viaggio scelto: scorre lungo la barra, così le foto non si accavallano mai
  const fumetto = document.createElement("span"); fumetto.className = "fumetto"; fumetto.setAttribute("aria-hidden", "true");
  const fumettoFoto = document.createElement("span"); fumettoFoto.className = "fumetto-foto";
  const fumettoImg = document.createElement("img"); fumettoImg.alt = ""; fumettoImg.decoding = "async";
  fumettoFoto.append(fumettoImg); fumetto.append(fumettoFoto); linea.append(fumetto);
  voci.forEach(v => { const m = v.oggi ? "oggi" : v.foto; if (m) { const im = new Image(); im.src = `foto/micro/${m}.webp`; } }); // sono piccole: le carico subito
  function muoviFumetto(v) {
    const m = v.oggi ? "oggi" : v.foto;
    fumetto.style.left = v.x + "%";
    fumetto.className = "fumetto" + (v.oggi ? " oggi" : "") + (v.futuro ? " partenza" : "");
    fumettoFoto.style.setProperty("--c", v.c || coloreOggi);
    if (m) { fumettoImg.hidden = false; fumettoImg.src = `foto/micro/${m}.webp`; fumettoFoto.dataset.lettera = ""; }
    else { fumettoImg.hidden = true; fumettoFoto.dataset.lettera = v.titolo.charAt(0); }
  }
  const sistemaEtichette = () => {};

  // testi del pannello: l'area tiene l'altezza del viaggio più lungo, così la pagina sotto non salta
  function scrivi(v) {
    $("#p-viaggio").textContent = v.titolo;
    $("#p-anno").textContent = v.anno;
    $("#p-riga").textContent = v.riga || "";
    $("#p-ruolo").hidden = !v.guida;
    $("#p-video").hidden = !v.video;
    $("#p-partenza").hidden = !v.futuro;
    $("#p-oggi").hidden = !v.oggi;
    $("#istruzione").hidden = false;
    if (v.futuro) $("#p-partenza").href = `#imb-${v.slug}`;
    const q = $("#p-quando"); q.hidden = !v.quando; q.textContent = v.quando || "";
    const fr = $("#p-frase"); fr.hidden = !v.frase; fr.textContent = v.frase ? `«${v.frase}»` : "";
  }
  let corrente = iOggi;
  function misura() { scrivi(voci[corrente]); }
  // il pannello prende l'altezza del testo di ogni viaggio, con una transizione breve invece di un salto
  let animTesti = null;
  function scriviMorbido(v) {
    const h0 = testi.offsetHeight; scrivi(v); const h1 = testi.offsetHeight;
    if (ridotto || h0 === h1) return;
    if (animTesti) animTesti.cancel();
    testi.style.overflow = "hidden";
    animTesti = testi.animate([{ height: h0 + "px" }, { height: h1 + "px" }], { duration: 260, easing: EASE });
    animTesti.onfinish = animTesti.oncancel = () => { testi.style.overflow = ""; };
  }

  const src = v => `foto/${v.foto}.webp`;
  const precarica = i => { const v = voci[i]; if (v && v.foto) { const im = new Image(); im.decoding = "async"; im.src = src(v); } };

  function mostra(i) {
    i = Math.max(0, Math.min(voci.length - 1, i));
    corrente = i; const v = voci[i];
    tempo.style.setProperty("--cv", v.c || coloreOggi);
    fotogrammi.forEach((b, k) => { b.classList.toggle("scelto", k === i); b.setAttribute("aria-selected", k === i ? "true" : "false"); });
    linea.setAttribute("aria-activedescendant", `fotogramma-${i}`);
    muoviFumetto(v);
    scriviMorbido(v);
    if (v.oggi) { imgOggi.classList.add("is-on"); imgB.classList.remove("is-on"); palco.classList.remove("senza-foto"); }
    else if (v.foto) {
      imgB.hidden = false; imgB.style.objectPosition = `${v.pos}% 50%`;
      if (imgB.getAttribute("src") !== src(v)) imgB.src = src(v);
      imgB.alt = v.titolo; imgB.classList.add("is-on"); imgOggi.classList.remove("is-on"); palco.classList.remove("senza-foto");
    } else {
      imgOggi.classList.remove("is-on"); imgB.classList.remove("is-on");
      titoloPalco.textContent = v.titolo; palco.classList.add("senza-foto");
    }
    // timbro di Eugenio sui viaggi da tour leader: si «stampa» sulla foto
    const tb = $("#p-timbro");
    if (v.timbro) {
      const nuovo = `timbri/${v.timbro}.webp`;
      if (tb.hidden || tb.getAttribute("src") !== nuovo) {
        tb.src = nuovo; tb.hidden = false;
        tb.classList.remove("stampa"); void tb.offsetWidth; tb.classList.add("stampa");
      }
    } else tb.hidden = true;
    $("#annuncio").textContent = `${v.titolo}, ${v.anno}`;
    precarica(i - 1); precarica(i + 1);
  }

  // passaggio direzionale: il contenuto esce dal lato del gesto ed entra dall'altro (spazialità coerente)
  let anim = null;
  function vai(i, dir = 0, dx = 0) {
    i = Math.max(0, Math.min(voci.length - 1, i));
    if (anim) { anim.cancel(); anim = null; }
    if (!dir || ridotto || i === corrente) { strati.style.transform = ""; mostra(i); return; }
    const w = palco.offsetWidth;
    const uscita = strati.animate([{ transform: `translate3d(${dx}px,0,0)`, opacity: 1 }, { transform: `translate3d(${-dir * w * .35}px,0,0)`, opacity: 0 }],
      { duration: 140, easing: "linear", fill: "forwards" });
    anim = uscita;
    uscita.onfinish = () => {
      mostra(i);
      anim = strati.animate([{ transform: `translate3d(${dir * w * .25}px,0,0)`, opacity: 0 }, { transform: "translate3d(0,0,0)", opacity: 1 }],
        { duration: 300, easing: EASE });
      anim.onfinish = () => { anim = null; };
      strati.style.transform = "";
      uscita.cancel();
    };
  }

  // trascinare la linea: il cursore segue il dito 1:1
  const indiceDa = clientX => {
    let best = 0, dist = Infinity;
    fotogrammi.forEach((b, i) => { const r = b.getBoundingClientRect(), d = Math.abs(r.left + r.width / 2 - clientX); if (d < dist) { dist = d; best = i; } });
    return best;
  };
  let lineaPuntatore = null;
  linea.addEventListener("pointerdown", e => {
    if (lineaPuntatore !== null) return; // un dito solo
    fermaLapse(); lineaPuntatore = e.pointerId; linea.setPointerCapture(e.pointerId); linea.classList.add("trascina");
    mostra(indiceDa(e.clientX));
  });
  linea.addEventListener("pointermove", e => { if (e.pointerId === lineaPuntatore) { const i = indiceDa(e.clientX); if (i !== corrente) mostra(i); } });
  const fineLinea = e => { if (e.pointerId === lineaPuntatore) { lineaPuntatore = null; linea.classList.remove("trascina"); } };
  linea.addEventListener("pointerup", fineLinea); linea.addEventListener("pointercancel", fineLinea);
  linea.addEventListener("keydown", e => {
    const m = { ArrowRight: 1, ArrowUp: 1, ArrowLeft: -1, ArrowDown: -1 }[e.key];
    if (m) { e.preventDefault(); fermaLapse(); mostra(corrente + m); }
    if (e.key === "Home") { e.preventDefault(); mostra(0); }
    if (e.key === "End") { e.preventDefault(); mostra(voci.length - 1); }
  });

  // scorrere la foto: soglia di 10px, poi 1:1; ai bordi resistenza crescente (rubber band);
  // al rilascio si proietta dove il gesto sarebbe arrivato (decelerazione Apple) e si sceglie il viaggio
  const rubberband = (d, dim, k = .55) => (d * dim * k) / (dim + k * Math.abs(d));
  const proietta = (v, rate = .998) => (v / 1000) * rate / (1 - rate); // v in px/s
  let g = null;
  palco.addEventListener("pointerdown", e => {
    if (g || e.target.closest("a")) return;
    fermaLapse();
    if (anim) { anim.cancel(); anim = null; strati.style.transform = ""; }
    g = { id: e.pointerId, x0: e.clientX, y0: e.clientY, dx: 0, attivo: false, storia: [[performance.now(), e.clientX]] };
  });
  palco.addEventListener("pointermove", e => {
    if (!g || e.pointerId !== g.id) return;
    const dx = e.clientX - g.x0, dy = e.clientY - g.y0;
    if (!g.attivo) {
      if (Math.abs(dx) < 10 || Math.abs(dx) < Math.abs(dy)) return;
      g.attivo = true; palco.setPointerCapture(e.pointerId); palco.classList.add("trascina");
    }
    const bordo = (dx > 0 && corrente === 0) || (dx < 0 && corrente === voci.length - 1);
    g.dx = bordo ? rubberband(dx, palco.offsetWidth) : dx;
    strati.style.transform = `translate3d(${g.dx}px,0,0)`;
    g.storia.push([performance.now(), e.clientX]); if (g.storia.length > 5) g.storia.shift();
  });
  const lascia = e => {
    if (!g || e.pointerId !== g.id) return;
    const { attivo, dx, storia } = g; g = null; palco.classList.remove("trascina");
    if (!attivo) return;
    const [t0, x0] = storia[0], [t1, x1] = storia[storia.length - 1];
    const vel = t1 > t0 ? (x1 - x0) / (t1 - t0) * 1000 : 0; // px/s
    const w = palco.offsetWidth, fine = dx + proietta(vel);
    const dir = fine < -w / 4 ? 1 : fine > w / 4 ? -1 : 0;
    const dest = corrente + dir;
    if (dir && dest >= 0 && dest < voci.length && e.type === "pointerup") vai(dest, dir, dx);
    else { // torna al centro con la stessa curva, partendo da dove si trova
      anim = strati.animate([{ transform: `translate3d(${dx}px,0,0)` }, { transform: "translate3d(0,0,0)" }], { duration: 260, easing: EASE });
      strati.style.transform = ""; anim.onfinish = () => { anim = null; };
    }
  };
  palco.addEventListener("pointerup", lascia); palco.addEventListener("pointercancel", lascia);

  $("#p-video").addEventListener("click", ev => {
    const v = voci[corrente]; if (!v.video) return;
    fermaLapse(); apriVideo(v.video, `${v.titolo}, ${v.anno}`, v.c || coloreOggi, ev.currentTarget);
  });

  // le tessere della griglia aprono quel viaggio sulla linea del tempo, con un link condivisibile (#nome-viaggio)
  const indicePerSlug = s => voci.findIndex(v => v.slug === s);
  tessere.forEach(li => li.querySelector("a").addEventListener("click", ev => {
    const i = indicePerSlug(li.dataset.slug); if (i < 0) return;
    ev.preventDefault(); fermaLapse(); mostra(i);
    history.replaceState(null, "", "#" + li.dataset.slug);
    tempo.scrollIntoView({ behavior: ridotto ? "auto" : "smooth", block: "start" });
  }));

  // time-lapse all'apertura: dal primo viaggio a oggi, una volta sola, interrompibile
  let timer = null;
  function fermaLapse() { if (timer) { clearTimeout(timer); timer = null; } linea.classList.remove("lapse"); }
  addEventListener("keydown", fermaLapse, { once: true });
  misura();
  let rid; addEventListener("resize", () => { cancelAnimationFrame(rid); rid = requestAnimationFrame(misura); });

  const iniziale = location.hash ? indicePerSlug(decodeURIComponent(location.hash.slice(1))) : -1;
  if (iniziale >= 0) mostra(iniziale);
  else if (!ridotto) {
    // veloce, con un'accelerazione all'inizio e una frenata su «oggi»; poi la tappa futura si accende per un attimo
    linea.classList.add("lapse"); let i = 0; mostra(0);
    const durata = k => { const t = k / Math.max(1, iOggi); return 340 + 320 * (1 - Math.sin(Math.PI * t)); };
    const passo = () => {
      i++; mostra(i);
      if (i < iOggi) timer = setTimeout(passo, durata(i));
      else { fermaLapse(); linea.querySelectorAll(".fotogramma.partenza").forEach(t => t.classList.add("invito")); }
    };
    timer = setTimeout(passo, 700);
  } else mostra(iOggi);
}

/* ---------------- cartoline «In autonomia»: un mazzo aperto a ventaglio ----------------
   Si vedono tutte. Col mouse sopra, quella puntata si raddrizza e sale e le vicine si scostano;
   sul telefono il primo tocco la porta davanti, il secondo apre il video. */
document.querySelectorAll(".miei").forEach(ul => {
  const carte = [...ul.children]; const n = carte.length; if (!n) return;
  let scelta = -1, tocco = false, daPuntatore = false;
  const disponi = () => {
    const W = ul.clientWidth;
    const cw = Math.round(Math.min(200, Math.max(118, W * .34)));
    const margine = W < 520 ? 24 : 0, inclina = W < 520 ? 2.2 : 3;
    const passo = n > 1 ? Math.min(cw * .7, (W - cw - 2 * margine) / (n - 1)) : 0;
    const x0 = (W - (cw + passo * (n - 1))) / 2, mezzo = (n - 1) / 2;
    const scosta = Math.min(34, cw * .2);
    let alta = 0;
    carte.forEach(li => { li.style.width = cw + "px"; alta = Math.max(alta, li.offsetHeight); });
    carte.forEach((li, i) => {
      const d = i - mezzo;
      let x = x0 + i * passo, y = d * d * 1.8, r = d * inclina, s = 1;
      if (scelta >= 0 && i !== scelta) x += i < scelta ? -scosta : scosta;
      if (i === scelta) { y = -16; r = 0; s = 1.06; }
      li.style.transform = `translate(${x}px,${y}px) rotate(${r}deg) scale(${s})`;
      li.style.zIndex = i === scelta ? 50 : i + 1;
    });
    ul.style.height = Math.round(alta + 26 + mezzo * mezzo * 1.8) + "px";
  };
  const scegli = i => { if (scelta !== i) { scelta = i; disponi(); } };
  carte.forEach((li, i) => {
    li.addEventListener("pointerenter", e => { if (e.pointerType === "mouse") scegli(i); });
    li.addEventListener("pointerdown", e => { tocco = e.pointerType !== "mouse"; daPuntatore = true; });
    li.addEventListener("focusin", () => { if (!daPuntatore) scegli(i); }); // con la tastiera
    // al tocco: prima la porto davanti, poi si apre
    li.addEventListener("click", e => {
      setTimeout(() => { daPuntatore = false; });
      if (tocco && scelta !== i) { e.stopImmediatePropagation(); e.preventDefault(); scegli(i); }
    }, true);
  });
  ul.addEventListener("pointerleave", e => { if (e.pointerType === "mouse") { scelta = -1; disponi(); } });
  disponi(); addEventListener("resize", disponi);
  ul.querySelectorAll("img").forEach(im => im.addEventListener("load", disponi, { once: true }));
});

/* ---------------- viaggi di gruppo: la foto si assesta (zoom lento) quando la scheda entra nello schermo ---------------- */
if ("IntersectionObserver" in window && !ridotto) {
  const ossTessere = new IntersectionObserver(voci => voci.forEach(v => {
    if (v.isIntersecting) { v.target.classList.add("vista"); ossTessere.unobserve(v.target); }
  }), { threshold: .25 });
  document.querySelectorAll(".griglia .tessera").forEach(t => ossTessere.observe(t));
} else document.querySelectorAll(".griglia .tessera").forEach(t => t.classList.add("vista"));

/* ---------------- carta d'imbarco: tabellone a palette e volo ---------------- */
// le lettere scorrono in ordine come su un tabellone delle partenze, poi si fermano; l'aereo percorre la rotta.
// Parte una volta sola, quando la carta entra nello schermo. Con «riduci movimento» tutto è già al suo posto.
const ALFABETO = " ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
function preparaTabellone(el) {
  const righe = el.dataset.flap.split("/"), larg = Math.max(...righe.map(r => r.length));
  el.textContent = "";
  const celle = [];
  righe.forEach(r => {
    const riga = document.createElement("span"); riga.className = "tab-riga";
    [...r.padEnd(larg)].forEach(ch => {
      const c = document.createElement("span"), t = document.createElement("span");
      c.className = "cella"; t.textContent = ridotto ? ch.trim() : "";
      c.append(t); riga.append(c); celle.push({ c, t, fine: ch });
    });
    el.append(riga);
  });
  return celle;
}
function giraTabellone(celle, ritardo = 0) {
  if (ridotto) return;
  celle.forEach(({ c, t, fine }, k) => {
    const arrivo = Math.max(0, ALFABETO.indexOf(fine.toUpperCase()));
    const giri = fine === " " ? 2 : 5 + (k % 5) + Math.floor(Math.random() * 4);
    let n = 0;
    const tick = () => {
      n++;
      const ch = n >= giri ? fine : ALFABETO[(arrivo - giri + n + ALFABETO.length * 3) % ALFABETO.length];
      t.textContent = ch.trim();
      c.classList.remove("gira"); void c.offsetWidth; c.classList.add("gira");
      if (n < giri) setTimeout(tick, 62);
    };
    setTimeout(tick, ritardo + k * 28);
  });
}
function preparaVolo(svg) {
  const traccia = svg.querySelector(".volo-traccia"), fatto = svg.querySelector(".volo-fatto");
  const arrivo = svg.querySelector(".volo-arrivo"), aereo = svg.querySelector(".volo-aereo");
  const FINE = .86; let p = ridotto ? FINE : 0;
  const disegna = () => {
    const w = svg.clientWidth || 120, h = svg.clientHeight || 44;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    const d = `M 8 ${h - 9} Q ${w / 2} ${-h * .5} ${w - 8} ${h - 9}`;
    traccia.setAttribute("d", d); fatto.setAttribute("d", d);
    arrivo.setAttribute("cx", w - 8); arrivo.setAttribute("cy", h - 9);
    const L = traccia.getTotalLength();
    fatto.style.strokeDasharray = L; fatto.style.strokeDashoffset = L * (1 - p);
    const a = traccia.getPointAtLength(L * p), b = traccia.getPointAtLength(Math.min(L, L * p + 1)), z = traccia.getPointAtLength(Math.max(0, L * p - 1));
    aereo.setAttribute("transform", `translate(${a.x} ${a.y}) rotate(${Math.atan2(b.y - z.y, b.x - z.x) * 180 / Math.PI})`);
  };
  disegna();
  addEventListener("resize", disegna);
  return (ritardo = 0) => {
    if (ridotto) return;
    const t0 = performance.now() + ritardo, dur = 2200;
    const frame = now => {
      const t = Math.min(1, Math.max(0, (now - t0) / dur));
      p = FINE * (t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2); // ease-in-out: decollo e atterraggio dolci
      disegna(); if (t < 1) requestAnimationFrame(frame);
    };
    requestAnimationFrame(frame);
  };
}
document.querySelectorAll(".imbarco").forEach(li => {
  const tabelloni = [...li.querySelectorAll("[data-flap]")].map(preparaTabellone);
  const svg = li.querySelector("[data-volo]"), vola = svg ? preparaVolo(svg) : () => {};
  const parti = () => { tabelloni.forEach((c, i) => giraTabellone(c, i * 260)); vola(500); };
  if (!("IntersectionObserver" in window)) { parti(); return; }
  const oss = new IntersectionObserver(voci => {
    if (voci.some(v => v.isIntersecting)) { oss.disconnect(); parti(); }
  }, { threshold: .45 });
  oss.observe(li);
});

/* ---------------- condividi ---------------- */
const btn = $("#condividi");
btn.addEventListener("click", async () => {
  const url = location.href.split("#")[0];
  try {
    if (navigator.share) await navigator.share({ title: document.title, url });
    else { await navigator.clipboard.writeText(url); btn.setAttribute("aria-label", "Link copiato"); }
  } catch (e) { /* condivisione annullata */ }
});
})();
