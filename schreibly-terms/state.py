#!/usr/bin/env python3
"""When the gate went live on each realm.

The sweep deletes accounts that never got through the gate. That test is only
sound for accounts created after the gate existed: from that moment on, no
account can complete a login without accepting, so "no acceptance record" really
does mean "never signed in". An account created BEFORE the gate went live may
have signed in many times and simply not been asked yet -- deleting one of those
would destroy a real user's account.

So the moment the required action was switched on is recorded here, once per
realm, and the sweep will not touch anything older.
"""
import datetime
import json
import pathlib

STATE_FILE = pathlib.Path(__file__).resolve().parent / "gate-live.json"


def _read():
    if STATE_FILE.is_file():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {}


def gate_live_since(realm):
    """UTC datetime the gate went live on this realm, or None if unrecorded."""
    value = _read().get(realm)
    return datetime.datetime.fromisoformat(value) if value else None


def record_gate_live(realm, when=None):
    """Record the go-live moment once. Never moves an existing timestamp."""
    state = _read()
    if state.get(realm):
        return datetime.datetime.fromisoformat(state[realm]), False
    when = when or datetime.datetime.now(datetime.timezone.utc)
    state[realm] = when.isoformat()
    STATE_FILE.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return when, True
