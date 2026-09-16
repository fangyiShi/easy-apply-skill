from __future__ import annotations

import http.server
import socketserver
import sys
import tempfile
import threading
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from upload_file import parse_headers, upload_file  # noqa: E402


class _Handler(http.server.BaseHTTPRequestHandler):
    received = b""
    content_type = ""

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", "0"))
        type(self).received = self.rfile.read(length)
        type(self).content_type = self.headers.get("Content-Type", "")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"uploaded")

    def log_message(self, format: str, *args: object) -> None:
        return


class UploadFileTests(unittest.TestCase):
    def test_parse_headers(self) -> None:
        self.assertEqual(parse_headers(["X-Test: value"]), {"X-Test": "value"})
        with self.assertRaises(ValueError):
            parse_headers(["broken"])

    def test_http_requires_explicit_test_override_and_posts_multipart(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.pdf"
            path.write_bytes(b"PDF-CONTENT")

            with socketserver.TCPServer(("127.0.0.1", 0), _Handler) as server:
                thread = threading.Thread(target=server.serve_forever, daemon=True)
                thread.start()
                url = f"http://127.0.0.1:{server.server_address[1]}/upload"

                with self.assertRaises(ValueError):
                    upload_file(url, path)

                result = upload_file(url, path, allow_http=True)
                server.shutdown()
                thread.join(timeout=2)

            self.assertEqual(result["status"], 200)
            self.assertIn(b"PDF-CONTENT", _Handler.received)
            self.assertIn("multipart/form-data", _Handler.content_type)


if __name__ == "__main__":
    unittest.main()
