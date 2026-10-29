"""Publication isolation probes; set OINK_CHROME to run the real browser cases."""

import base64
from functools import partial
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from threading import Thread
import unittest
from urllib.error import HTTPError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("book_pdf", ROOT / "bin/book-pdf.py")
pdf = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pdf)
CHROME = os.environ.get("OINK_CHROME")
PNG = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+a3i8AAAAASUVORK5CYII=")


class PublicationSafety(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.public = self.root / "public"
        self.public.mkdir()
        self.document = self.public / "index.html"
        self.manifest = self.root / "manifest.json"
        self.manifest.write_text(json.dumps({"schemaVersion": 1, "baseURL": "https://example.org/",
            "book": {"print": "/index.html"}, "pages": [{"path": "/chapter", "aggregateId": "chapter"}]}))

    def serve(self, handler):
        server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        def stop():
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)
        self.addCleanup(stop)
        return f"http://127.0.0.1:{server.server_port}"

    def render(self, *extra):
        command = [sys.executable, str(ROOT / "bin/book-pdf.py"), "--manifest", str(self.manifest),
                   "--public", str(self.public), "--output", str(self.root / "book.pdf"),
                   "--virtual-time-budget", "1000", "--timeout", "20", *extra]
        if CHROME:
            command += ["--chrome", CHROME]
        return subprocess.run(command, capture_output=True, text=True, timeout=30)

    def test_refresh_is_rejected_even_with_remote_opt_in(self):
        for attributes in ('http-equiv="REFRESH"', 'http-equiv="refresh" http-equiv="ignored"'):
            self.document.write_text(f'<meta {attributes} content="0;url=http://127.0.0.1:9/">')
            for flags in ((), ("--allow-remote-resources",)):
                with self.subTest(attributes=attributes, flags=flags):
                    result = self.render(*flags)
                    self.assertEqual(result.returncode, 1)
                    self.assertIn("must not navigate with meta refresh", result.stderr)
                    self.assertFalse((self.root / "book.pdf").exists())

    def test_server_refuses_symlink_resources_outside_public(self):
        outside = self.root / "outside.txt"
        outside.write_text("must remain private")
        (self.public / "escape.txt").symlink_to(outside)
        (self.public / "directory").mkdir()
        (self.public / "directory/index.html").symlink_to(outside)
        url = self.serve(partial(pdf.QuietHandler, directory=str(self.public)))
        for route in ("/escape.txt", "/directory/"):
            with self.subTest(route=route), self.assertRaises(HTTPError) as failure:
                urlopen(url + route, timeout=5)
            self.assertEqual(failure.exception.code, 404)
            failure.exception.close()

    @unittest.skipUnless(CHROME and shutil.which("pdftotext"), "set OINK_CHROME and install pdftotext for browser probes")
    def test_default_blocks_css_network_and_scripts_while_opt_in_allows_passive_media(self):
        requests = []
        class MediaHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                requests.append(self.path)
                self.send_response(200)
                self.send_header("Content-Type", "image/png")
                self.end_headers()
                self.wfile.write(PNG)
            def log_message(self, *_args):
                pass
        remote = self.serve(MediaHandler)
        probe = '<p id="probe">OINK_JS_DISABLED</p><script>document.getElementById("probe").textContent="OINK_JS_EXECUTED"</script>'
        self.document.write_text(f'<html><head><style>body{{background-image:url({remote}/css.png)}}</style></head><body>{probe}</body></html>')
        result = self.render()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(requests, [], "default publication made an indirect network request")
        text = subprocess.run(["pdftotext", str(self.root / "book.pdf"), "-"], capture_output=True, text=True, check=True).stdout
        self.assertIn("OINK_JS_DISABLED", text)
        self.assertNotIn("OINK_JS_EXECUTED", text)
        self.document.write_text(f'<html><body>{probe}<img src="{remote}/allowed.png"></body></html>')
        result = self.render("--allow-remote-resources", "--force")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("/allowed.png", requests)
        text = subprocess.run(["pdftotext", str(self.root / "book.pdf"), "-"], capture_output=True, text=True, check=True).stdout
        self.assertIn("OINK_JS_DISABLED", text)
        self.assertNotIn("OINK_JS_EXECUTED", text)


if __name__ == "__main__":
    unittest.main()
