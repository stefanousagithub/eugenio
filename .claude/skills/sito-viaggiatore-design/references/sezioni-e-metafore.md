# Sezioni e metafore

Catalogo di sezioni per il sito del viaggiatore. Non vanno messe tutte: scegli quelle per cui esistono dati veri (una sezione con due elementi inventati è peggio di nessuna sezione) e tieni l'ordine "chi sono → cosa ho fatto → cosa sto per fare → come scrivermi".

## Indice

1. Regola per le metafore
2. Hero (scegline uno)
3. Sezioni di contenuto
4. Sezioni per i viaggi enologici
5. Contatti e azione fissa
6. Metafore da evitare

## 1. Regola per le metafore

Una metafora funziona quando prende un oggetto **reale** del mondo del viaggiatore, con il suo comportamento fisico, e lo usa per mostrare un dato vero. Il tabellone a palette funziona perché le partenze *sono* partenze e il tabellone si comporta come quello vero. Una metafora che decora soltanto (una valigia disegnata accanto al titolo "Viaggi") non è una metafora, è clip-art.

Al massimo due metafore per pagina: una nell'hero, una in una sezione. Le altre sezioni usano il linguaggio iOS di base.

## 2. Hero (scegline uno)

**H1. Ritratto nel tempo** (quello del riferimento). Foto per ogni viaggio, linea del tempo trascinabile, colore del viaggio. Funziona con almeno 6–8 viaggi con foto in cui compare il viaggiatore. Con meno viaggi la linea è troppo corta e l'effetto si perde: scegli un altro hero.

**H2. Passaporto.** L'hero è la pagina dei timbri: un timbro per paese (forma, colore e data diversi, leggermente ruotati, inchiostro con texture SVG leggera), che all'apertura vengono "timbrati" in sequenza una volta sola. Toccando un timbro si apre il viaggio. Adatto quando il dato forte è il numero di paesi più che le foto.

**H3. Carta d'imbarco.** Nome come passeggero, "da" città di casa "a" prossima meta, data, gate. Lo strappo del talloncino rivela il prossimo viaggio. Adatto quando c'è sempre una partenza imminente da mettere in evidenza.

**H4. Annate.** Per un profilo centrato sul vino: la linea del tempo diventa una fila di annate (gli anni come su un'etichetta, peso 200 grande), ogni annata mostra i viaggi e le cantine di quell'anno. Variante di H1 che tiene la stessa fisica di trascinamento.

## 3. Sezioni di contenuto

**Bio.** Una frase d'attacco (22px semibold) e un paragrafo. Niente titolo "Chi sono": si capisce. Deve contenere almeno un fatto preciso e un tratto di carattere (nel riferimento: "giornate intense con la sveglia presto, anche a discapito della comodità").

**Dove sono stato (griglia).** Tessere 3:4 in 3 colonne su telefono, 4 su desktop largo. Badge solo per un ruolo che conta (es. "Guida", "Vendemmia"). Ordine cronologico, dal più vecchio, perché la griglia racconta un percorso.

**Prossime partenze (tabellone).** Solo se il viaggiatore organizza o accompagna viaggi a cui altri possono iscriversi. Altrimenti diventa "Prossimo viaggio" con una sola scheda e un conto alla rovescia.

**Mappa leggera (facoltativa, mai hero).** SVG statico del mondo (o dell'Italia per le zone vinicole) con i paesi o le regioni visitate in accento e gli altri in `scheda-2`. Niente librerie di mappe, niente tile, niente pin: pesa poco, si legge sul telefono, non richiede API key.

**Numeri (facoltativa).** Al massimo una riga di testo nel pannello dell'hero ("12 viaggi, 5 da coordinatore") invece di una sezione con contatori animati.

**Diario o racconti (facoltativa).** Se il viaggiatore scrive, una lista di righe stile Note di iOS (titolo, data, prima riga) che portano a pagine dedicate. Questo è il caso in cui conviene passare a un generatore statico (vedi `sito-statico-deploy`).

## 4. Sezioni per i viaggi enologici

Il vino ha oggetti fisici molto riconoscibili. Usane uno, bene.

**V1. Carta dei vini.** La sezione dei viaggi in cantina impaginata come la carta di un ristorante: regione come intestazione, poi righe "Cantina — Vino, annata" con la zona e il mese della visita a destra in tabular-nums. È sobria, densa, leggibile, e si costruisce con la stessa riga dei contatti iOS senza icona. Ottima come default.

**V2. Scheda di degustazione.** Per ogni visita importante, una scheda con il vino assaggiato e una nota personale breve (una frase sua, mai inventata). Facoltativo un piccolo grafico radar a 5 assi (acidità, tannino, corpo, frutto, persistenza) disegnato in SVG con l'accento, solo se il viaggiatore fornisce i valori.

**V3. Etichette.** Tessere in proporzione da etichetta (circa 4:5 o 3:4) con il nome della cantina composto come un'etichetta: qui è ammesso il secondo carattere (un serif o un display coerente col vino), solo dentro le etichette. Rischio: scivolare nel cliché "enoteca elegante"; tienilo sullo sfondo scuro iOS, senza texture di carta.

**V4. Calendario della vigna.** Se fa vendemmie o viaggi stagionali: una riga di 12 mesi con i periodi dei viaggi segnati sui mesi del ciclo della vite (potatura, fioritura, vendemmia). Il dato è vero e la metafora è sua.

Il colore dei viaggi in cantina può venire dal vino (rosso, rosato, bianco, orange) invece che dalla foto, se il viaggiatore indica il vino principale di ogni visita.

## 5. Contatti e azione fissa

- Righe stile Impostazioni, una per canale reale (WhatsApp, Instagram, email). Il colore dell'icona è quello del servizio.
- Barra fissa in basso con l'azione principale (di solito "Scrivimi" su WhatsApp con messaggio precompilato) e un pulsante quadrato secondario. Sfumatura sotto la barra verso lo sfondo. Su desktop (layout B) la barra diventa una riga di pulsanti in fondo alla colonna destra o in cima a essa, non resta fissa.
- Ogni link a un messaggio precompilato contiene il contesto (quale viaggio, quale data), così chi riceve sa già di cosa si parla.

## 6. Metafore da evitare

- Valigie, aeroplanini, bussole, mappamondi, calici e grappoli come icone decorative.
- Linee tratteggiate di aerei che attraversano la pagina.
- Polaroid inclinate sparse con ombre: è il secondo cliché più usato dopo l'hero a tutto schermo.
- Texture di carta, macchie di vino, sughero.
- Font "scritto a mano" per dare un tocco personale: il tocco personale lo danno i testi.
