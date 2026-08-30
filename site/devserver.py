# -*- coding: utf-8 -*-
"""
Local preview server for arjuanfelipe.com.

`python -m http.server` sends no Cache-Control at all, so browsers apply
heuristic freshness and will happily serve a page they fetched before an
earlier build -- which looks exactly like the site having two different
headers depending on which page you open. This serves the same files with
caching switched off, so what you see on screen is what is on disk.

Run:  python devserver.py [port]        (default 8123, serves the repo root)
"""

import os
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class NoCacheHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store, must-revalidate")
        super().end_headers()


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8123
    print(f"serving {ROOT} at http://localhost:{port}/  (no-store)")
    ThreadingHTTPServer(("127.0.0.1", port), NoCacheHandler).serve_forever()


if __name__ == "__main__":
    main()
