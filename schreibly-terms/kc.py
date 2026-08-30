#!/usr/bin/env python3
"""Minimal Keycloak admin REST client for the Schreibly terms gate tooling.

Credentials are NOT stored here. By default they are read out of the running
keycloak container's environment (KC_BOOTSTRAP_ADMIN_USERNAME / _PASSWORD), so
this tooling introduces no second copy of the admin password. Override with
KC_ADMIN / KC_ADMIN_PASSWORD in the environment if you prefer a dedicated account.
"""
import json
import os
import subprocess
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_URL = "http://127.0.0.1:8090"
CONTAINER = os.environ.get("KC_CONTAINER", "keycloak")


class Keycloak:
    def __init__(self, url=None):
        self.url = (url or os.environ.get("KC_URL") or DEFAULT_URL).rstrip("/")
        self._token = None

    # ── auth ────────────────────────────────────────────────────────────────
    def _credentials(self):
        user = os.environ.get("KC_ADMIN")
        password = os.environ.get("KC_ADMIN_PASSWORD")
        if user and password:
            return user, password
        out = subprocess.run(
            ["docker", "inspect", CONTAINER, "--format", "{{json .Config.Env}}"],
            capture_output=True, text=True, check=True).stdout
        env = dict(e.split("=", 1) for e in json.loads(out) if "=" in e)
        return env["KC_BOOTSTRAP_ADMIN_USERNAME"], env["KC_BOOTSTRAP_ADMIN_PASSWORD"]

    def token(self):
        if self._token:
            return self._token
        user, password = self._credentials()
        data = urllib.parse.urlencode({
            "client_id": "admin-cli", "username": user,
            "password": password, "grant_type": "password"}).encode()
        with urllib.request.urlopen(
                self.url + "/realms/master/protocol/openid-connect/token", data, timeout=30) as r:
            self._token = json.load(r)["access_token"]
        return self._token

    # ── plumbing ────────────────────────────────────────────────────────────
    def call(self, method, path, body=None):
        payload = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(self.url + path, data=payload, method=method)
        req.add_header("Authorization", "Bearer " + self.token())
        if payload:
            req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                text = r.read().decode()
                return json.loads(text) if text.strip() else None
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"HTTP {e.code} on {method} {path}: {e.read().decode()}") from None

    def get(self, path):
        return self.call("GET", path)

    def put(self, path, body):
        return self.call("PUT", path, body)

    def post(self, path, body=None):
        return self.call("POST", path, body)

    def delete(self, path):
        return self.call("DELETE", path)

    # ── users ───────────────────────────────────────────────────────────────
    def users(self, realm, page=100):
        """Every user in the realm, paginated, full representation."""
        first = 0
        while True:
            batch = self.get(f"/admin/realms/{realm}/users"
                             f"?briefRepresentation=false&first={first}&max={page}")
            if not batch:
                return
            yield from batch
            if len(batch) < page:
                return
            first += page

    def user(self, realm, user_id):
        return self.get(f"/admin/realms/{realm}/users/{user_id}")

    def update_user(self, realm, user):
        """PUT a whole user representation back. Always read-modify-write."""
        self.put(f"/admin/realms/{realm}/users/{user['id']}", user)


def attr(user, name, default=None):
    """First value of a user attribute, or default."""
    values = (user.get("attributes") or {}).get(name) or []
    return values[0] if values else default


def attr_list(user, name):
    return list((user.get("attributes") or {}).get(name) or [])
