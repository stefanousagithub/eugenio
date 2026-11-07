---
name: sito-statico-deploy
description: Struttura, build e pubblicazione a costo (quasi) zero del sito personale del viaggiatore come sito statico (scelta tra HTML senza build e generatore statico, GitHub Pages o Cloudflare Pages, dominio personalizzato, HTTPS, SEO e anteprime social, analytics senza cookie, dati aggiornati in automatico con GitHub Actions). Da usare ogni volta che si parla di dove mettere online il sito, quanto costa, dominio, deploy, struttura del repository, performance o aggiornamenti automatici, anche se l'utente chiede solo "come lo pubblico?" o "mi serve un server?".
---

# Sito statico: struttura, build e pubblicazione

Il sito del viaggiatore è un **sito statico**: file HTML, CSS, JS e immagini serviti da una CDN. Non serve un server acceso, non serve un database, e quindi l'hosting può costare zero; l'unico costo fisso è il dominio. Questa è la stessa architettura del riferimento (manfreditocci.it, su GitHub Pages).

Il dettaglio di piani e limiti dei provider, verificato a novembre 2026, è in `references/hosting-costi.md`. I limiti cambiano: prima di consigliare un piano a pagamento o di dare un numero preciso all'utente, ricontrolla la pagina ufficiale del provider.

## 1. Build: con o senza generatore?

| Criterio | A. HTML senza build | B. Generatore statico (Astro) |
|---|---|---|
| Pagine | 1–3 | Molte, o una per viaggio/diario |
| Elementi nelle liste | fino a ~40 | qualsiasi |
| Chi aggiorna | anche un non sviluppatore, copiando una riga | chi sa usare Git e un terminale, o un CMS |
| Lingue | una | più lingue |
| Strumenti | nessuno | Node, `npm run build` |
| Rischio | file unico che cresce | dipendenze da aggiornare |

Default: **A** per la prima versione, come il riferimento. Passa a **B** quando una delle colonne di B diventa vera (per esempio quando il viaggiatore vuole una pagina per ogni viaggio con il racconto). Astro perché produce HTML puro senza JS di default e accetta i dati da YAML/JSON con lo stesso schema di `sito-viaggiatore-contenuti`.

Struttura per A:

```
/
├── index.html          # pagina, CSS e JS inline
├── foto/               # tagli grandi (.webp + .jpg)
│   ├── mini/           # miniature
│   └── colori.json     # colori e dimensioni da prepara_foto.py
├── og.jpg              # anteprima social 1200x630
├── favicon.svg
├── robots.txt
├── sitemap.xml
├── CNAME               # solo GitHub Pages con dominio personalizzato
├── .nojekyll           # solo GitHub Pages
└── .github/workflows/  # facoltativo: aggiornamenti automatici
```

Le foto originali **non** vanno nel repository: restano sul computer del viaggiatore, nel repo vanno solo quelle elaborate da `prepara_foto.py`. Aggiungi la cartella degli originali al `.gitignore`.

## 2. Dove pubblicarlo

Due opzioni gratuite che vanno bene, più quelle da evitare per questo caso.

**GitHub Pages** (quella del riferimento). Repository pubblico, push sul ramo e il sito è online. Gratis con limiti morbidi (sito fino a 1 GB, ~100 GB di traffico al mese), largamente sufficienti per un sito personale. Contro: nel piano gratuito il repository deve essere pubblico, quindi tutto quello che c'è dentro è visibile a chiunque.

**Cloudflare Pages.** Collegato a un repo GitHub (anche privato) o caricato da riga di comando; traffico statico illimitato, 500 build al mese, dominio personalizzato e HTTPS gratis, analytics senza cookie gratuite, e Workers gratuiti (100.000 richieste al giorno) se un giorno serve una piccola funzione lato server (un modulo contatti, un endpoint). Contro: un account in più da gestire.

Scelta:

- Repo pubblico va bene e non servono funzioni → **GitHub Pages**.
- Vuoi il repo privato, le analytics, o prevedi un modulo contatti → **Cloudflare Pages**.

Da evitare qui: **Vercel Hobby** (il piano gratuito è limitato all'uso personale non commerciale: se il viaggiatore vende viaggi o promuove partenze a pagamento è una zona grigia), **Netlify Free** (va bene, ma funziona a crediti mensili ed è meno prevedibile), hosting condiviso tradizionale a pagamento (paghi un server che a un sito statico non serve).

## 3. Dominio

- Un `.it` costa indicativamente € 10–16 l'anno da un registrar italiano (attenzione ai prezzi promozionali del primo anno, che poi raddoppiano al rinnovo). Un `.com` registrato su Cloudflare Registrar costa il prezzo all'ingrosso, intorno ai $10 l'anno, rinnovo incluso allo stesso prezzo.
- Senza dominio il sito funziona comunque su `utente.github.io` o `progetto.pages.dev`: per una prima versione va benissimo.
- Configura il DNS seguendo la guida del provider (record CNAME per il `www`, record A/ALIAS o CNAME flattening per il dominio nudo), attiva HTTPS obbligatorio e verifica il dominio nel provider per evitare che altri lo "agganci".

Costo totale realistico: **€ 0** senza dominio, **€ 10–16 l'anno** con dominio.

## 4. Prima della pubblicazione

- `<title>`, `meta description`, Open Graph (`og:title`, `og:description`, `og:image` 1200×630, `og:locale` it_IT) e `twitter:card`: il sito sarà condiviso soprattutto su WhatsApp e Instagram, e senza anteprima il link sembra spam.
- Dati strutturati JSON-LD di tipo `Person` (nome, `sameAs` con i profili social).
- `robots.txt` e `sitemap.xml`. Se il sito non è pronto, `noindex` come fa il riferimento, e toglilo al lancio.
- `theme-color` per tema chiaro e scuro, favicon SVG inline o file leggero, `apple-touch-icon`.
- Analytics: Cloudflare Web Analytics o nessuna. Niente Google Analytics: richiede il banner dei cookie, che rovina il primo schermo su telefono.
- Verifica con `scripts/controlla.sh` (link rotti, pesi, meta mancanti) e con gli screenshot di `sito-viaggiatore-design`.

## 5. Pubblicare

**GitHub Pages**: Settings → Pages → Deploy from a branch → `main` / root. Con dominio: file `CNAME` contenente solo il dominio, poi DNS. Per il caso B (Astro) usa invece il workflow ufficiale di Pages con build; un modello è in `assets/deploy-github-pages.yml`.

**Cloudflare Pages**: Workers & Pages → Create → Pages → collega il repo; nessun comando di build per il caso A (output: `/`), `npm run build` e output `dist` per il caso B. Oppure da terminale: `npx wrangler pages deploy . --project-name=<nome>`. Header di cache e sicurezza in un file `_headers` (modello in `assets/_headers`).

## 6. Dati che si aggiornano da soli

Un sito statico può avere dati "vivi" senza server: una GitHub Action pianificata (cron) scarica i dati da una fonte pubblica, riscrive gli attributi nell'HTML e fa un commit; il commit fa ripartire il deploy. È quello che fa il riferimento con gli iscritti alle partenze, una volta al giorno. Modello in `assets/aggiorna-dati.yml`. Regole: solo fonti pubbliche e consentite, uno User-Agent che dica chi sei, frequenza bassa (una volta al giorno basta), nessun commit se non è cambiato niente.

## 7. Se il sito lo aggiorna il viaggiatore

Quando chi aggiorna non è uno sviluppatore, i contenuti escono dall'HTML e vanno in file JSON (`contenuti/profilo.json`, `viaggi.json`, `partenze.json`), modificati con **Pages CMS** (app.pagescms.org, gratuito, invito via email senza account GitHub). Uno script `build.py` li valida, elabora le foto caricate, genera l'HTML statico con gli stessi attributi `data-*` e una GitHub Action lo pubblica a ogni salvataggio e ogni mattina. La configurazione dei campi, il modello di build e le insidie (numeri salvati come testo, foto originali con GPS nel repo pubblico) sono in `references/cms-pages.md`.

## 8. Contenuti privati

Su un hosting statico pubblico non esistono cartelle segrete: un URL non indovinabile protegge solo finché qualcuno non lo condivide, e in un repo pubblico è comunque leggibile. Se servono pagine private (un diario, foto di gruppo), usa Cloudflare Pages con Cloudflare Access (gratuito per pochi utenti) oppure tienile fuori dal sito.

## File di questa skill

- `references/hosting-costi.md`: piani, limiti e costi dei provider con le fonti.
- `references/cms-pages.md`: gestione dei contenuti da parte del viaggiatore con Pages CMS e build Python.
- `assets/deploy-github-pages.yml`: workflow di build e deploy per Astro su GitHub Pages.
- `assets/aggiorna-dati.yml`: workflow cron per aggiornare i dati nell'HTML.
- `assets/_headers`: cache e sicurezza per Cloudflare Pages.
- `scripts/controlla.sh`: controlli prima del deploy.
