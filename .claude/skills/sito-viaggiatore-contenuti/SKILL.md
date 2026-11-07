---
name: sito-viaggiatore-contenuti
description: Dati, testi e foto per il sito personale del viaggiatore (viaggi fatti, prossime partenze, visite in cantina e degustazioni, interessi, contatti). Da usare ogni volta che si aggiunge o modifica un viaggio o una cantina, si scrivono bio, didascalie o frasi del sito, si preparano o ottimizzano le foto, o si decide come strutturare i dati, anche se l'utente dice solo "aggiungi il viaggio in Georgia" o "scrivimi la bio". Va usata insieme a sito-viaggiatore-design.
---

# Sito del viaggiatore: contenuti, testi e foto

Il sito vive dei suoi contenuti: un viaggio vero con una foto vera e una frase scritta dal viaggiatore vale più di qualunque effetto. Questa skill dice come rappresentare i dati, come scrivere i testi e come preparare le foto, in modo che il sito resti facile da aggiornare a mano anche da chi non è sviluppatore.

## 1. Dati: una riga per viaggio, nell'HTML

Come nel riferimento, i contenuti stanno nell'HTML (la pagina si legge anche senza JavaScript e i motori di ricerca vedono tutto) e i dati strutturati negli attributi `data-*`. Il JavaScript legge quegli attributi per costruire timeline, colori e stati. Lo schema completo, con esempi per viaggi, partenze, cantine e contatti, è in `references/schema-dati.md`.

Principi:

- **Una riga = un elemento.** Per aggiungere un viaggio si copia un `<li>` e si cambiano i valori. Sopra ogni lista c'è un commento HTML in italiano che spiega i campi, scritto per il viaggiatore e non per uno sviluppatore.
- **Date in ISO** (`2026-11-06`), anni come numeri, codici come stringhe. Il JS formatta in italiano (`6 nov`, `Dal 6 al 17 novembre 2026`) con `Intl.DateTimeFormat('it-IT')`.
- **Lo stato si calcola, non si scrive.** "Già fatto" o "prossimo" deriva dalla data rispetto a oggi; "quasi completo" deriva da posti e iscritti. Così una partenza passata scivola da sola tra i viaggi fatti.
- **Se i dati superano ~40 elementi o servono pagine per singolo viaggio**, si passa a file YAML/JSON + generatore statico: vedi `sito-statico-deploy`. Lo schema dei campi resta lo stesso.

## 2. Testi

Il sito parla in prima persona, con la voce del viaggiatore. La regola di fondo è la stessa della skill `scrittura-senza-ai-slop` se è installata (che si applica anche qui): fatti al posto degli aggettivi, niente slogan, niente frasi a effetto. Qui le regole specifiche per un sito personale.

**Prima di scrivere chiedi i fatti.** Per la bio: cosa fa nella vita, da quanto viaggia, che tipo di viaggi preferisce, un'abitudine o un difetto che lo rende riconoscibile. Per ogni viaggio: con chi, in che ruolo, una cosa successa davvero. Se il viaggiatore non dà una frase sua per un viaggio, il campo resta vuoto: **le frasi personali non si inventano mai**, perché sono la parte del sito che i suoi amici riconoscerebbero come falsa.

**Bio.** Una frase d'attacco e un paragrafo di 2–4 frasi. Esempio di tono dal riferimento: "Sono un partecipante come gli altri, solo con qualche pensiero in più." Funziona perché è autoironica, specifica sul ruolo e non usa nessun aggettivo da brochure.

**Didascalie e schede.** Nome del luogo come lo direbbe lui ("Lofoten", non "Le magiche isole Lofoten"), anno, ruolo. Per le cantine: nome della cantina, zona, vino, annata, mese della visita.

**Interfaccia.** Pulsanti con verbi che dicono cosa succede: "Scrivimi su WhatsApp", "Iscriviti", "Scheda del viaggio". Sentence case, niente maiuscolo, niente frecce nel testo dei pulsanti. Gli stati usano le stesse parole che il viaggiatore o il tour operator usano già.

**Parole da non usare nel sito**: passione, esperienze uniche, avventura indimenticabile, scoprire il mondo, viaggiatore curioso, anima, emozioni, wanderlust, eccellenza, territorio (come parola vuota), "il viaggio è...". Se una frase regge solo con una di queste parole, manca il fatto: chiedilo.

**Contrapposizioni e massime**: niente "non è un viaggio, è...", niente chiusure aforistiche. Un motto nel piede è ammesso se è una frase che il viaggiatore dice davvero.

## 3. Foto

Le foto sono il contenuto principale e il punto in cui un sito statico diventa lento. Usa `scripts/prepara_foto.py`:

```bash
python scripts/prepara_foto.py originali/ --out foto/ --json foto/colori.json
```

Lo script, per ogni immagine:

- corregge l'orientamento e **rimuove tutti i metadati EXIF, GPS compreso** (le foto di un viaggiatore contengono spesso le coordinate di casa o dell'alloggio);
- produce un taglio grande (lato lungo 1600px) e una miniatura (480px), in WebP e in JPEG di riserva, con nomi in minuscolo senza spazi;
- calcola il colore del viaggio: la tinta più satura che occupa almeno il 6% della foto, scurita fino a un contrasto di circa 9:1 col testo bianco (lo stesso criterio del riferimento), e lo scrive nel JSON insieme a larghezza, altezza e peso;
- avvisa se un file supera i limiti di peso (grande > 250 KB, miniatura > 40 KB).

In HTML usa `<picture>` con WebP e JPEG, `width`/`height` reali, `loading="lazy"` tranne l'hero, `alt` descrittivo ("Sul passo sopra la valle di Ushguli, 2024"), vuoto solo per foto puramente decorative.

**Diritti delle foto.** Usa foto del viaggiatore. Se servono foto altrui (per esempio per le prossime partenze), solo con licenza che lo consenta e credito nel piede della pagina, come fa il riferimento.

## 4. Privacy

- Niente indirizzo di casa, niente date di viaggi in corso in tempo reale se il viaggiatore vive da solo (segnala il rischio e lascia decidere a lui).
- Numero di telefono: meglio un link `wa.me` che il numero in chiaro nel testo.
- Se ci sono contenuti privati (diario, foto di gruppo con altre persone), non metterli in una cartella "nascosta" pensando che basti: su un hosting statico pubblico tutto ciò che è nel repository è scaricabile. Vedi `sito-statico-deploy` per le opzioni.

## File di questa skill

- `references/schema-dati.md`: attributi e markup per viaggi, partenze, cantine, contatti, con esempi.
- `scripts/prepara_foto.py`: ottimizzazione foto, rimozione EXIF, colore del viaggio.
