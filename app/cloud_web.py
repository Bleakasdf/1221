from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import threading

from app.main import main


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path not in {"/", "/health", "/ready"}:
            self.send_response(404)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write("Not found.\n".encode("utf-8"))
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write("Training bot is running.\n".encode("utf-8"))

    def log_message(self, format: str, *args) -> None:
        return


def run_health_server() -> None:
    port = int(os.getenv("PORT", "8000"))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()


if __name__ == "__main__":
    threading.Thread(target=run_health_server, daemon=True).start()
    import asyncio

    asyncio.run(main())
