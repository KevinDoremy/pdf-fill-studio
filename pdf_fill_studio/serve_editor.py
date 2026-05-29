"""Local loopback HTTP server for the editor, plus the export->bake glue.

Binds to 127.0.0.1 on an ephemeral port and shuts down after the export POST
(or a timeout), so it is reachable only from this machine and only briefly.
"""
import json
import os
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pdf_fill_studio.bake_overlay import bake_overlay

EDITOR_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "editor")


def handle_export(job, posted, out_path):
    """Merge posted final coordinates into the job and bake."""
    by_id = {f["id"]: f for f in posted.get("fields", [])}
    merged = dict(job)
    merged["fields"] = [by_id.get(f["id"], f) for f in job["fields"]] if job["fields"] else posted["fields"]
    return bake_overlay(merged, out_path)


def serve(job, out_path, open_browser=True):
    """Serve the editor; bake on export POST; shut down afterwards. Returns out_path."""
    done = threading.Event()

    class Handler(BaseHTTPRequestHandler):
        def _send(self, code, body=b"", ctype="text/plain"):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            if body:
                self.wfile.write(body)

        def log_message(self, *a):
            pass

        def do_GET(self):
            path = self.path.split("?")[0]
            if path in ("/", "/index.html"):
                return self._serve_file(os.path.join(EDITOR_DIR, "index.html"), "text/html")
            if path == "/job.json":
                return self._send(200, json.dumps(job).encode("utf-8"), "application/json")
            if path == "/input.pdf":
                return self._serve_file(job["pdf"], "application/pdf")
            if path.startswith("/vendor/") or path in ("/editor.js", "/coords.js"):
                rel = path.lstrip("/")
                return self._serve_file(os.path.join(EDITOR_DIR, rel), self._ctype(rel))
            return self._send(404)

        def do_POST(self):
            if self.path.split("?")[0] != "/export":
                return self._send(404)
            length = int(self.headers.get("Content-Length", 0))
            posted = json.loads(self.rfile.read(length) or b"{}")
            handle_export(job, posted, out_path)
            self._send(200, b"ok")
            done.set()

        def _serve_file(self, fpath, ctype):
            if not os.path.exists(fpath):
                return self._send(404)
            with open(fpath, "rb") as fh:
                self._send(200, fh.read(), ctype)

        @staticmethod
        def _ctype(rel):
            if rel.endswith(".mjs") or rel.endswith(".js"):
                return "text/javascript"
            if rel.endswith(".pdf"):
                return "application/pdf"
            return "application/octet-stream"

    httpd = HTTPServer(("127.0.0.1", 0), Handler)
    port = httpd.server_address[1]
    url = f"http://127.0.0.1:{port}/"
    print(f"Éditeur ouvert : {url}")
    if open_browser:
        webbrowser.open(url)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    done.wait(timeout=1800)  # 30 min max
    httpd.shutdown()
    return out_path
