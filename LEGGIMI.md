# Sito di Eugenio Lucarelli

Pagina personale statica: i contenuti stanno in tre file JSON in `contenuti/`, le foto in `foto/caricate/`. A ogni modifica una GitHub Action rigenera la pagina (`build.py`) e la pubblica su GitHub Pages in circa un minuto.

## Per Eugenio: come aggiornare il sito

1. Apri [app.pagescms.org](https://app.pagescms.org) ed entra con il link che ti arriva per email (non serve un account GitHub).
2. A sinistra trovi tre voci: **Profilo**, **Prossime partenze**, **Viaggi fatti**.
3. Modifica quello che vuoi e premi **Save**. Dopo circa un minuto il sito è aggiornato.

Cose utili da sapere:

- **Aggiungere un viaggio**: in *Viaggi fatti* premi «Add an entry», compila titolo, anno, mese e carica una foto in cui ci sei tu. L'ordine sulla pagina è automatico, dal più vecchio.
- **Foto**: puoi caricarle così come escono dal telefono. Il sito le ridimensiona e toglie i dati GPS da quelle pubblicate. Se il soggetto viene tagliato, cambia «Inquadratura» (0 lato sinistro, 50 centro, 100 lato destro).
- **Prossime partenze**: con il codice di Avventure (le 4 cifre, es. 3597) iscritti e posti si aggiornano da soli ogni mattina. Quando il viaggio finisce, la partenza passa da sola tra i viaggi fatti: poi puoi aggiungerle la foto.
- **«Adesso sono in viaggio»**: compare solo se lo attivi nella partenza, e solo nei giorni del viaggio.
- **Frase sul viaggio**: è facoltativa e compare in corsivo. Se non hai una frase tua, lasciala vuota.
- Se salvi qualcosa di sbagliato (una data o un colore non validi), il sito online non cambia e nella scheda Actions su GitHub trovi scritto in italiano cosa correggere.

## Per Stefano: messa online (una volta sola)

1. Crea un repository su GitHub con questi file (`dist/` non va caricata, è nel `.gitignore`).
2. Settings → Pages → Source: **GitHub Actions**. Il primo push pubblica il sito su `utente.github.io/repo`.
3. Dominio personalizzato (facoltativo): file `CNAME` nella radice con il dominio, poi i record DNS indicati da GitHub e «Enforce HTTPS». Aggiorna anche «Indirizzo del sito» nel Profilo, serve all'anteprima dei link su WhatsApp.
4. Pages CMS: entra su app.pagescms.org con GitHub, installa la GitHub App sul repository, apri il repository e da **Collaborators** invita l'email di Eugenio.
5. Al lancio: nel Profilo attiva «Visibile su Google».

Sviluppo in locale:

```bash
pip install -r requirements.txt
python build.py --offline        # senza leggere gli iscritti dal sito di Avventure
python -m http.server -d dist    # http://localhost:8000
```

Struttura:

| Percorso | Contenuto |
|---|---|
| `contenuti/*.json` | Profilo, viaggi fatti, prossime partenze (li modifica il CMS) |
| `foto/caricate/` | Originali caricati dal CMS |
| `modello/` | HTML, CSS e JS della pagina, con i segnaposto `{{...}}` |
| `build.py` | Validazione, elaborazione foto, iscritti da Avventure, generazione di `dist/` |
| `strumenti/prepara_foto.py` | Ridimensionamento, rimozione EXIF/GPS, colore del viaggio |
| `.pages.yml` | Campi e testi d'aiuto del CMS |
| `.github/workflows/pubblica.yml` | Build e pubblicazione: a ogni push e ogni mattina alle 5:17 UTC |

Nota sulla privacy: con un repository pubblico (necessario per GitHub Pages gratis) gli originali in `foto/caricate/` sono scaricabili con i loro metadati, anche se il sito pubblica solo le versioni ripulite. Se Eugenio carica foto con il GPS attivo, conviene un repository privato con pubblicazione su Cloudflare Pages (vedi la skill `sito-statico-deploy`).
