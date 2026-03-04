#!/usr/bin/env python3
"""Serve Skyview locally with optional API key injection and browser launch."""
import argparse
import http.server
import os
import threading
import webbrowser

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)


def load_api_key() -> str:
    env_path = os.path.join(ROOT, ".env")
    if not os.path.exists(env_path):
        return ""
    with open(env_path, encoding="utf-8") as env_file:
        for line in env_file:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                if k.strip() == "GOOGLE_MAPS_API_KEY":
                    return v.strip()
    return ""


API_KEY = load_api_key()


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/skyview-standalone.html") and API_KEY:
            with open("skyview-standalone.html", "rb") as html_file:
                content = html_file.read().replace(b"GOOGLE_MAPS_API_KEY", API_KEY.encode())
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return
        super().do_GET()


def should_open_browser() -> bool:
    return bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY") or os.environ.get("BROWSER"))


def parse_args():
    parser = argparse.ArgumentParser(description="Run the Skyview local server.")
    parser.add_argument("--host", default="0.0.0.0", help="Host interface to bind (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8090, help="Port to bind (default: 8090)")
    parser.add_argument("--no-browser", action="store_true", help="Do not try to open the browser automatically")
    return parser.parse_args()


def main():
    args = parse_args()
    try:
        server = http.server.HTTPServer((args.host, args.port), Handler)
    except OSError as err:
        if err.errno == 98:
            print(f"Port {args.port} is already in use on {args.host}.")
            print(f"Stop the existing process or run with a different port, e.g. --port {args.port + 1}.")
            return
        raise
    host_for_url = "localhost" if args.host in ("127.0.0.1", "0.0.0.0") else args.host
    url = f"http://{host_for_url}:{args.port}/skyview-standalone.html"

    print(f"Serving Skyview at {url}")
    print(f"Bind address: {args.host}:{args.port}")
    print(f"API key injection: {'enabled' if API_KEY else 'disabled'}")

    if not args.no_browser and should_open_browser():
        threading.Timer(0.4, lambda: webbrowser.open(url)).start()
    elif not args.no_browser:
        print("Skipping browser auto-open (no GUI browser environment detected).")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
