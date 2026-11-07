# QA visivo prima della consegna

Genera gli screenshot con `python scripts/screenshot.py <file-o-url> --out shots/` e guardali tutti. Ogni voce sotto si verifica sugli screenshot o nel browser, non a memoria.

## Telefono (390×844, scuro e chiaro)

- Nell'hero il volto o il soggetto della foto non finisce sotto il nome. Se succede, alza la foto (attributo di alzata) o cambia inquadratura.
- Il nome sta su una riga, o va a capo in un punto sensato.
- La barra fissa in basso non copre l'ultimo contenuto (padding inferiore della pagina ≥ altezza barra + safe area).
- Le tessere della griglia hanno didascalie leggibili anche su foto chiare (gradiente presente).
- Nessuno scroll orizzontale della pagina.
- Bersagli toccabili ≥ 44×44px.

## Tablet (820×1180)

- La colonna non si allarga oltre il previsto; nessun elemento "galleggia" in modo strano tra i due layout.

## Desktop (1440×900, scuro e chiaro)

- Layout scelto (A o B) applicato; in B l'hero resta fermo mentre il contenuto scorre e non viene tagliato in altezza.
- Hover presenti solo dove c'è un'azione, e non sono l'unico segnale.

## Temi e accessibilità

- Contrasto testo/sfondo ≥ 4.5:1 in entrambi i temi, incluso il testo sopra l'accento e sopra i colori dei viaggi.
- Accento leggibile nel tema chiaro (serve quasi sempre una variante più scura per il testo).
- Navigazione da tastiera: focus visibile, linea del tempo controllabile con le frecce.
- Con `prefers-reduced-motion: reduce` niente time-lapse e niente animazioni lunghe.
- Pagina leggibile con JavaScript disattivato (contenuti nell'HTML).

## Prestazioni

- HTML+CSS+JS iniziali sotto ~100 KB compressi; nessuna libreria caricata se non serve davvero.
- Foto hero ≤ ~250 KB, miniature ≤ ~40 KB, formati moderni con fallback (vedi `sito-viaggiatore-contenuti`).
- Nessun salto di layout visibile al caricamento (dimensioni delle immagini dichiarate).

## Identità

- Rileggi il piano di design: l'elemento memorabile è uno solo ed è legato a questo viaggiatore?
- Nessuno dei tell elencati in "Cosa non fare" nella SKILL.md.
- Hai tolto almeno una cosa rispetto alla prima versione?
