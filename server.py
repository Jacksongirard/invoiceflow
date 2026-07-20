#!/usr/bin/env python3
"""InvoiceFlow local server — serves the app and saves data to data.json (Dropbox-safe)."""

from __future__ import annotations

import json
import os
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

HOST = "127.0.0.1"
PORT = 8765
ROOT = Path(__file__).resolve().parent
DATA_FILE = ROOT / "data.json"


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, fmt, *args):
        sys.stderr.write("[%s] %s\n" % (self.log_date_time_string(), fmt % args))

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, PUT, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-store")

    def _send_json(self, code: int, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self._cors()
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/data":
            if DATA_FILE.exists():
                try:
                    raw = DATA_FILE.read_text(encoding="utf-8")
                    data = json.loads(raw) if raw.strip() else {}
                except Exception as e:
                    self._send_json(500, {"error": str(e)})
                    return
                self._send_json(200, {"ok": True, "data": data, "path": str(DATA_FILE)})
            else:
                self._send_json(200, {"ok": True, "data": None, "path": str(DATA_FILE)})
            return
        if path == "/api/status":
            self._send_json(
                200,
                {
                    "ok": True,
                    "mode": "file",
                    "dataFile": str(DATA_FILE),
                    "exists": DATA_FILE.exists(),
                },
            )
            return
        return super().do_GET()

    def do_PUT(self):
        path = urlparse(self.path).path
        if path != "/api/data":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", "0") or 0)
        raw = self.rfile.read(length)
        try:
            payload = json.loads(raw.decode("utf-8"))
            # Accept either full envelope or bare data object
            data = payload.get("data", payload)
            if not isinstance(data, dict):
                raise ValueError("payload must be a JSON object")
            # Atomic-ish write for Dropbox
            tmp = DATA_FILE.with_suffix(".json.tmp")
            tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            os.replace(tmp, DATA_FILE)
            self._send_json(200, {"ok": True, "path": str(DATA_FILE)})
        except Exception as e:
            self._send_json(400, {"ok": False, "error": str(e)})


def main():
    os.chdir(ROOT)
    # Seed empty file so Dropbox tracks it
    if not DATA_FILE.exists():
        DATA_FILE.write_text("{}\n", encoding="utf-8")

    try:
        httpd = ThreadingHTTPServer((HOST, PORT), Handler)
    except OSError as e:
        print(f"\n  Could not start on {HOST}:{PORT}: {e}")
        print("  Is InvoiceFlow already running? Close the other window and try again.\n")
        sys.exit(1)

    print()
    print("  InvoiceFlow is running with Dropbox file storage.")
    print()
    print("  Open this address in Chrome or Firefox:")
    print()
    print(f"      http://{HOST}:{PORT}")
    print()
    print(f"  Your data file (synced by Dropbox):")
    print(f"      {DATA_FILE}")
    print()
    print("  Leave this window open while you use the app.")
    print("  Press Ctrl+C when finished.")
    print()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n  Stopped.\n")
        httpd.server_close()


if __name__ == "__main__":
    main()
