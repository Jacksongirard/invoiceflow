#!/bin/bash
cd "$(dirname "$0")"
echo ""
echo "  InvoiceFlow is starting..."
echo ""
echo "  Open this address in your browser:"
echo ""
echo "      http://127.0.0.1:8765"
echo ""
echo "  (Leave this window open while you use the app)"
echo "  Press Ctrl+C when finished."
echo ""
python3 -m http.server 8765
