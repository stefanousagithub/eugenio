#!/usr/bin/env bash
# Controlli prima del deploy di un sito statico.
# Uso: bash controlla.sh [cartella-del-sito]   (default: cartella corrente)
# Controlla: meta essenziali, file locali referenziati ma mancanti, pesi di HTML e immagini, file da non pubblicare.
set -u
SITO="${1:-.}"
cd "$SITO" || exit 1
ERR=0
avviso() { echo "  ATTENZIONE: $*"; ERR=1; }

echo "== Meta in index.html"
if [ ! -f index.html ]; then echo "  index.html non trovato"; exit 1; fi
for m in '<title>' 'name="description"' 'name="viewport"' 'property="og:title"' 'property="og:image"' 'property="og:description"' 'lang="'; do
  grep -q "$m" index.html || avviso "manca $m"
done
grep -q 'name="robots" content="noindex"' index.html && avviso "noindex presente: toglilo al lancio"

echo "== File locali referenziati"
{
  grep -ohE '(src|href)="[^"#?]+' ./*.html | sed -E 's/^(src|href)="//'
  grep -ohE 'srcset="[^"]+' ./*.html | sed -E 's/^srcset="//' | tr ',' '\n' | awk '{print $1}'
} | grep -vE '^(https?:|mailto:|tel:|data:|//|$)' | grep -vF '${' | grep -v '%3C' | sort -u | while read -r f; do
    f="${f#/}"; [ -z "$f" ] && continue
    [ -e "$f" ] || [ -e "$f/index.html" ] || echo "  MANCANTE: $f"
  done

echo "== Pesi"
for f in ./*.html; do
  kb=$(( $(gzip -c "$f" | wc -c) / 1024 ))
  echo "  $f: ${kb} KB compresso"; [ "$kb" -gt 100 ] && avviso "$f supera 100 KB compresso"
done
if [ -d foto ]; then
  find foto -maxdepth 1 -type f \( -name '*.jpg' -o -name '*.webp' \) -size +250k -printf "  GRANDE: %p %k KB\n"
  [ -d foto/mini ] && find foto/mini -type f -size +40k -printf "  MINI PESANTE: %p %k KB\n"
fi

echo "== File da non pubblicare"
find . -path ./.git -prune -o -type f \( -iname '*.heic' -o -iname '*.raw' -o -iname '*.psd' -o -name '.env' -o -name '.DS_Store' \) -print | sed 's/^/  /'
find . -path ./.git -prune -o -type f -size +5M -print | sed 's/^/  OLTRE 5 MB: /'

[ "$ERR" -eq 0 ] && echo "Nessun problema bloccante." || echo "Rivedi gli avvisi sopra."
