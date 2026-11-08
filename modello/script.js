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
  futuri.push({ titolo: d.destinazione, data: dal, guida: d.guida === "si", c: d.c, mancano, slug: d.slug, foto: d.foto || "" });
});
const sezPartenze = $("#partenze");
if (sezPartenze && !document.querySelector(".imbarco")) sezPartenze.hidden = true;

/* ---------------- linea del tempo ---------------- */
const tessere = [...document.querySelectorAll("#griglia > li")];
const fatti = tessere.map(li => ({
  titolo: li.dataset.titolo, anno: +li.dataset.anno, mese: +li.dataset.mese || 1, guida: li.dataset.guida === "si",
  c: li.dataset.c, foto: li.dataset.foto, pos: li.dataset.pos || "50", riga: li.dataset.riga, frase: li.dataset.frase, slug: li.dataset.slug, video: li.dataset.video || ""
}));
const prossimo = futuri[0];
const rigaBase = $("#p-riga").dataset.predefinita;
let rigaOggi = rigaBase;
if (inCorso) {
  rigaOggi = `Adesso sono in viaggio: ${inCorso.titolo}, giorno ${giorni(inCorso.dal, oggi) + 1} di ${giorni(inCorso.dal, inCorso.al) + 1}.`;
} else if (prossimo) {
  rigaOggi = `${rigaBase} Prossima partenza ${prossimo.mancano === 1 ? "domani" : "tra " + prossimo.mancano + NBSP + "giorni"}: ${prossimo.titolo}.`;
}
$("#p-riga").textContent = rigaOggi;
const voci = [...fatti,
  { titolo: "Oggi", anno: oggi.getFullYear(), oggi: true, riga: rigaOggi, c: null },
  ...futuri.map(f => ({ titolo: f.titolo, anno: f.data.getFullYear(), futuro: true, data: f.data, guida: f.guida, c: f.c, slug: f.slug,
    foto: f.foto, pos: "50", riga: `Prossima tappa: parto il ${fmtLungo(f.data)}${f.guida ? ", da tour leader" : ""}.` }))];
const iOggi = voci.findIndex(v => v.oggi);

if (fatti.length >= 2) {
  const tempo = $("#tempo"), palco = $("#palco"), strati = $("#strati"), titoloPalco = $("#palco-titolo");
  const imgOggi = $("#scatto-a"), imgB = $("#scatto-b"), linea = $("#linea"), testi = $("#p-testi");
  const coloreOggi = getComputedStyle(document.documentElement).getPropertyValue("--oggi").trim();

  // posizioni: passo fisso, più spazio per gli anni saltati e prima di "oggi"
  let x = 0; const pos = [];
  voci.forEach((v, i) => {
    if (i) { x += 1 + Math.max(0, v.anno - voci[i - 1].anno - 1) * .6; if (v.oggi) x += .25; if (v.futuro) x += 1.1; }
    pos.push(x);
  });
  voci.forEach((v, i) => v.x = 2 + pos[i] / (pos[pos.length - 1] || 1) * 96);

  linea.hidden = false; $("#istruzione").hidden = false;
  linea.innerHTML = '<span class="binario"></span>';
  if (futuri.length) { const f = document.createElement("span"); f.className = "futuro"; f.style.left = voci[iOggi].x + "%"; f.style.right = "0"; linea.append(f); }
  voci.forEach(v => {
    if (v.oggi) return;
    const t = document.createElement("span");
    t.className = v.futuro ? "tacca-futura" : "tacca" + (v.guida ? " guida" : "");
    t.style.left = v.x + "%"; linea.append(t);
  });
  // etichette: anni, "oggi", mesi delle partenze; poi tolgo gli anni che si sovrappongono
  const etichette = []; let annoVisto = null;
  voci.forEach((v, i) => {
    let testo = null, cls = "etichetta";
    if (v.oggi) testo = "oggi";
    else if (v.futuro) { testo = fmtBreve(v.data); cls += " futura" + (i === voci.length - 1 ? " ultima" : ""); }
    else if (v.anno !== annoVisto) { testo = String(v.anno); annoVisto = v.anno; }
    if (!testo) return;
    const e = document.createElement("span"); e.className = cls + (i === 0 ? " prima" : ""); e.textContent = testo;
    e.style.left = (i === 0 ? v.x - 1 : v.x) + "%"; linea.append(e);
    etichette.push({ e, fissa: v.oggi || v.futuro });
  });
  const cur = document.createElement("span");
  cur.className = "cursore"; cur.tabIndex = 0; cur.setAttribute("role", "slider");
  cur.setAttribute("aria-label", "Viaggio sulla linea del tempo");
  cur.setAttribute("aria-valuemin", 0); cur.setAttribute("aria-valuemax", voci.length - 1);
  linea.append(cur);
  const sistemaEtichette = () => {
    etichette.forEach(x => x.e.hidden = false);
    const r = el => el.getBoundingClientRect();
    const fisse = etichette.filter(x => x.fissa).map(x => r(x.e));
    let prec = null;
    etichette.filter(x => !x.fissa).forEach(({ e }) => {
      const b = r(e), tocca = a => b.left < a.right + 6 && b.right > a.left - 6;
      if ((prec && tocca(prec)) || fisse.some(tocca)) e.hidden = true; else prec = b;
    });
  };

  // testi del pannello: l'area tiene l'altezza del viaggio più lungo, così la pagina sotto non salta
  function scrivi(v) {
    $("#p-viaggio").textContent = v.titolo;
    $("#p-anno").textContent = v.anno;
    $("#p-riga").textContent = v.riga || "";
    $("#p-ruolo").hidden = !v.guida;
    $("#p-video").hidden = !v.video;
    $("#p-partenza").hidden = !v.futuro;
    const fr = $("#p-frase"); fr.hidden = !v.frase; fr.textContent = v.frase ? `«${v.frase}»` : "";
  }
  let corrente = iOggi;
  function misura() {
    testi.style.minHeight = "";
    let h = 0; voci.forEach(v => { scrivi(v); h = Math.max(h, testi.offsetHeight); });
    testi.style.minHeight = h + "px"; scrivi(voci[corrente]);
    sistemaEtichette();
  }

  const src = v => `foto/${v.foto}.webp`;
  const precarica = i => { const v = voci[i]; if (v && v.foto) { const im = new Image(); im.decoding = "async"; im.src = src(v); } };

  function mostra(i) {
    i = Math.max(0, Math.min(voci.length - 1, i));
    corrente = i; const v = voci[i];
    tempo.style.setProperty("--cv", v.c || coloreOggi);
    cur.style.left = v.x + "%";
    cur.setAttribute("aria-valuenow", i); cur.setAttribute("aria-valuetext", `${v.titolo} ${v.anno}`);
    scrivi(v);
    if (v.oggi) { imgOggi.classList.add("is-on"); imgB.classList.remove("is-on"); palco.classList.remove("senza-foto"); }
    else if (v.foto) {
      imgB.hidden = false; imgB.style.objectPosition = `${v.pos}% 50%`;
      if (imgB.getAttribute("src") !== src(v)) imgB.src = src(v);
      imgB.alt = v.titolo; imgB.classList.add("is-on"); imgOggi.classList.remove("is-on"); palco.classList.remove("senza-foto");
    } else {
      imgOggi.classList.remove("is-on"); imgB.classList.remove("is-on");
      titoloPalco.textContent = v.titolo; palco.classList.add("senza-foto");
    }
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
    const r = linea.getBoundingClientRect(), p = (clientX - r.left) / r.width * 100;
    let best = 0; voci.forEach((v, i) => { if (Math.abs(v.x - p) < Math.abs(voci[best].x - p)) best = i; });
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
  cur.addEventListener("keydown", e => {
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

  // video: il lettore di Instagram si carica solo quando lo si apre, e si scarica alla chiusura
  const schermo = $("#schermo"), contVideo = $("#schermo-video");
  $("#p-video").addEventListener("click", () => {
    const v = voci[corrente]; if (!v.video) return;
    fermaLapse();
    schermo.style.setProperty("--cv", v.c || coloreOggi);
    $("#schermo-titolo").textContent = `${v.titolo}, ${v.anno}`;
    $("#schermo-link").href = v.video;
    const fr = document.createElement("iframe");
    fr.src = v.video + "embed/"; fr.title = `Video di ${v.titolo}`;
    fr.allow = "autoplay; encrypted-media; picture-in-picture; fullscreen"; fr.loading = "eager";
    contVideo.replaceChildren(fr);
    schermo.showModal();
  });
  $("#schermo-chiudi").addEventListener("click", () => schermo.close());
  schermo.addEventListener("click", e => { if (e.target === schermo) schermo.close(); });
  schermo.addEventListener("close", () => { contVideo.replaceChildren(); $("#p-video").focus(); });

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
      else { fermaLapse(); linea.querySelectorAll(".tacca-futura").forEach(t => t.classList.add("invito")); }
    };
    timer = setTimeout(passo, 700);
  } else mostra(iOggi);
}

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
