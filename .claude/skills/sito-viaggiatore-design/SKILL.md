---
name: sito-viaggiatore-design
description: Direzione visiva e di interazione per il sito personale di un viaggiatore (viaggi fatti, prossime partenze, enoturismo e viaggi in cantina, interessi, contatti), nello stile "app nativa iOS" di manfreditocci.it/avventure. Da usare ogni volta che si progetta, si costruisce, si rivede o si estende una pagina o una sezione di questo sito (hero, timeline dei viaggi, griglia delle mete, degustazioni, contatti, layout desktop), anche se l'utente chiede solo "fai la sezione X" o "rendilo più bello" e non parla di design. Va usata insieme a sito-viaggiatore-contenuti (dati, testi e foto) e sito-statico-deploy (build e pubblicazione).
---

# Sito del viaggiatore: direzione di design

Il sito è il profilo personale di una persona che viaggia: dove è stata, dove sta per andare, i viaggi legati al vino (cantine, vendemmie, degustazioni) e gli altri interessi. Chi lo apre arriva quasi sempre da Instagram o da un link condiviso, quindi **dal telefono**, con pochi secondi di attenzione. Il sito deve far capire in un colpo d'occhio chi è questa persona e cosa ha visto, e dare un modo immediato per scriverle.

Il riferimento visivo è manfreditocci.it/avventure. La sua analisi completa (token, componenti, interazioni, cosa lo rende diverso da un sito generato) è in `references/riferimento-manfreditocci.md`: **leggila prima di progettare qualunque cosa**, perché le scelte sotto ne derivano. Ci ispiriamo al sistema, non cloniamo la pagina: testi, foto, nomi e struttura dei contenuti sono del nuovo viaggiatore.

## Perché il riferimento funziona (e cosa ne prendiamo)

Il riferimento non sembra un sito fatto con l'AI perché non prende in prestito il linguaggio dei siti web: prende quello di oggetti che la gente conosce già.

1. **Linguaggio di un'app nativa iOS.** Font di sistema (SF Pro su Apple, Segoe/Roboto altrove), colori di sistema iOS, schede con angoli morbidi, liste come le Impostazioni, pulsanti che si comprimono al tocco. Sul telefono sembra un'app, non una pagina.
2. **Una sola interazione memorabile.** L'hero è una foto 4:5 con una linea del tempo sotto: trascinandola (o scorrendo la foto col dito) si passa da un viaggio all'altro, e foto e pannello prendono il colore del viaggio. All'apertura parte una volta sola un time-lapse dal primo viaggio a oggi. Tutto il resto della pagina è quieto.
3. **Metafore fisiche al posto dei componenti web.** Le prossime partenze sono un tabellone a palette (split-flap) come negli aeroporti; i posti liberi sono pallini pieni e vuoti; i contatti sono righe con l'icona colorata come in iOS.
4. **Colonna stretta e disciplina.** Una colonna di 520px al massimo, anche su desktop; gerarchia data da peso e dimensione del font, non da decorazioni.
5. **Testi in prima persona, concreti, autoironici.** Niente slogan da agenzia.

Il nuovo sito eredita i punti 1, 4 e 5 come base, e reinterpreta 2 e 3 sul soggetto del nuovo viaggiatore (vedi `references/sezioni-e-metafore.md`).

## Processo obbligatorio

### 1. Raccogli i fatti prima di disegnare

Servono: nome e come vuole essere presentato, elenco dei viaggi (meta, anno, ruolo, foto), eventuali prossime partenze, viaggi enologici (cantine, zone, vini), altri interessi, canali di contatto. Se mancano, chiedili. Una pagina senza fatti si riempie di aggettivi e di sezioni generiche ("La mia filosofia di viaggio"), che sono la prima cosa che la fa sembrare finta. Per i dati usa lo schema di `sito-viaggiatore-contenuti`.

### 2. Piano di design compatto (prima del codice)

Scrivi un piano breve con:

- **Token colore**: parti da quelli del riferimento (tema scuro di default, chiaro con `prefers-color-scheme`). L'accento giallo `#ffd60a` è la firma di Manfredi: per il nuovo viaggiatore scegli **un altro colore di sistema iOS** coerente col soggetto (per un profilo legato al vino, ad esempio un rosso vinaccia derivato da `systemPink`/`systemRed` desaturato, o un verde vigna da `systemGreen`) e verifica il contrasto del testo nero o bianco sopra di esso (almeno 4.5:1).
- **Tipografia**: stack di sistema come nel riferimento. Un secondo carattere è ammesso **solo** per un elemento-firma legato al vino (per esempio le etichette delle bottiglie o le annate), mai per titoli e testo corrente.
- **Layout**: wireframe ASCII per telefono (390px) e desktop (1440px). Vedi "Desktop" sotto.
- **L'elemento memorabile**: quale interazione fa da hero e perché è legata a *questo* viaggiatore. Una sola.

Poi rileggi il piano e chiediti: "Se mi chiedessero un sito per un altro viaggiatore qualunque, arriverei qui?" Se sì per qualche voce, cambiala e scrivi cosa hai cambiato.

### 3. Costruisci

Regole di costruzione nella sezione "Sistema" sotto. Le sezioni disponibili e come adattarle sono in `references/sezioni-e-metafore.md`. Per la fisica delle interazioni (trascinamento 1:1, velocità al rilascio, interrompibilità) segui la skill esterna `apple-design` di Emil Kowalski se è installata; altrimenti i principi riassunti in `references/riferimento-manfreditocci.md`, sezione "Interazioni".

### 4. Guarda quello che hai fatto

Fai screenshot a 390×844 (telefono), 820×1180 (tablet) e 1440×900 (desktop), in tema scuro e chiaro, con `scripts/screenshot.py`. Guardali davvero e correggi: testo che va a capo male, foto con il soggetto coperto dal nome, schede che saltano, contrasto basso nel tema chiaro. Poi passa la checklist in `references/qa-visivo.md`. Non consegnare senza aver guardato gli screenshot.

## Sistema

### Base (non negoziabile)

- Mobile-first. Il telefono è il caso principale, il desktop è un adattamento.
- `viewport-fit=cover` e `env(safe-area-inset-*)` sui bordi e sulla barra fissa in basso, perché su iPhone il contenuto finisce sotto la barra di sistema.
- Font di sistema, `font-size` base 17px, interlinea ~1.47, `letter-spacing` leggermente negativo (−0.01em sul testo, −0.025/−0.03em sui titoli), `-webkit-font-smoothing: antialiased`. Sono i valori di iOS e sono il motivo per cui il testo "sembra Apple".
- Numeri con `font-variant-numeric: tabular-nums` ovunque ci siano anni, date, conteggi.
- `text-wrap: balance` sui titoli, `pretty` sui paragrafi.
- Feedback al tocco su `:active` (scale 0.97–0.985, 160ms, ease-out `cubic-bezier(.23,1,.32,1)`), niente hover come unico segnale.
- `:focus-visible` evidente, `prefers-reduced-motion` rispettato (il time-lapse non parte, le transizioni diventano quasi istantanee).
- Immagini con `loading="lazy"` tranne l'hero (`fetchpriority="high"`), dimensioni dichiarate per evitare salti di layout, fallback a colore pieno se una foto non carica.

### Gerarchia dei raggi

Il riferimento non mette lo stesso raggio su tutto, e questo conta: tessere della griglia 14px, righe di contatto 18px, schede delle partenze 22px, hero su desktop 28px, pillole 999px. Più il contenitore è grande e importante, più il raggio cresce. Non usare un raggio unico.

### Colore

- Superfici: nero puro `#000` (non `#0b0b0b`), schede `#1c1c1e`, schede secondarie `#2c2c2e`; in chiaro `#f2f2f7`, `#fff`, `#e5e5ea`. Sono i grigi di sistema iOS.
- Testo secondario con trasparenza (`rgba(235,235,245,.64)` / `rgba(60,60,67,.74)`), non grigi pieni.
- Un accento solo, usato per: azione principale, ruolo speciale (es. "coordinatore", "in vendemmia"), stato "quasi pieno". Non come decorazione.
- Il colore di ogni viaggio viene dalla sua foto (la tinta più satura che occupa almeno il 6% dell'immagine, scurita per avere ~9:1 col testo bianco). Lo calcola `prepara_foto.py` di `sito-viaggiatore-contenuti`: usalo per pannelli e fallback.

### Desktop

Il riferimento tiene la colonna di 520px anche su desktop, con l'hero arrotondato. È una scelta onesta ma su un monitor da 1440px lascia due fasce vuote. Proponi all'utente una di queste due strade e fagli scegliere (con screenshot di entrambe se possibile):

- **A. Colonna "app" centrata** (come il riferimento): sotto i 1024px è identico al telefono; sopra, colonna 520–560px centrata, sfondo pieno. Pro: identità intatta, zero rischio. Contro: spazio sprecato.
- **B. Palco fisso + contenuto che scorre**: da 1024px in su due colonne; a sinistra l'hero con la linea del tempo resta fermo (`position: sticky`, altezza 100svh meno margini), a destra scorrono bio, partenze, griglia (che passa a 4 colonne), contatti; la barra d'azione fissa diventa una riga di pulsanti dentro la colonna destra. Pro: usa lo schermo e tiene l'interazione sempre visibile. Contro: più CSS da curare, e l'hero va ripensato in proporzione 4:5 dentro un'altezza fissa.

Default se l'utente non sceglie: B, perché ha chiesto esplicitamente che il sito sia bello anche su PC.

### Cosa non fare (tell tipici di un sito generato, in questo contesto)

- Hero con foto a tutto schermo, titolo centrato enorme e "Esplora il mondo con me" sopra. È il template di ogni travel blog.
- Mappa del mondo interattiva con i pin come elemento principale: pesante, generica, e sul telefono si usa male. Una mappa può esserci come elemento secondario e leggero (SVG statico con i paesi colorati), mai come hero.
- Card tutte uguali con ombra grigia, gradienti decorativi, fade-in su ogni sezione allo scroll.
- Etichette in maiuscoletto spaziato sopra ogni titolo, contatori animati ("47 paesi!"), icone di bicchieri e valigie come decorazione.
- Sfondo crema con serif e accento terracotta (il cliché "vino ed eleganza"): il vino si racconta con contenuti e foto, non con una palette da enoteca.
- Testi da agenzia: "passione", "esperienze uniche", "scoprire il mondo", "viaggiatore curioso". Le regole di scrittura sono in `sito-viaggiatore-contenuti`.

### Interazioni (dalle skill apple-design ed emil-design-eng)

- Swipe sulla foto: soglia di 10px prima di decidere la direzione, poi 1:1; ai bordi resistenza crescente (`rubberband(d, dim) = d·dim·0.55 / (dim + 0.55·|d|)`); al rilascio si proietta il punto d'arrivo con la decelerazione Apple (`v/1000 · 0.998 / 0.002`) e si sceglie il viaggio da lì, non dalla posizione del dito.
- Il passaggio è direzionale: il contenuto esce dal lato del gesto ed entra dall'altro (WAAPI, interrompibile); con `prefers-reduced-motion` diventa un cambio secco.
- Un dito solo: i puntatori successivi al primo si ignorano.
- Le tessere della griglia aprono quel viaggio sulla linea del tempo e scrivono `#nome-viaggio` nell'URL; aprendo un link con quell'hash il time-lapse non parte e si va diretti al viaggio.
- Si precaricano le foto dei viaggi adiacenti.
- Date brevi con spazio non separabile (`13\u00a0dic`), `touch-action: manipulation` su link e pulsanti, `scroll-padding-bottom` pari alla barra fissa perché il focus da tastiera non finisca sotto.

## Spendi il coraggio in un punto

Un elemento memorabile (di solito l'hero con la linea del tempo), un secondo elemento con una metafora fisica legata al soggetto (il tabellone, o la "carta dei vini" dei viaggi in cantina), tutto il resto sobrio e preciso. Prima di consegnare, togli una cosa.

## File di questa skill

- `references/riferimento-manfreditocci.md`: analisi del sito di riferimento, token, componenti, interazioni. Leggere sempre.
- `references/sezioni-e-metafore.md`: catalogo delle sezioni possibili e delle metafore adatte a un viaggiatore e ai viaggi enologici. Leggere quando si sceglie la struttura o si aggiunge una sezione.
- `references/qa-visivo.md`: checklist prima della consegna.
- `scripts/screenshot.py`: screenshot automatici a più larghezze e temi (Playwright).
