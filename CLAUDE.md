# Sito di Eugenio Lucarelli: istruzioni per Claude Code

Questo file riassume il lavoro fatto in chat e dice cosa fare adesso, in che ordine. Leggilo tutto prima di toccare il repository.

## 1. Contesto

- **Cosa**: pagina personale statica di Eugenio Lucarelli (Roma, classe ’97), assistente di volo e tour leader con Avventure nel Mondo. Mostra i viaggi fatti, la prossima partenza, i contatti.
- **Chi**: lo sviluppa Stefano; i contenuti li aggiornerà Eugenio da solo, con Pages CMS, senza toccare codice.
- **Riferimento visivo**: manfreditocci.it/avventure (sorgente pubblico su github.com/Manfr3d1/avventure). Ci ispiriamo al sistema (linguaggio iOS, una sola interazione forte), non lo copiamo.
- **Repository GitHub**: `OWNER/Eugenio` sull'account di Stefano. **Sostituisci `OWNER`** con il nome utente GitHub reale (chiedilo a Stefano o ricavalo da `gh api user -q .login`).

## 2. Cosa è stato fatto

1. Analisi del sito di riferimento dal sorgente: token iOS, linea del tempo trascinabile con time-lapse, tabellone a palette, colore del viaggio estratto dalla foto, GitHub Pages + Action giornaliera per gli iscritti.
2. Tre skill scritte per questo tipo di sito, incluse in `.claude/skills/`:
   - `sito-viaggiatore-design`: direzione visiva, processo (piano → revisione anti-generico → build → screenshot), interazioni;
   - `sito-viaggiatore-contenuti`: schema dati, regole dei testi, `prepara_foto.py`;
   - `sito-statico-deploy`: hosting a costo zero, dominio, CMS, workflow.
3. Concept "testa tra le nuvole", dalla frase di Eugenio *«Piedi a terra e testa tra le nuvole, tra un sogno e un’incudine»*:
   - hero "ritratto nel tempo" con linea del tempo;
   - carta d'imbarco con mappa dei posti per la prossima partenza (al posto del tabellone di Manfredi);
   - accento systemCyan `#64d2ff`;
   - motti in serif corsivo di sistema;
   - su desktop, hero fisso a sinistra e contenuto a destra.
4. Contenuti raccolti dal suo Instagram: 9 viaggi datati e la prossima partenza reale, Finlandia Aurore Boreali Discovery, cod. 3597, 13–20 dicembre 2026.
5. Il progetto è stato ristrutturato per il CMS:
   - contenuti in JSON;
   - `build.py` che valida, elabora le foto (ridimensionamento, rimozione GPS, colore) e legge gli iscritti dall'API pubblica di Avventure;
   - GitHub Action che pubblica a ogni push e ogni mattina.
6. Rifiniture dalle skill apple-design ed emil-design-eng e dall'audit con le Web Interface Guidelines di Vercel:
   - swipe con rubber band e proiezione del momento;
   - transizione direzionale;
   - tessere che aprono il viaggio sulla linea del tempo (`#slug` condivisibile);
   - skip link, hover solo con mouse, `scroll-padding-bottom`.
7. Testato in locale: build ok, nessun errore JS, screenshot a 390/820/1440 px in tema chiaro e scuro.

## 3. Decisioni prese (non cambiarle senza chiedere)

| Tema | Decisione |
|---|---|
| Hosting | GitHub Pages, repository **pubblico** (gratis). Cloudflare Pages solo se in futuro serve il repo privato |
| Indirizzo | Per ora `https://OWNER.github.io/Eugenio/`. Il dominio arriverà dopo (vedi fase F) |
| Dominio | `.it` da registrar italiano (Aruba, Register.it, OVHcloud), intestato a Eugenio, circa € 10–16/anno. Cloudflare non vende `.it` |
| CMS | Pages CMS ospitato (app.pagescms.org), Eugenio invitato come collaboratore via email |
| Lavoro | Scrivere sempre "assistente di volo", mai il nome della compagnia aerea |
| "Adesso sono in viaggio" | Solo se attivato nella singola partenza (`mostra_in_viaggio`). Lo decide Eugenio |
| Tour leader | Marrakech Discovery 2025 e Lofoten Discovery 2024 (la Norvegia è **da confermare**) |
| Enoturismo | Nessuna sezione: non risulta dai dati di Eugenio |
| Testi e foto | Li definirà Eugenio dal CMS. **Non inventare** frasi personali, numeri, iscritti |

## 4. Struttura del progetto

| Percorso | Ruolo |
|---|---|
| `contenuti/profilo.json`, `viaggi.json`, `partenze.json` | Contenuti (li modifica il CMS) |
| `foto/caricate/` | Originali caricati dal CMS |
| `modello/testa.html`, `stile.css`, `corpo.html`, `script.js` | Pagina con segnaposto `{{...}}` |
| `build.py` | Genera `dist/`. `--offline` evita la chiamata ad Avventure |
| `strumenti/prepara_foto.py` | Foto: due tagli WebP+JPEG, niente EXIF, colore del viaggio |
| `.pages.yml` | Campi del CMS con descrizioni in italiano |
| `.github/workflows/pubblica.yml` | Build e deploy su Pages: a ogni push su `main`, ogni giorno alle 5:17 UTC, a mano |
| `.claude/skills/` | Le tre skill del progetto |
| `LEGGIMI.md` | Guida per Eugenio e per Stefano |

`dist/` è generata e sta nel `.gitignore`: non va mai committata né modificata a mano.

## 5. Procedura, in ordine

### Fase A: verifica locale

```bash
python3 -m pip install -r requirements.txt
python3 build.py --offline          # deve stampare "Sito generato in dist/: N viaggi di gruppo, N miei, N partenze future."
python3 -m http.server -d dist 8000 # controlla http://localhost:8000
```

Facoltativo, per il QA visivo: `pip install playwright && playwright install chromium`, poi `python3 .claude/skills/sito-viaggiatore-design/scripts/screenshot.py dist/index.html --out shots/`.

### Fase B: impostare l'indirizzo del sito

In `contenuti/profilo.json` imposta `"indirizzo_sito": "https://OWNER.github.io/Eugenio"` (senza barra finale), con OWNER reale. Serve per l'`og:image` assoluta, cioè per l'anteprima del link su WhatsApp. Lascia `"online_su_google": false`.

### Fase C: attivare GitHub Pages con sorgente "GitHub Actions"

Va fatto **prima** del primo push, altrimenti il primo deploy fallisce. Due modi:

- a mano (Stefano): repository → Settings → Pages → Build and deployment → Source: **GitHub Actions**;
- con `gh` autenticato:
  ```bash
  gh api -X POST repos/OWNER/Eugenio/pages -f build_type=workflow
  # se Pages esiste già: gh api -X PUT repos/OWNER/Eugenio/pages -f build_type=workflow
  ```

### Fase D: primo push

```bash
git init -b main
git add .
git status   # controlla: deve esserci .github/ e .pages.yml, NON dist/
git commit -m "Prima versione del sito di Eugenio"
git remote add origin https://github.com/OWNER/Eugenio.git
git ls-remote origin   # se il repo remoto ha già commit (es. README creato da GitHub):
#   git pull --rebase origin main   e risolvi eventuali conflitti
git push -u origin main
```

### Fase E: verificare la pubblicazione

```bash
gh run list --workflow pubblica.yml --limit 1
gh run watch          # attende la fine
gh api repos/OWNER/Eugenio/pages -q .html_url
```

Atteso: run verde e sito su `https://OWNER.github.io/Eugenio/`. Il warning "sito di Avventure non raggiungibile" non blocca nulla. Se la build fallisce per contenuti non validi, il messaggio è in italiano e dice cosa correggere.

Controlla il sito pubblicato su telefono e desktop:
- foto e linea del tempo;
- carta d'imbarco con i link "Iscriviti" e "Scheda del viaggio";
- se l'API di Avventure ha risposto dal runner, la mappa dei posti.

### Fase F: Pages CMS per Eugenio (manuale, Stefano)

1. app.pagescms.org → Sign in with GitHub → installa la GitHub App sul repository `Eugenio`.
2. Apri il repository nel CMS e verifica che compaiano Profilo, Prossime partenze, Viaggi fatti.
3. Collaborators → invita l'email di Eugenio.
4. Prova: modifica un testo dal CMS, salva, verifica che parta la Action e che il sito si aggiorni.

### Fase G (dopo): dominio personalizzato

1. Eugenio compra `eugeniolucarelli.it` (solo dominio, niente hosting) da un registrar italiano. Verificare prima la disponibilità e il prezzo di rinnovo.
2. GitHub, impostazioni dell'account → Pages → verifica il dominio con il record TXT indicato (evita takeover).
3. Repository → Settings → Pages → Custom domain: `eugeniolucarelli.it` → Save.
4. DNS dal registrar:
   - `A @` → 185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153;
   - `CNAME www` → `OWNER.github.io`.
5. Attendi la propagazione (fino a 24 h), poi **Enforce HTTPS**.
6. `profilo.json`: `indirizzo_sito` → `https://eugeniolucarelli.it`.

Con il deploy via Actions il file `CNAME` non serve.

### Fase H: lancio

`profilo.json` → `"online_su_google": true`. La build rimuove il `noindex`, apre `robots.txt` e genera `sitemap.xml`.

## 6. Regole di lavoro

- Prima di ogni commit: `python3 build.py --offline` deve passare.
- I contenuti si cambiano nei JSON, il codice in `modello/` e `build.py`. Mai in `dist/`.
- Per modifiche di design segui `.claude/skills/sito-viaggiatore-design/SKILL.md`: guarda gli screenshot prima di dire che è fatto.
- Testi del sito: prima persona, concreti, niente slogan da agenzia (regole in `sito-viaggiatore-contenuti`).
- Messaggi di commit in italiano, brevi.
- Non committare segreti né foto con dati sensibili. Il repository è pubblico: gli originali in `foto/caricate/` sono scaricabili.

## 7. Aperti

| Cosa | Chi |
|---|---|
| Foto originali per ogni viaggio (meglio dal telefono, una per viaggio con lui) | Eugenio, dal CMS |
| Anni dei viaggi senza data: Praga, Chefchaouen–Tangeri, Andalucía, Cipro, Grecia, Creta, Balcani, Georgia, Italia | Eugenio |
| Conferma del viaggio in Norvegia da tour leader | Eugenio |
| Numero WhatsApp: se inserito, il pulsante principale diventa WhatsApp | Eugenio |
| Approvazione della bio (oggi è una bozza fatta solo di fatti dal suo profilo) | Eugenio |
| Dominio | Eugenio e Stefano, fase G |
