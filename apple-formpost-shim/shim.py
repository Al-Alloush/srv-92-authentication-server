#!/usr/bin/env python3
"""
apple-formpost-shim
===================
Sign in with Apple requires response_mode=form_post whenever the email/name
scope is requested, so Apple invokes the broker callback with an HTTP POST
(params in the body). Keycloak 26.5's generic OIDC broker endpoint is GET-only
(@GET/@QueryParam) and answers 405 to that POST.

This shim sits ONLY on POST requests to the apple broker endpoint (routed there
by Traefik). It reads code/state (or error) from the form body and issues a
303 See Other back to the SAME Keycloak endpoint as a GET with those params in
the query string. 303 turns the cross-site POST into a same-site top-level GET,
so the browser re-sends its SameSite=Lax Keycloak session cookies and Keycloak's
GET endpoint completes the token exchange (email arrives in Apple's id_token).

One shim serves every realm that has an Apple IdP: the target realm is taken
from the request path rather than from config, so adding a realm is an env-var
edit (REALMS) plus a Traefik router.

Notes:
- The Location is not attacker-controlled: the host is fixed (BASE_URL), the
  path must match PATH_RE exactly, the realm must be in the REALMS allow-list,
  and only code/state/error are reflected. So this is not an open redirect.
- Apple's first-login-only `user` field (display name) is intentionally dropped:
  Keycloak's generic OIDC provider cannot ingest it anyway. Email comes from the
  id_token, not from `user`, so nothing Keycloak could use is lost.
"""
import os
import re
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

BASE_URL = os.environ.get("BASE_URL", "https://auth.codexo.dev").rstrip("/")
REALMS = frozenset(
    r.strip() for r in os.environ.get("REALMS", "imeterreader_dev").split(",") if r.strip()
)
PATH_RE = re.compile(r"^/realms/([^/]+)/broker/apple/endpoint$")
PORT = int(os.environ.get("LISTEN_PORT", "8080"))
# Only these are forwarded onward; everything else in the POST body is discarded.
PASSTHROUGH = ("code", "state", "error", "error_description")


class Handler(BaseHTTPRequestHandler):
    server_version = "apple-formpost-shim/1.0"
    protocol_version = "HTTP/1.1"

    def _target(self):
        """Same-realm broker endpoint for this request, or None if not allowed."""
        m = PATH_RE.match(urllib.parse.urlparse(self.path).path)
        if not m or m.group(1) not in REALMS:
            return None
        return f"{BASE_URL}/realms/{m.group(1)}/broker/apple/endpoint"

    def _bare(self, code):
        self.send_response(code)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def _redirect(self, target, params):
        forwarded = {k: params[k] for k in PASSTHROUGH if k in params}
        query = urllib.parse.urlencode(forwarded)
        location = target + (("?" + query) if query else "")
        self.send_response(303)
        self.send_header("Location", location)
        self.send_header("Content-Length", "0")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()

    def do_POST(self):
        target = self._target()
        length = int(self.headers.get("Content-Length", "0") or "0")
        raw = self.rfile.read(length).decode("utf-8", "replace") if length else ""
        if target is None:
            self._bare(404)
            return
        parsed = urllib.parse.parse_qs(raw, keep_blank_values=True)
        params = {k: v[-1] for k, v in parsed.items()}
        if "code" not in params and "error" not in params:
            self._bare(400)
            return
        self._redirect(target, params)

    def do_GET(self):
        # Traefik routes GET straight to Keycloak, so this normally never fires.
        # Fail safe: bounce any stray GET onward, preserving its query.
        target = self._target()
        if target is None:
            self._bare(404)
            return
        q = urllib.parse.urlparse(self.path).query
        self._redirect(target, dict(urllib.parse.parse_qsl(q, keep_blank_values=True)))

    def log_message(self, fmt, *args):  # quiet; Traefik/access logs cover this
        pass


if __name__ == "__main__":
    ThreadingHTTPServer.allow_reuse_address = True
    with ThreadingHTTPServer(("0.0.0.0", PORT), Handler) as httpd:
        httpd.serve_forever()
