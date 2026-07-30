"""Serve the folder over HTTP with caching disabled.

Useful when opening the app on a phone: browsers will happily keep serving an old
copy of ccse.html after a rebuild, which makes it look like a change did nothing.

Usage: python3 serve.py [port]
"""

import http.server
import socketserver
import sys

DEFAULT_PORT = 8765


class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def send_header(self, keyword, value):
        # without Last-Modified the browser has no basis for a 304, so it always refetches
        if keyword == "Last-Modified":
            return
        super().send_header(keyword, value)


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("0.0.0.0", port), NoCacheHandler) as server:
        print(f"http://localhost:{port}/ccse.html")
        server.serve_forever()


if __name__ == "__main__":
    main()
