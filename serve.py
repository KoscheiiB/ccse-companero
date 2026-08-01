"""Serve the app locally, with caching disabled.

Two deliberate restrictions, because this runs in a working directory that also holds
notes, source material and a .git directory:

  * it binds to loopback only, so nothing on the local network can reach it. To open the
    app on a phone, put a reverse proxy in front of this rather than widening the bind.
  * it serves an explicit list of files, so a stray path cannot walk into anything else,
    and there are no directory listings.

Caching is off because a browser will otherwise keep serving an old copy of the app after
a rebuild, which looks exactly like a change that did nothing.

Usage: python3 serve.py [port]
"""

import http.server
import socketserver
import sys
import urllib.parse

HOST = "127.0.0.1"
DEFAULT_PORT = 8765
HOME = "/ccse.html"

# Everything the installed app needs, and nothing else.
ALLOWED = frozenset({
    HOME,
    "/manifest.webmanifest",
    "/sw.js",
    "/icon-180.png",
    "/icon-512.png",
})


class AppHandler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {
        **http.server.SimpleHTTPRequestHandler.extensions_map,
        # served as octet-stream otherwise, and iOS then ignores the manifest
        ".webmanifest": "application/manifest+json",
    }

    def send_head(self):
        path = urllib.parse.urlparse(self.path).path
        if path == "/":
            self.send_response(302)
            self.send_header("Location", HOME)
            self.end_headers()
            return None
        if path not in ALLOWED:
            self.send_error(404, "Not Found")
            return None
        return super().send_head()

    def end_headers(self):
        self.send_header("Cache-Control", "no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def send_header(self, keyword, value):
        # with no Last-Modified the browser has no basis for a 304, so it always refetches
        if keyword == "Last-Modified":
            return
        super().send_header(keyword, value)


def parse_port(arg):
    try:
        port = int(arg)
    except ValueError:
        sys.exit(f"port must be a whole number, got {arg!r}")
    if not 1 <= port <= 65535:
        sys.exit(f"port must be between 1 and 65535, got {port}")
    return port


def main():
    port = parse_port(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer((HOST, port), AppHandler) as server:
        print(f"http://localhost:{port}{HOME}", flush=True)
        print(f"bound to {HOST} only; {len(ALLOWED)} files served", flush=True)
        server.serve_forever()


if __name__ == "__main__":
    main()
