#!/usr/bin/env python3
"""InvoiceFlow server — serves the app and saves data to invoiceflow-data.json.

Desktop launchers bind to 127.0.0.1 (this computer only).
NAS / LAN mode:  python3 server.py --lan
"""

from __future__ import annotations

import argparse
import json
import os
import socket
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, unquote

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765
ROOT = Path(__file__).resolve().parent
SYNC_FILE = ROOT / "invoiceflow-data.json"
LEGACY_DATA_FILE = ROOT / "data.json"
INDEX_FILE = ROOT / "index.html"

HOST = DEFAULT_HOST
PORT = DEFAULT_PORT
DATA_FILE = SYNC_FILE
LAN_MODE = False


def env_str(name: str, default: str = "") -> str:
    val = os.environ.get(name)
    if val is None:
        return default
    return val.strip()


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="InvoiceFlow app + data-file server")
    parser.add_argument(
        "--host",
        default=env_str("INVOICEFLOW_HOST", DEFAULT_HOST) or DEFAULT_HOST,
        help="Listen address (default 127.0.0.1; use 0.0.0.0 for NAS/LAN)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(env_str("INVOICEFLOW_PORT", str(DEFAULT_PORT)) or DEFAULT_PORT),
        help="Listen port (default 8765)",
    )
    parser.add_argument(
        "--lan",
        action="store_true",
        help="Listen on all interfaces so phones/PCs on your network can open the app",
    )
    parser.add_argument(
        "--data",
        default=env_str("INVOICEFLOW_DATA"),
        help="Path to invoiceflow-data.json (default: next to this script)",
    )
    return parser.parse_args(argv)


def guess_lan_ip() -> str | None:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("1.1.1.1", 80))
        ip = sock.getsockname()[0]
        sock.close()
        if ip and not ip.startswith("127."):
            return ip
    except Exception:
        pass
    try:
        ip = socket.gethostbyname(socket.gethostname())
        if ip and not ip.startswith("127."):
            return ip
    except Exception:
        pass
    return None


def resolve_data_file(explicit: str | None = None) -> Path:
    """Use invoiceflow-data.json when present (or always prefer it for new writes)."""
    if explicit:
        path = Path(explicit).expanduser()
        if not path.is_absolute():
            path = (ROOT / path).resolve()
        else:
            path = path.resolve()
        return path
    if SYNC_FILE.exists():
        return SYNC_FILE
    if LEGACY_DATA_FILE.exists() and not SYNC_FILE.exists():
        # Migrate legacy data.json → invoiceflow-data.json once
        try:
            raw = LEGACY_DATA_FILE.read_text(encoding="utf-8-sig").strip()
            if raw and raw != "{}":
                SYNC_FILE.write_text(LEGACY_DATA_FILE.read_text(encoding="utf-8-sig"), encoding="utf-8")
                return SYNC_FILE
        except Exception:
            pass
        return LEGACY_DATA_FILE
    return SYNC_FILE


def is_lan_bind(host: str) -> bool:
    return host not in ("127.0.0.1", "localhost", "::1")


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
            "<p>Wait for the folder to finish copying or syncing, then restart "
            "InvoiceFlow (Docker, <strong>Run InvoiceFlow NAS</strong>, or "
            "<strong>Run InvoiceFlow PC/Mac/Linux</strong>).</p>"
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
                    "lan": LAN_MODE or is_lan_bind(HOST),
                    "bind": HOST,
                    "port": PORT,
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
            DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
            tmp = DATA_FILE.with_suffix(DATA_FILE.suffix + ".tmp")
            tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            os.replace(tmp, DATA_FILE)
            self._send_json(200, {"ok": True, "path": str(DATA_FILE)})
        except Exception as e:
            self._send_json(400, {"ok": False, "error": str(e)})


def main(argv=None):
    args = parse_args(argv)

    os.chdir(ROOT)
    try:
        sys.stdout.reconfigure(line_buffering=True)
        sys.stderr.reconfigure(line_buffering=True)
    except Exception:
        pass

    print()
    print("  InvoiceFlow server")
    print("  ==================")
    global DATA_FILE, HOST, PORT, LAN_MODE
    HOST = "0.0.0.0" if args.lan else args.host
    PORT = args.port
    LAN_MODE = args.lan or is_lan_bind(HOST)
    DATA_FILE = resolve_data_file(args.data or None)

    print(f"  Folder: {ROOT}")
    print(f"  index.html present: {INDEX_FILE.exists()}")
    print(f"  Sync file: {DATA_FILE}")
    print(f"  Bind: {HOST}:{PORT}")
    print()

    if not INDEX_FILE.exists():
        print("  ERROR: index.html is missing from the app folder.")
        print("  Finish copying or syncing the InvoiceFlow folder, then try again.")
        print()
        sys.exit(1)

    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        DATA_FILE.write_text("{}\n", encoding="utf-8")

    try:
        httpd = ThreadingHTTPServer((HOST, PORT), Handler)
    except OSError as e:
        print(f"  Could not start on {HOST}:{PORT}: {e}")
        print("  Close any other InvoiceFlow window, or pick another port:")
        print(f"    python3 server.py --lan --port {PORT + 1}")
        print()
        sys.exit(1)

    print(f"  This computer: http://127.0.0.1:{PORT}/index.html")
    if LAN_MODE:
        lan_ip = guess_lan_ip()
        if lan_ip:
            print(f"  Other devices:  http://{lan_ip}:{PORT}/index.html")
        else:
            print(f"  Other devices:  http://YOUR-NAS-OR-PC-IP:{PORT}/index.html")
        print("  Keep this on your home/office LAN. Do not port-forward it to the internet.")
        print("  Use one device at a time; last save wins.")
    print("  Leave this window open. Press Ctrl+C when finished.")
    print()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n  Stopped.\n")
        httpd.server_close()


if __name__ == "__main__":
    main()
