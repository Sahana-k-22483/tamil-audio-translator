#!/usr/bin/env python3
"""Local dev server with a /proxy-put endpoint to bypass CORS on signed storage URLs."""

import http.server
import urllib.request
import json
import os

PORT = int(os.environ.get("PORT", 8080))
BIND = "0.0.0.0"  # Render requires binding to all interfaces
DIR = os.path.dirname(os.path.abspath(__file__))


class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIR, **kwargs)

    def do_OPTIONS(self):
        self._cors_headers()
        self.end_headers()

    def do_POST(self):
        if self.path == "/proxy-put":
            self._handle_proxy_put()
        elif self.path == "/proxy-get":
            self._handle_proxy_get()
        else:
            self.send_response(404)
            self.end_headers()

    def _handle_proxy_get(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(content_length))
            target_url = body.get("url", "").strip()
            if not target_url:
                raise ValueError("url field is missing")

            req = urllib.request.Request(target_url, method="GET")
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

            try:
                with opener.open(req) as resp:
                    status = resp.status
                    response_body = resp.read()
            except urllib.error.HTTPError as e:
                status = e.code
                response_body = e.read()

            result = json.dumps({
                "status": status,
                "ok": 200 <= status < 300,
                "body": response_body.decode("utf-8", errors="replace")
            }).encode()

            self.send_response(200)
            self._cors_headers()
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(result)))
            self.end_headers()
            self.wfile.write(result)

        except Exception as e:
            error = json.dumps({"error": str(e)}).encode()
            self.send_response(500)
            self._cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(error)

    def _handle_proxy_put(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            target_url = self.headers.get("X-Target-URL", "").strip()
            target_headers_json = self.headers.get("X-Target-Headers", "{}")
            target_headers = json.loads(target_headers_json)

            if not target_url:
                raise ValueError("X-Target-URL header is missing")

            file_data = self.rfile.read(content_length)

            req = urllib.request.Request(target_url, data=file_data, method="PUT")
            for k, v in target_headers.items():
                req.add_header(k, v)

            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

            try:
                with opener.open(req) as resp:
                    status = resp.status
                    response_body = resp.read()
            except urllib.error.HTTPError as e:
                status = e.code
                response_body = e.read()

            result = json.dumps({
                "status": status,
                "ok": 200 <= status < 300,
                "body": response_body.decode("utf-8", errors="replace")
            }).encode()

            self.send_response(200)
            self._cors_headers()
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(result)))
            self.end_headers()
            self.wfile.write(result)

        except Exception as e:
            error = json.dumps({"error": str(e)}).encode()
            self.send_response(500)
            self._cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(error)

    def _cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")

    def log_message(self, format, *args):
        print(f"  {args[0]} {args[1]}")


if __name__ == "__main__":
    with http.server.HTTPServer((BIND, PORT), ProxyHandler) as httpd:
        print(f"Serving at http://localhost:{PORT}")
        httpd.serve_forever()
