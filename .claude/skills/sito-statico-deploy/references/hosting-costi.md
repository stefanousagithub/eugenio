# Hosting e costi (verificati a novembre 2026)

I limiti dei piani gratuiti cambiano spesso. Prima di dare un numero all'utente come definitivo, ricontrolla la pagina ufficiale indicata.

| Provider | Piano gratuito | Limiti rilevanti | Note per questo sito | Fonte da ricontrollare |
|---|---|---|---|---|
| GitHub Pages | Sì | sito pubblicato fino a 1 GB, ~100 GB/mese di traffico (limite morbido), ~10 build/ora (limite morbido, non vale per workflow Actions personalizzati) | Nel piano Free il repo deve essere pubblico. Usato dal riferimento. | docs.github.com → Pages → Limits |
| Cloudflare Pages | Sì | traffico statico illimitato, 500 build/mese, 1 build alla volta, 20.000 file per sito, 25 MiB per file, 100 domini per progetto | Repo anche privato; Web Analytics gratis; Workers gratis fino a 100.000 richieste/giorno | developers.cloudflare.com/pages/platform/limits |
| Netlify | Sì | sistema a crediti mensili (300 crediti nel Free) invece di quote separate | Va bene ma meno prevedibile | netlify.com/pricing |
| Vercel Hobby | Sì | ~100 GB/mese di banda | Solo uso personale non commerciale | vercel.com/pricing e termini Hobby |

## Dominio

| Estensione | Costo indicativo annuo | Note |
|---|---|---|
| .it | € 10–16 da registrar italiani | Offerte del primo anno (anche € 5–6) che al rinnovo tornano a prezzo pieno: guarda sempre il prezzo di rinnovo. |
| .com | ~$10 su Cloudflare Registrar (prezzo all'ingrosso, senza ricarico, rinnovo allo stesso prezzo) | Privacy WHOIS inclusa. |

## Costo totale

| Scenario | Costo |
|---|---|
| Sito su sottodominio gratuito (utente.github.io, progetto.pages.dev) | € 0 |
| Sito con dominio personalizzato | € 10–16/anno |
| Con modulo contatti su Cloudflare Workers (entro il piano gratuito) | invariato |

Un server (VPS, hosting condiviso) non serve: avrebbe senso solo con un backend vero (login, database, pagamenti), che questo sito non ha.
