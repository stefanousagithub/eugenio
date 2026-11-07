# Analisi del riferimento: manfreditocci.it/avventure

Sorgente pubblico: github.com/Manfr3d1/avventure (pagina) e github.com/Manfr3d1/manfr3d1.github.io (radice del dominio). Analizzato a novembre 2026. È una pagina singola in HTML, CSS e JavaScript senza framework né build (~62 KB di HTML, di cui ~15 KB di CSS e ~27 KB di JS inline), ospitata su GitHub Pages con dominio personalizzato.

Usalo come sistema da cui partire, non come pagina da copiare: testi, foto, contenuti e marchio appartengono a Manfredi Tocci.

## Indice

1. Struttura della pagina
2. Token
3. Componenti
4. Interazioni
5. Dettagli che fanno la differenza
6. Architettura tecnica

## 1. Struttura della pagina (dall'alto)

1. **Hero "ritratto nel tempo"**: foto 4:5 (max 66svh), nome e ruolo in basso a sinistra sopra la foto, che sfuma nel colore del viaggio. Sotto, un pannello dello stesso colore con la linea del tempo, nome del viaggio + anno, una riga di contesto, una frase personale facoltativa e il link alla scheda.
2. **Bio**: una frase d'attacco in 22px semibold, poi un paragrafo in testo secondario. Niente titolo di sezione.
3. **Prossime partenze**: schede con foto di sfondo velata, data, conto alla rovescia, nome del viaggio sul tabellone a palette, periodo, posti come pallini, stato (Confermato / Quasi completo / Completo / "Si parte con 3 iscritti"), pulsanti "Iscriviti" e "Scrivimi per info" (WhatsApp con messaggio precompilato).
4. **Dove sono già stato**: griglia 3 colonne di tessere 3:4 con foto, nome e anno; badge giallo per il ruolo da coordinatore.
5. **Contatti**: righe come le Impostazioni di iOS (icona colorata 40px, titolo, sottotitolo, pillola d'azione a destra).
6. **Piede**: un motto in 22px bold, due righe di testo piccolo, crediti foto.
7. **Barra d'azione fissa** in basso: pulsante giallo largo (WhatsApp) + pulsante quadrato Instagram, con una sfumatura verso lo sfondo dietro, così il testo che scorre non si legge sotto i pulsanti.

## 2. Token

Colore, tema scuro (default):

| Token | Valore | Uso |
|---|---|---|
| sfondo | `#000` | pagina |
| scheda | `#1c1c1e` | schede, righe contatto |
| scheda-2 | `#2c2c2e` | pulsanti secondari, fallback foto |
| sep | `rgba(84,84,88,.65)` | separatori |
| testo | `#fff` | |
| testo-2 | `rgba(235,235,245,.64)` | testo secondario |
| accento | `#ffd60a` (systemYellow) | azione principale, ruolo, "quasi completo" |
| verde | `#30d158` | stato confermato |
| blu | `#0a84ff` | focus |
| tinta | `rgba(255,255,255,.12)` | pillole secondarie |

Tema chiaro: sfondo `#f2f2f7`, scheda `#fff`, scheda-2 `#e5e5ea`, testo `#000`, testo-2 `rgba(60,60,67,.74)`, accento `#ffcc00` con una variante scura `#8a6100` per il testo giallo su bianco (il giallo puro su bianco non si legge), verde `#248a3d`, blu `#0063cc`. Sono i colori di sistema iOS nelle due modalità.

Tipografia: stack `-apple-system, BlinkMacSystemFont, "SF Pro Text"/"SF Pro Display", "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif`. Scala usata:

| Ruolo | Peso / dimensione / interlinea | Tracking |
|---|---|---|
| Nome nell'hero | 800 / clamp(34px,10vw,54px) / 1.02 | −0.03em |
| Numero del conto alla rovescia | 200 / clamp(104px,34vw,168px) / .82 | −0.04em |
| Titolo sezione | 700 / 22px / 1.2 | −0.025em |
| Nome viaggio nel pannello | 700 / 28px; anno 300 / 28px | −0.025em |
| Nome scheda partenza | 700 / 21px | −0.02em |
| Testo | 400 / 17px / 1.47 | −0.01em |
| Secondario | 15px; didascalie 13–14px; micro 12px | |

Il contrasto tra pesi estremi (800 per il nome, 200–300 per numeri e anni) è una delle firme visive: dà carattere senza un secondo font.

Movimento: `--ease-out: cubic-bezier(.23,1,.32,1)`, `--ease-in-out: cubic-bezier(.77,0,.175,1)`. Pressione 160ms, cambio colore del viaggio 500ms, dissolvenza foto 140–200ms.

Spaziature: colonna `max-width: 520px`, padding laterale 16–20px, 40px tra sezioni, gap griglia 6px, gap schede 10–12px.

Raggi: tessere 14px, icone 11–12px, righe contatto e pulsanti fissi 18px, schede partenza 22px, hero su desktop 28px, pillole 999px.

## 3. Componenti

**Palco dell'hero.** Due livelli `<img>` sovrapposti per le dissolvenze. Un `::after` sfuma dal basso nel colore del viaggio (`color-mix` con fallback a gradiente nero), così foto e pannello sembrano una superficie unica. Se la foto manca, al suo posto compare il nome del viaggio in 300 enorme e semitrasparente.

**Linea del tempo.** Binario 3px, una tacca per viaggio (gialla se da coordinatore), il futuro tratteggiato a puntini con cerchi gialli per le partenze, cursore bianco 23px con ombra. Le posizioni hanno passo fisso tra un viaggio e l'altro, con spazio in più per gli anni saltati. Le etichette mostrano gli anni senza sovrapporsi, poi "oggi" e i mesi delle partenze.

**Tabellone a palette.** Ogni carattere è una cella con due metà fisse e due "fogli" che ruotano sul cardine (`perspective`, `backface-visibility: hidden`, una riga scura a metà altezza). Massimo 11 caratteri per riga, righe separate da "/" nel dato (es. `GUATEMALA/DISCOVERY`). L'animazione: la metà superiore cade e scopre la nuova lettera, poi la metà inferiore si chiude sopra la vecchia.

**Posti come pallini.** Un pallino 8px per posto: pieno se preso, solo contorno se libero. Rende la disponibilità leggibile senza leggere numeri.

**Tessera della griglia.** 3:4, raggio 14px, foto `object-fit: cover`, didascalia in basso su gradiente scuro solo se c'è la foto (`:has(img)`), colore di riserva `--c` per tessera.

**Riga contatto.** Icona quadrata colorata come nelle Impostazioni (colore del servizio), titolo 17px semibold, sottotitolo 14px secondario, pillola d'azione a destra ("Scrivi", "Segui").

## 4. Interazioni

- **Time-lapse all'apertura**: una volta sola, dal primo viaggio a oggi, poi si ferma su "oggi". Qualunque tocco lo interrompe. Disattivato con `prefers-reduced-motion`.
- **Trascinare la linea**: il cursore segue il dito 1:1 (`touch-action: none`, Pointer Events), la foto cambia con dissolvenza breve.
- **Scorrere la foto col dito**: la foto segue il dito e quella accanto entra dal lato; verso sinistra si va avanti nel tempo; si passa al viaggio successivo se il dito ha percorso un quinto della larghezza o l'ha lanciata; ai bordi della linea la foto fa resistenza.
- **Caricamento progressivo**: durante lo scorrimento veloce si usano le miniature, a riposo arriva la foto grande.
- **Niente salti di pagina**: l'area dei testi del pannello tiene sempre l'altezza del viaggio con il testo più lungo.
- **Accessibilità**: il cursore è focalizzabile e si muove con le frecce; un `aria-live="polite"` annuncia il viaggio corrente.
- Le partenze passate si spostano da sole tra i viaggi fatti, in base alla data.

Questi comportamenti coincidono con i principi Apple di "Designing Fluid Interfaces" (risposta immediata, manipolazione diretta, interrompibilità, momento al rilascio, resistenza ai bordi). La skill esterna `apple-design` di Emil Kowalski li spiega in dettaglio con codice per il web.

## 5. Dettagli che fanno la differenza

- Colore di ogni viaggio estratto dalla foto (tinta più satura con almeno il 6% dei pixel, 18 spicchi da 20°, luminosità calibrata per ~9:1 col bianco), con override manuale quando due viaggi vicini verrebbero dello stesso colore.
- Attributo per alzare la foto grande di N% quando il soggetto finirebbe sotto il nome, con sfumatura che si allunga di conseguenza.
- Messaggi WhatsApp precompilati con nome del viaggio, data e codice.
- Etichette di stato con la stessa logica e le stesse parole del sito del tour operator, così chi le legge non deve tradurle.
- Commenti HTML in italiano che spiegano a Manfredi come aggiungere un viaggio copiando una riga: la pagina è pensata per essere mantenuta a mano da chi non è sviluppatore.
- `noindex` sulla radice finché il sito personale non è pronto.
- Favicon SVG inline (quadrato nero arrotondato con cerchio giallo): nessuna richiesta in più.

## 6. Architettura tecnica

- Contenuto renderizzato nell'HTML (le liste esistono senza JS); i dati stanno negli attributi `data-*` di ogni `<li>`. Il JS legge quegli attributi e costruisce timeline, palette e stati. Se il JS non parte, la pagina resta leggibile.
- Foto in due tagli: `foto/<nome>.jpg` (grande) e `foto/mini/<nome>.jpg` (miniatura).
- GitHub Action giornaliera (cron) che legge iscritti e posti da un'API pubblica del tour operator e riscrive gli attributi nell'HTML con un commit automatico. È il modo per avere dati "vivi" su un hosting statico senza server.
- Una sottocartella con nome non indovinabile ospita un diario privato installabile come PWA (manifest + service worker).
- Costo: zero. GitHub Pages per l'hosting, solo il dominio è a pagamento.
