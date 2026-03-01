#!/usr/bin/env python3
"""Open Skyview in your browser. Just double-click this file."""
import http.server, webbrowser, threading, os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
PORT = 8090
server = http.server.HTTPServer(('localhost', PORT), http.server.SimpleHTTPRequestHandler)
print(f"Serving at http://localhost:{PORT}")
threading.Timer(0.5, lambda: webbrowser.open(f"http://localhost:{PORT}/skyview-standalone.html")).start()
server.serve_forever()
