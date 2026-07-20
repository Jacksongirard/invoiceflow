#!/usr/bin/env python3
"""InvoiceFlow local server — serves the app and saves data to data.json (Dropbox-safe)."""

from __future__ import annotations

import json
import os
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, unquote

HOST = "127.0.0.1"
PORT = 8765
ROOT = Path(__file__).resolve().parent
DATA_FILE = ROOT / "data.json"
INDEX_FILE = ROOT / "index.html"


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

    def _send_html(self, code: int, html: str):
        body = html.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self._cors()
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, file_path: Path, content_type: str):
        data = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self._cors()
        self.end_headers()
        self.wfile.write(data)

    def list_directory(self, path):
        # Never show raw directory listings — they confuse users
        self._send_html(
            404,
            "<!doctype html><meta charset=utf-8><title>InvoiceFlow</title>"
            "<body style='font-family:sans-serif;max-width:36rem;margin:3rem auto;padding:0 1rem'>"
            "<h1>InvoiceFlow file missing</h1>"
            "<p>The app could not find <code>index.html</code>.</p>"
            f"<p>Looked in:<br><code>{ROOT}</code></p>"
            "<p>Wait for Dropbox to finish syncing the <code>app</code> folder "
            "(green checkmarks), then close this window and run "
            "<strong>Run InvoiceFlow PC/Mac</strong> again.</p>"
            "</body>",
        )
        return None

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        path = unquote(urlparse(self.path).path)

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
                    "root": str(ROOT),
                    "indexExists": INDEX_FILE.exists(),
                    "dataFile": str(DATA_FILE),
                    "exists": DATA_FILE.exists(),
                },
            )
            return

        # Always serve the app at / and /index.html
        if path in ("/", "", "/index.html", "/index.htm"):
            if not INDEX_FILE.exists():
                self.list_directory(str(ROOT))
                return
            self._send_file(INDEX_FILE, "text/html; charset=utf-8")
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
            data = payload.get("data", payload)
            if not isinstance(data, dict):
                raise ValueError("payload must be a JSON object")
            tmp = DATA_FILE.with_suffix(".json.tmp")
            tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            os.replace(tmp, DATA_FILE)
            self._send_json(200, {"ok": True, "path": str(DATA_FILE)})
        except Exception as e:
            self._send_json(400, {"ok": False, "error": str(e)})


def main():
    os.chdir(ROOT)

    print()
    print("  InvoiceFlow server")
    print("  ==================")
    print(f"  Folder: {ROOT}")
    print(f"  index.html present: {INDEX_FILE.exists()}")
    print(f"  data.json: {DATA_FILE}")
    print()

    if not INDEX_FILE.exists():
        print("  ERROR: index.html is missing from the app folder.")
        print("  Wait for Dropbox to finish downloading, then try again.")
        print()
        sys.exit(1)

    if not DATA_FILE.exists():
        DATA_FILE.write_text("{}\n", encoding="utf-8")

    try:
        httpd = ThreadingHTTPServer((HOST, PORT), Handler)
    except OSError as e:
        print(f"  Could not start on {HOST}:{PORT}: {e}")
        print("  Close any other InvoiceFlow window and try again.")
        print()
        sys.exit(1)

    print(f"  Open: http://{HOST}:{PORT}/index.html")
    print("  Leave this window open. Press Ctrl+C when finished.")
    print()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n  Stopped.\n")
        httpd.server_close()


if __name__ == "__main__":
    main()
