import json
import threading
from urllib.parse import parse_qs
import os

from http.server import BaseHTTPRequestHandler, HTTPServer
from dcnow import CONFIGURATION_FILE, scan_mac_address


class DreamPiConfigurationService(BaseHTTPRequestHandler):

    def _get_post_data(self):
        if self.headers.get('Content-Type') == 'application/x-www-form-urlencoded':
            postvars = parse_qs(
                self.rfile.read(int(self.headers.get('Content-Length'))).decode(),
                keep_blank_values=True
            )
        else:
            postvars = {}

        return postvars

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        enabled_state = True
        if os.path.exists(CONFIGURATION_FILE):
            with open(CONFIGURATION_FILE, "r") as f:
                enabled_state = json.loads(f.read())["enabled"]

        self.wfile.write(json.dumps({
            "mac_address": scan_mac_address(),
            "is_enabled": enabled_state
        }).encode())


    def do_POST(self):
        enabled_state = True

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        post_data = self._get_post_data()
        if 'disable' in post_data:
            enabled_state = False
        else:
            enabled_state = True

        with open(CONFIGURATION_FILE, "w") as f:
            f.write(json.dumps({"enabled": enabled_state}))

        self.wfile.write(json.dumps({
            "mac_address": scan_mac_address(),
            "is_enabled": enabled_state
        }).encode())


server = None
thread = None

def start():
    global server
    global thread
    server = HTTPServer(('0.0.0.0', 1998), DreamPiConfigurationService)
    thread = threading.Thread(target=server.serve_forever)
    thread.start()

def stop():
    global server
    global thread

    if server:
        server.shutdown()

    if thread:
        thread.join()
