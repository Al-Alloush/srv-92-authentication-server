#!/usr/bin/env python3
"""Put the terms-acceptance gate in place on a realm. Idempotent.

Three changes, and nothing else:
  1. the built-in TERMS_AND_CONDITIONS required action: enabled + default action
  2. the four acceptance attributes (+ a history attribute) declared on the user
     profile, admin-readable and admin-writable only, so the legal record cannot
     be edited by the account that it is about
  3. supported locales pinned to the languages the gate copy exists in

Clients, redirect URIs, scopes, roles and flows are not touched.

    ./setup_realm.py --realm schreibly-dev [--dry-run]
"""
import argparse
import json
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from kc import Keycloak  # noqa: E402
from config import load_config  # noqa: E402
from state import record_gate_live  # noqa: E402

REQUIRED_ACTION = "TERMS_AND_CONDITIONS"

# Written by Keycloak's built-in action itself. Declared here only so that it is a
# managed attribute: on a realm with unmanaged attributes disabled it would
# otherwise be invisible to the admin API, and the record could not be audited.
# The name is Keycloak's, not ours -- see README "What the attribute is called".
KEYCLOAK_OWNED = "terms_and_conditions"

ADMIN_ONLY = {"view": ["admin"], "edit": ["admin"]}

ATTRIBUTES = [
    {
        "name": KEYCLOAK_OWNED,
        "displayName": "Terms accepted at (epoch seconds)",
        "permissions": ADMIN_ONLY,
        "multivalued": False,
    },
    {
        "name": "terms_version",
        "displayName": "Terms of Service version accepted",
        "permissions": ADMIN_ONLY,
        "multivalued": False,
    },
    {
        "name": "privacy_version",
        "displayName": "Privacy Policy version acknowledged",
        "permissions": ADMIN_ONLY,
        "multivalued": False,
    },
    {
        "name": "terms_locale",
        "displayName": "Language the text was shown in",
        "permissions": ADMIN_ONLY,
        "multivalued": False,
    },
    {
        "name": "terms_history",
        "displayName": "Every acceptance, one value per acceptance",
        "permissions": ADMIN_ONLY,
        "multivalued": True,
    },
]


def sync_required_action(kc, realm, dry_run, default_action=True):
    path = f"/admin/realms/{realm}/authentication/required-actions/{REQUIRED_ACTION}"
    action = kc.get(path)
    before = (action["enabled"], action["defaultAction"])
    want = (True, default_action)
    if before == want:
        print(f"  required action  : already enabled={want[0]} default={want[1]}")
        return False
    action["enabled"], action["defaultAction"] = want
    print(f"  required action  : enabled/default {before} -> {want}")
    if not dry_run:
        kc.put(path, action)
    return True


def sync_locales(kc, realm, cfg, dry_run):
    realm_rep = kc.get(f"/admin/realms/{realm}")
    want = sorted(cfg["SUPPORTED_LOCALES"])
    have = sorted(realm_rep.get("supportedLocales") or [])
    default_ok = realm_rep.get("defaultLocale") == cfg["DEFAULT_LOCALE"]
    i18n_ok = realm_rep.get("internationalizationEnabled") is True
    if have == want and default_ok and i18n_ok:
        print(f"  locales          : already {want}, default {cfg['DEFAULT_LOCALE']}")
        return False
    print(f"  locales          : {have} -> {want}, default "
          f"{realm_rep.get('defaultLocale')} -> {cfg['DEFAULT_LOCALE']}, i18n {i18n_ok} -> True")
    if not dry_run:
        # Partial representation on purpose: Keycloak applies only the fields
        # present, so nothing else on the realm (SMTP password included) is touched.
        kc.put(f"/admin/realms/{realm}", {
            "realm": realm,
            "internationalizationEnabled": True,
            "supportedLocales": cfg["SUPPORTED_LOCALES"],
            "defaultLocale": cfg["DEFAULT_LOCALE"],
        })
    return True


def sync_user_profile(kc, realm, dry_run):
    path = f"/admin/realms/{realm}/users/profile"
    profile = kc.get(path)
    existing = {a["name"]: a for a in profile.get("attributes", [])}
    added, changed = [], []
    for want in ATTRIBUTES:
        have = existing.get(want["name"])
        if have is None:
            profile["attributes"].append(dict(want))
            added.append(want["name"])
        elif (have.get("permissions") != want["permissions"]
              or bool(have.get("multivalued")) != want["multivalued"]):
            have.update(want)
            changed.append(want["name"])
    if not added and not changed:
        print(f"  user profile     : all {len(ATTRIBUTES)} attributes already declared")
        return False
    print(f"  user profile     : added {added or '[]'}, corrected {changed or '[]'}")
    if not dry_run:
        kc.put(path, profile)
    return True


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--realm", required=True)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-default-action", action="store_true",
                    help="enable the action but do not apply it to new accounts yet. "
                         "Use it to prove the realm's terms.ftl renders before a broken "
                         "template can block every sign-in, then re-run without the flag.")
    args = ap.parse_args()

    cfg = load_config()
    kc = Keycloak(cfg["KC_URL"])
    print(f"{'DRY RUN ' if args.dry_run else ''}realm {args.realm}")
    touched = [
        sync_required_action(kc, args.realm, args.dry_run,
                             default_action=not args.no_default_action),
        sync_locales(kc, args.realm, cfg, args.dry_run),
        sync_user_profile(kc, args.realm, args.dry_run),
    ]
    if not args.dry_run and not args.no_default_action:
        # The sweep needs to know when the gate started applying to new accounts,
        # or it cannot tell an abandoned registration from an account that
        # predates the gate. Only the armed stage counts.
        when, first = record_gate_live(args.realm)
        print(f"  gate live since  : {when:%Y-%m-%d %H:%M:%SZ}"
              f"{' (recorded now)' if first else ' (already recorded)'}")
    print("  ->", "changes applied" if any(touched) else "nothing to do")


if __name__ == "__main__":
    main()
