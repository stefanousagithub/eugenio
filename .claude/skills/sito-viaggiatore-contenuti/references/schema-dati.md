# Schema dei dati

I dati stanno negli attributi `data-*` di elementi `<li>` già renderizzati nell'HTML. Il contenuto visibile dentro il `<li>` è la versione senza JavaScript; il JS lo arricchisce. Ogni lista ha sopra un commento in italiano che spiega i campi a chi aggiorna il sito a mano.

## Viaggi fatti

```html
<!-- VIAGGI FATTI, dal più vecchio. Per aggiungerne uno copia una riga <li> e cambia i dati.
     data-anno: anno del viaggio. data-mese (facoltativo): 1-12, serve a ordinare viaggi dello stesso anno.
     data-tipo: "viaggio" oppure "cantina" (i viaggi in cantina compaiono anche nella carta dei vini).
     data-ruolo (facoltativo): "guida", "vendemmia", ... mostra un'etichetta sulla tessera.
     data-foto: nome del file in foto/ (la miniatura è in foto/mini/ con lo stesso nome).
     data-colore (facoltativo): colore del viaggio; se manca si usa quello calcolato dalla foto.
     data-alza (facoltativo): alza la foto grande di N% se il soggetto finisce sotto il nome.
     data-frase (facoltativo): solo una frase tua, testuale. Se non c'è, lascialo vuoto. -->
<ol class="griglia">
  <li data-anno="2024" data-mese="9" data-tipo="viaggio" data-titolo="Georgia, Svaneti"
      data-breve="Svaneti" data-foto="svaneti.jpg" data-colore="#3d5a4a" data-frase="">
    <a class="tessera" href="#svaneti">
      <picture>
        <source srcset="foto/mini/svaneti.webp" type="image/webp">
        <img src="foto/mini/svaneti.jpg" width="480" height="640" alt="Torri di Ushguli sotto la neve, 2024" loading="lazy">
      </picture>
      <span class="didascalia"><b>Georgia, Svaneti</b><span class="anno">2024</span></span>
    </a>
  </li>
</ol>
```

## Prossime partenze

```html
<!-- PARTENZE: una riga per partenza. Dal giorno della partenza passa da sola tra i viaggi fatti.
     data-dal / data-al: date ISO. data-tabellone: righe del tabellone separate da "/", max 11 caratteri per riga.
     data-posti e data-iscritti (facoltativi): se ci sono, compaiono i pallini e lo stato.
     data-minimo (facoltativo): iscritti minimi per partire.
     data-iscrizione (facoltativo): link per iscriversi. data-info: testo precompilato del messaggio WhatsApp. -->
<ul class="tabellone">
  <li data-dal="2027-09-12" data-al="2027-09-19" data-titolo="Vendemmia in Langa"
      data-tabellone="VENDEMMIA/IN LANGA" data-posti="8" data-iscritti="3" data-minimo="4"
      data-foto="partenze/langa.jpg" data-iscrizione="https://..." data-info="Ciao, vorrei info sulla vendemmia in Langa di settembre">
    ...versione statica della scheda...
  </li>
</ul>
```

Stato calcolato (adatta le parole a quelle che il viaggiatore usa):

| Condizione | Etichetta |
|---|---|
| iscritti ≥ posti | Completo |
| posti − iscritti ≤ 3 | Quasi completo |
| iscritti ≥ minimo | Confermato |
| altrimenti | Si parte con N iscritti |

## Visite in cantina (carta dei vini)

Le visite in cantina possono essere viaggi a sé (`data-tipo="cantina"` nella griglia) oppure righe di una sezione dedicata. Per la sezione:

```html
<!-- CANTINE, raggruppate per regione. data-vino: vino principale assaggiato. data-annata: annata del vino.
     data-colore-vino: rosso | rosato | bianco | orange | bollicine (colora la riga).
     data-quando: mese e anno della visita, in ISO (2025-10). data-nota (facoltativo): una frase tua. -->
<section class="carta" aria-labelledby="t-cantine">
  <h2 id="t-cantine">Cantine</h2>
  <h3>Piemonte</h3>
  <ul>
    <li data-cantina="Nome cantina" data-zona="Barolo" data-vino="Barolo" data-annata="2019"
        data-colore-vino="rosso" data-quando="2025-10" data-nota="">
      <span class="vino"><b>Nome cantina</b> Barolo 2019</span>
      <span class="quando">ott 2025</span>
    </li>
  </ul>
</section>
```

## Contatti

```html
<!-- CONTATTI: una riga per canale. data-servizio: whatsapp | instagram | email | altro (sceglie icona e colore). -->
<ul class="contatti">
  <li data-servizio="whatsapp">
    <a class="contatto" href="https://wa.me/39XXXXXXXXXX?text=Ciao%2C%20ti%20scrivo%20dal%20sito">
      <span class="contatto-icona" style="--i:#25d366">...svg...</span>
      <span class="testi"><b>WhatsApp</b><small>Per info sui viaggi</small></span>
      <span class="contatto-cta">Scrivi</span>
    </a>
  </li>
</ul>
```

## Passaggio a YAML/JSON (quando il sito cresce)

Con un generatore statico gli stessi campi diventano un file per collezione:

```yaml
# contenuti/viaggi.yaml
- titolo: Georgia, Svaneti
  breve: Svaneti
  anno: 2024
  mese: 9
  tipo: viaggio
  foto: svaneti.jpg
  colore: "#3d5a4a"
  frase: ""
```

I nomi dei campi restano identici a quelli degli attributi (senza `data-`), così il JS del frontend non cambia: il generatore scrive gli stessi `<li data-*>`.
