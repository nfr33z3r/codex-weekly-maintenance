from __future__ import annotations

import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from weekly_maintenance.notify import NotificationError, notification_message, send_notification


class CaptureHandler(BaseHTTPRequestHandler):
    body = b""
    headers_seen = None

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        type(self).body = self.rfile.read(length)
        type(self).headers_seen = self.headers
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"{}")

    def log_message(self, *_args):
        return


class NotifyTests(unittest.TestCase):
    def test_completion_message_contains_no_repository_metadata(self):
        message = notification_message(count=2)
        self.assertEqual(
            message,
            "Le rapport hebdomadaire est prêt pour 2 dépôt(s). "
            "Quota Codex : inconnu. Ouvrir l’exécution GitHub privée.",
        )
        self.assertNotIn("acme/widget", message)
        self.assertNotIn("token", message.lower())

    def test_rejects_insecure_or_leaky_url(self):
        with self.assertRaises(NotificationError):
            send_notification("http://ntfy.sh/topic", "hello")
        with self.assertRaises(NotificationError):
            send_notification("https://ntfy.sh/topic?secret=value", "hello")

    def test_sends_expected_private_payload_and_headers(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), CaptureHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            send_notification(
                f"http://127.0.0.1:{server.server_port}/random-topic",
                "generic message",
                click_url="https://github.com/acme/orchestrator/actions/runs/1",
                token="secret-token",
                allow_http=True,
            )
        finally:
            server.shutdown()
            thread.join()
            server.server_close()
        self.assertEqual(CaptureHandler.body, b"generic message")
        self.assertEqual(CaptureHandler.headers_seen["Authorization"], "Bearer secret-token")
        self.assertEqual(
            CaptureHandler.headers_seen["Click"],
            "https://github.com/acme/orchestrator/actions/runs/1",
        )


if __name__ == "__main__":
    unittest.main()
