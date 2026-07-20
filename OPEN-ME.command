#!/bin/bash
cd "$(dirname "$0")"
clear
echo ""
echo "  InvoiceFlow — Dropbox file storage"
echo "  =================================="
echo ""
echo "  Data is saved to data.json in this folder"
echo "  (Dropbox will sync it to the cloud)."
echo ""
echo "  Opening http://127.0.0.1:8765 ..."
echo "  Leave this window open while you work."
echo "  Press Ctrl+C when finished."
echo ""

# Open browser shortly after server can accept connections
(sleep 0.8 && open "http://127.0.0.1:8765") &

exec python3 server.py
