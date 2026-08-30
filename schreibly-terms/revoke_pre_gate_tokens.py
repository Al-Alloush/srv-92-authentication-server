#!/usr/bin/env python3
"""Revoke every session issued before the terms gate existed.

Required actions only run during browser authentication. A client holding an
offline refresh token never authenticates again -- it mints access tokens straight
from the token endpoint -- so an install that was signed in before the gate went
live bypasses it indefinitely. Enabling the required action is therefore not enough
on its own: the tokens that predate it have to go.

Three steps, in order:
  1. delete every offline session (kills the offline refresh tokens)
  2. log out every regular session
  3. set the realm's not-before to now and push it, so any access token already
     in flight is rejected rather than living out its remaining lifetime

After this, every client must authenticate in a browser again, which is what puts
it in front of the gate.

    ./revoke_pre_gate_tokens.py --realm schreibly-dev [--dry-run]
"""
import argparse
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from kc import Keycloak  # noqa: E402
from config import load_config  # noqa: E402


def offline_sessions(kc, realm, client):
    first, out = 0, []
    while True:
        batch = kc.get(f"/admin/realms/{realm}/clients/{client['id']}"
                       f"/offline-sessions?first={first}&max=100")
        if not batch:
            return out
        out += batch
        if len(batch) < 100:
            return out
        first += 100


def revoke(kc, realm, dry_run):
    clients = kc.get(f"/admin/realms/{realm}/clients?briefRepresentation=true")
    killed = 0
    for client in clients:
        sessions = offline_sessions(kc, realm, client)
        for session in sessions:
            print(f"  {'would delete' if dry_run else 'deleted'} offline session "
                  f"{session['id'][:8]}… {session.get('username')} @ {client['clientId']}")
            if not dry_run:
                kc.delete(f"/admin/realms/{realm}/sessions/{session['id']}?isOffline=true")
            killed += 1
    print(f"  offline sessions: {killed}")

    if not dry_run:
        kc.post(f"/admin/realms/{realm}/logout-all")
        print("  logged out all regular sessions")
        # Rejects tokens issued before now, so nothing in flight outlives this.
        kc.put(f"/admin/realms/{realm}", {"realm": realm, "notBefore": int(time.time())})
        kc.post(f"/admin/realms/{realm}/push-revocation")
        print(f"  realm not-before set to {int(time.time())} and pushed")
    return killed


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--realm", required=True, help="a realm name, or 'all'")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    cfg = load_config()
    kc = Keycloak(cfg["KC_URL"])
    realms = cfg["REALMS"] if args.realm == "all" else [args.realm]
    for realm in realms:
        print(f"{'DRY RUN ' if args.dry_run else ''}realm {realm}")
        revoke(kc, realm, args.dry_run)


if __name__ == "__main__":
    main()
