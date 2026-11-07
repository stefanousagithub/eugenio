# Contenuti gestiti dal viaggiatore: Pages CMS + build Python

Verificato su pagescms.org a novembre 2026. Pages CMS modifica direttamente i file del repository GitHub (nessun database per i contenuti); la versione ospitata è gratuita e i collaboratori si invitano via email, senza account GitHub.

## Struttura del repository

```
contenuti/profilo.json      # un oggetto: nome, bio, foto principale, contatti, SEO
contenuti/viaggi.json       # lista di viaggi fatti
contenuti/partenze.json     # lista di partenze future
foto/caricate/              # originali caricati dal CMS
modello/                    # testa.html, stile.css, corpo.html, script.js con segnaposto {{...}}
build.py                    # valida, elabora le foto, genera dist/
strumenti/prepara_foto.py   # dalla skill sito-viaggiatore-contenuti
.pages.yml                  # campi del CMS, con descrizioni in italiano semplice
.github/workflows/pubblica.yml
```

## .pages.yml: scelte che contano

- Un `type: file` con `format: json` per il profilo e due `type: file` con `list: true` per viaggi e partenze: la barra laterale del CMS mostra tre voci chiare.
- `media.input: foto/caricate`, `output: /foto/caricate`, `rename: safe`: il CMS scrive nel JSON percorsi come `/foto/caricate/islanda.jpg`, che `build.py` risolve.
- Ogni campo ha `label` e `description` scritte per chi non è tecnico (cosa compare dove, formato atteso, cosa succede se resta vuoto).
- `operations: { delete: false }` sul profilo, per non cancellarlo per sbaglio.

## build.py: regole

- **Valida e si ferma** con messaggi in italiano («Viaggio 2 (Jamaica): il colore «rosso» non è valido (formato #RRGGBB)»): il sito online resta quello precedente finché l'errore non è corretto.
- **Normalizza i tipi**: il CMS può salvare numeri come testo (es. il mese da un `select`), quindi `int()` su anno e mese prima di ordinare.
- **Elabora le foto** con `prepara_foto.py`: due tagli WebP+JPEG, niente EXIF, colore del viaggio se non indicato.
- **Partenze concluse** diventano viaggi fatti in automatico; il cron giornaliero della Action le sposta anche senza modifiche.
- **Dati esterni facoltativi** (es. iscritti dall'API pubblica del tour operator): letti a build time con timeout e `try`; se falliscono la build prosegue con un warning.
- Genera `robots.txt` (Disallow finché `online_su_google` è spento) e, con l'indirizzo del sito, `og:image` assoluta e `sitemap.xml`.

## Insidie

- Repository pubblico (GitHub Pages gratis): gli originali in `foto/caricate/` restano scaricabili con il GPS, anche se il sito pubblica solo le versioni pulite. Alternative: repo privato con build e deploy su Cloudflare Pages (`wrangler pages deploy dist`), oppure chiedere foto già esportate senza posizione.
- `og:image` relativa non funziona nelle anteprime di WhatsApp: serve l'indirizzo assoluto del sito.
- Il cron di GitHub Actions può ritardare di qualche minuto e si disattiva dopo 60 giorni senza attività sul repository: un salvataggio dal CMS lo riattiva.
