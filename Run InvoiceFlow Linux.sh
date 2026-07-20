#!/usr/bin/env bash
# InvoiceFlow launcher for Linux — serves app + Dropbox sync file (invoiceflow-data.json)
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP="$DIR/app"

# Support either Dropbox layout (script next to app/) or flat repo layout (script next to server.py)
if [[ -d "$APP" && -f "$APP/server.py" ]]; then
  :
elif [[ -f "$DIR/server.py" && -f "$DIR/index.html" ]]; then
  APP="$DIR"
else
  echo ""
  echo "  ERROR: Could not find InvoiceFlow app files."
  echo "  Looked for: $DIR/app/server.py"
  echo "  Wait for Dropbox to finish syncing, then try again."
  echo ""
  read -r -p "Press Enter to close..." _
  exit 1
fi

cd "$APP"

clear 2>/dev/null || true
echo ""
echo "  InvoiceFlow (Linux)"
echo "  =================="
echo "  Folder: $APP"
echo "  index.html: $( [[ -f index.html ]] && echo YES || echo MISSING )"
echo "  server.py:  $( [[ -f server.py ]] && echo YES || echo MISSING )"
echo ""

if [[ ! -f index.html ]]; then
  echo "  ERROR: index.html is missing."
  echo "  In Dropbox, make the app folder available offline, wait for sync, retry."
  echo ""
  read -r -p "Press Enter to close..." _
  exit 1
fi

if [[ ! -f server.py ]]; then
  echo "  ERROR: server.py is missing."
  echo ""
  read -r -p "Press Enter to close..." _
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "  ERROR: python3 not found."
  echo "  Install it, then try again:"
  echo "    Debian/Ubuntu:  sudo apt update && sudo apt install -y python3"
  echo "    Fedora:         sudo dnf install -y python3"
  echo "    Arch:           sudo pacman -S python"
  echo ""
  read -r -p "Press Enter to close..." _
  exit 1
fi

URL="http://127.0.0.1:8765/index.html"

open_browser() {
  # Prefer common Linux helpers; fall back quietly
  if command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$URL" >/dev/null 2>&1 || true
  elif command -v gio >/dev/null 2>&1; then
    gio open "$URL" >/dev/null 2>&1 || true
  elif command -v sensible-browser >/dev/null 2>&1; then
    sensible-browser "$URL" >/dev/null 2>&1 || true
  fi
}

echo "  Opening $URL"
echo "  Leave this terminal open while you work."
echo "  Press Ctrl+C when finished."
echo ""

# Open browser after the server has a moment to bind
(sleep 1 && open_browser) &

exec python3 server.py
