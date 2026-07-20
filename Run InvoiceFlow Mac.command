#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
APP="$DIR/app"
cd "$APP" || {
  echo "ERROR: app folder not found at: $APP"
  echo "Wait for Dropbox to finish syncing."
  read -r _
  exit 1
}

clear
echo ""
echo "  InvoiceFlow"
echo "  ==========="
echo "  Folder: $APP"
echo "  index.html: $( [[ -f index.html ]] && echo YES || echo MISSING )"
echo ""

if [[ ! -f index.html ]]; then
  echo "ERROR: index.html missing. Wait for Dropbox sync / Make available offline."
  read -r _
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: python3 not found."
  read -r _
  exit 1
fi

echo "  Opening http://127.0.0.1:8765/index.html"
echo "  Leave this window open. Press Ctrl+C when finished."
echo ""

(sleep 1 && open "http://127.0.0.1:8765/index.html") &
exec python3 server.py
