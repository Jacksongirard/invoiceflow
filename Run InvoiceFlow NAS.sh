#!/usr/bin/env bash
# InvoiceFlow on a NAS or any always-on Linux box.
# Listens on the LAN so phones/PCs can open http://NAS-IP:8765
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP="$DIR/app"

if [[ -d "$APP" && -f "$APP/server.py" ]]; then
  :
elif [[ -f "$DIR/server.py" && -f "$DIR/index.html" ]]; then
  APP="$DIR"
else
  echo ""
  echo "  ERROR: Could not find InvoiceFlow app files."
  echo "  Copy the whole InvoiceFlow folder onto the NAS, then run this script again."
  echo ""
  read -r -p "Press Enter to close..." _
  exit 1
fi

cd "$APP"

echo ""
echo "  InvoiceFlow (NAS / LAN)"
echo "  ======================="
echo "  Folder: $APP"
echo ""

if [[ ! -f index.html || ! -f server.py ]]; then
  echo "  ERROR: index.html or server.py is missing."
  echo ""
  read -r -p "Press Enter to close..." _
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "  ERROR: python3 not found on this NAS."
  echo "  Install Python 3, or use Docker instead (see docs/NAS.md)."
  echo ""
  read -r -p "Press Enter to close..." _
  exit 1
fi

echo "  Starting on all network interfaces (port 8765)."
echo "  Leave this running. Press Ctrl+C to stop."
echo ""

exec python3 server.py --lan
