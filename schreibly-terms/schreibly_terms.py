#!/usr/bin/env python3
"""Operate the Schreibly terms-acceptance gate.

The gate itself is Keycloak's built-in TERMS_AND_CONDITIONS required action: it
blocks token issuance and writes the acceptance timestamp. This tool owns the
three things the built-in action does not do.

  status   what every account in a realm has on record
  stamp    write terms_version / privacy_version / terms_locale + append history
  sweep    delete registrations abandoned at the gate (never a completed one)
  enforce  (re-)add the required action -- backfill, and re-acceptance after a bump
  notify   render / send the policy-change notice that must precede a bump

Every command defaults to --realm schreibly-dev. Dev first, always.
"""
import argparse
import datetime
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from kc import Keycloak, attr, attr_list  # noqa: E402
from config import load_config  # noqa: E402
from state import gate_live_since  # noqa: E402

REQUIRED_ACTION = "TERMS_AND_CONDITIONS"
ACCEPTED_AT = "terms_and_conditions"   # written by Keycloak's built-in action
HISTORY = "terms_history"
DEFAULT_REALM = "schreibly-dev"


# ── helpers ─────────────────────────────────────────────────────────────────

def now():
    return datetime.datetime.now(datetime.timezone.utc)


def iso(epoch_seconds):
    try:
        return datetime.datetime.fromtimestamp(
            int(epoch_seconds), datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    except (TypeError, ValueError):
        return "?"


def created(user):
    return datetime.datetime.fromtimestamp(
        user["createdTimestamp"] / 1000, datetime.timezone.utc)


def is_service_account(user):
    return bool(user.get("serviceAccountClientId")) or \
        user.get("username", "").startswith("service-account-")


def shown_locale(user, cfg):
    """The language the gate text was shown in.

    terms.ftl appends kc_locale to its own POST, so Keycloak's update_user_locale
    action persists exactly the rendered language onto the user. Anything outside
    the languages the copy exists in could not have been the language shown.
    """
    value = attr(user, "locale")
    if value in cfg["SUPPORTED_LOCALES"]:
        return value, None
    # Either the locale is one the gate copy does not exist in, or it is missing
    # entirely -- which would mean terms.ftl did not carry kc_locale through and
    # the recorded language is a fallback, not an observation. Say so, loudly.
    return cfg["DEFAULT_LOCALE"], value or "unset"


def history_entry(accepted_at, cfg, locale):
    return (f"at={accepted_at}"
            f";terms={cfg['TERMS_VERSION']}"
            f";privacy={cfg['PRIVACY_VERSION']}"
            f";locale={locale}")


def set_attr(user, name, value):
    user["attributes"] = user.get("attributes") or {}
    user["attributes"][name] = [value] if isinstance(value, str) else list(value)


def has_any_session(kc, realm, user_id):
    if kc.get(f"/admin/realms/{realm}/users/{user_id}/sessions"):
        return True
    for client in kc.get(f"/admin/realms/{realm}/clients?briefRepresentation=true"):
        if kc.get(f"/admin/realms/{realm}/users/{user_id}/offline-sessions/{client['id']}"):
            return True
    return False


# ── status ──────────────────────────────────────────────────────────────────

def cmd_status(kc, cfg, args):
    users = list(kc.users(args.realm))
    print(f"realm {args.realm}: {len(users)} accounts   "
          f"(current versions: terms {cfg['TERMS_VERSION']}, privacy {cfg['PRIVACY_VERSION']})")
    print(f"{'username':<38} {'accepted at':<21} {'terms':<10} {'privacy':<11} {'loc':<4} {'hist':<5} pending")
    gaps = 0
    for user in sorted(users, key=lambda u: u.get("username", "")):
        if is_service_account(user):
            continue
        accepted = attr(user, ACCEPTED_AT)
        pending = REQUIRED_ACTION in (user.get("requiredActions") or [])
        stale = accepted and (attr(user, "terms_version") != cfg["TERMS_VERSION"]
                              or attr(user, "privacy_version") != cfg["PRIVACY_VERSION"])
        if not accepted and not pending:
            gaps += 1
        print(f"{user.get('username', '?'):<38} {iso(accepted) if accepted else '-':<21} "
              f"{attr(user, 'terms_version', '-'):<10} {attr(user, 'privacy_version', '-'):<11} "
              f"{attr(user, 'terms_locale', '-'):<4} {len(attr_list(user, HISTORY)):<5} "
              f"{'yes' if pending else '-'}{'  (version behind)' if stale else ''}")
    if gaps:
        print(f"\n  !! {gaps} account(s) with neither an acceptance record nor the action "
              f"pending. That is a hole in the gate -- run: enforce --realm {args.realm}")
    else:
        print("\n  every account either has an acceptance record or the gate pending.")
    return 0


# ── stamp ───────────────────────────────────────────────────────────────────

def cmd_stamp(kc, cfg, args):
    """Record which documents, and in which language, each acceptance was for.

    Keycloak's built-in action writes only the timestamp. This adds the three
    attributes that make the timestamp mean something, and appends -- never
    overwrites -- a history value so an earlier acceptance survives a re-acceptance.
    """
    stamped = skipped = 0
    for user in kc.users(args.realm):
        accepted_at = attr(user, ACCEPTED_AT)
        if not accepted_at:
            continue
        locale, unexpected = shown_locale(user, cfg)
        if unexpected:
            print(f"  ! {user['username']}: user locale is {unexpected!r}, not one of "
                  f"{cfg['SUPPORTED_LOCALES']}. Recording {locale!r} as a FALLBACK -- "
                  f"this record does not prove which text was shown.")
        entry = history_entry(accepted_at, cfg, locale)
        history = attr_list(user, HISTORY)
        current_ok = (attr(user, "terms_version") == cfg["TERMS_VERSION"]
                      and attr(user, "privacy_version") == cfg["PRIVACY_VERSION"]
                      and attr(user, "terms_locale") == locale)
        if current_ok and entry in history:
            skipped += 1
            continue
        set_attr(user, "terms_version", cfg["TERMS_VERSION"])
        set_attr(user, "privacy_version", cfg["PRIVACY_VERSION"])
        set_attr(user, "terms_locale", locale)
        if entry not in history:
            history.append(entry)
            set_attr(user, HISTORY, history)
        print(f"  {'would stamp' if args.dry_run else 'stamped'} {user['username']}: "
              f"terms={cfg['TERMS_VERSION']} privacy={cfg['PRIVACY_VERSION']} "
              f"locale={locale} accepted={iso(accepted_at)} (history: {len(history)})")
        if not args.dry_run:
            kc.update_user(args.realm, user)
        stamped += 1
    if stamped or not getattr(args, "quiet", False):
        print(f"realm {args.realm}: {stamped} stamped, {skipped} already current"
              f"{' (DRY RUN, nothing written)' if args.dry_run else ''}")
    return 0


# ── sweep ───────────────────────────────────────────────────────────────────

def sweep_candidates(kc, cfg, realm, live_since):
    """Registrations abandoned at the gate.

    An account qualifies only if ALL of these hold:
      - it was created after the gate went live (see state.py -- without this,
        a pre-existing account that simply has not signed in since the backfill
        is indistinguishable from an abandoned registration)
      - the gate is still pending on it
      - it has no acceptance record and no history -- it never got through
      - it holds no session, active or offline
      - it is older than SWEEP_AFTER_DAYS
    Login events would be a stronger "never signed in" signal, but event storage
    is disabled on both realms. It is not needed for accounts created after the
    gate: the gate is mandatory, so one that never completed it never logged in.
    """
    cutoff = now() - datetime.timedelta(days=cfg["SWEEP_AFTER_DAYS"])
    for user in kc.users(realm):
        if is_service_account(user):
            continue
        if created(user) < live_since:
            continue
        if REQUIRED_ACTION not in (user.get("requiredActions") or []):
            continue
        if attr(user, ACCEPTED_AT) or attr_list(user, HISTORY):
            continue
        if created(user) > cutoff:
            continue
        if has_any_session(kc, realm, user["id"]):
            continue
        yield user


def cmd_sweep(kc, cfg, args):
    live_since = gate_live_since(args.realm)
    if live_since is None:
        print(f"refusing to sweep {args.realm}: no go-live moment recorded for it in "
              f"gate-live.json. Run setup_realm.py --realm {args.realm} first. Without "
              f"it there is no way to tell an abandoned registration from an account "
              f"that predates the gate.")
        return 2
    apply = args.apply and cfg.get("SWEEP_APPLY") == 1
    if args.apply and not apply:
        # Not an error: this is how the daily job reports what it *would* remove
        # until somebody reads a run and arms it. Falls through to a dry run.
        print("NOT ARMED: SWEEP_APPLY is not 1 in terms.env, so nothing will be "
              "deleted. Read the list below, then set SWEEP_APPLY=1 to arm it.")
    print(f"realm {args.realm}: accounts stuck at the gate for more than "
          f"{cfg['SWEEP_AFTER_DAYS']} days{'' if apply else '  (DRY RUN)'}")
    print(f"  only accounts created after the gate went live ({live_since:%Y-%m-%d %H:%M:%SZ}) "
          f"are eligible")
    found = 0
    for user in sweep_candidates(kc, cfg, args.realm, live_since):
        age = (now() - created(user)).days
        found += 1
        print(f"  {'DELETING' if apply else 'would delete'}: {user.get('username')} "
              f"email={user.get('email')} created={created(user):%Y-%m-%d} age={age}d "
              f"pending={user.get('requiredActions')}")
        if apply:
            # Belt and braces: never delete something that got through the gate.
            fresh = kc.user(args.realm, user["id"])
            if attr(fresh, ACCEPTED_AT) or attr_list(fresh, HISTORY):
                print("    ABORT on this account: it has an acceptance record after all")
                continue
            kc.delete(f"/admin/realms/{args.realm}/users/{user['id']}")
    print(f"  {found} account(s){'' if apply else ' would be deleted'}")
    return 0


# ── enforce ─────────────────────────────────────────────────────────────────

def cmd_enforce(kc, cfg, args):
    """(Re-)add the gate. --missing backfills; --all is the re-acceptance sweep."""
    touched = 0
    for user in kc.users(args.realm):
        if is_service_account(user):
            continue
        actions = user.get("requiredActions") or []
        if REQUIRED_ACTION in actions:
            continue
        if not args.all and attr(user, ACCEPTED_AT):
            continue  # --missing: this one already has a record
        user["requiredActions"] = actions + [REQUIRED_ACTION]
        print(f"  {'would add' if args.dry_run else 'added'} gate to {user.get('username')} "
              f"(record: {attr(user, 'terms_version', 'none')})")
        if not args.dry_run:
            kc.update_user(args.realm, user)
        touched += 1
    print(f"realm {args.realm}: {touched} account(s) will see the gate at next sign-in"
          f"{' (DRY RUN, nothing written)' if args.dry_run else ''}")
    return 0


# ── notify ──────────────────────────────────────────────────────────────────

def cmd_notify(kc, cfg, args):
    from notify_templates import render, all_changes_present
    out = pathlib.Path(__file__).resolve().parent / "notify-out"
    out.mkdir(exist_ok=True)
    password_file = pathlib.Path(cfg["SMTP_PASSWORD_FILE"])
    sending = args.send
    if sending and not all_changes_present(cfg["SUPPORTED_LOCALES"]):
        print("cannot send: the 'what changed' paragraph is missing for at least one "
              "language. Write notify-changes/<lang>.txt first -- a notice that does not "
              "say what changed is not a notice. Rendering only.")
        sending = False
    if sending and not password_file.is_file():
        print(f"cannot send: {password_file} does not exist. Keycloak's own SMTP "
              f"password is masked by the admin API and is not recoverable from it; "
              f"an operator has to put the SendGrid API key there. Rendering only.")
        sending = False
    smtp = None
    if sending:
        import smtplib
        smtp = smtplib.SMTP_SSL(cfg["SMTP_HOST"], int(cfg["SMTP_PORT"]), timeout=30)
        smtp.login(cfg["SMTP_USER"], password_file.read_text().strip())

    sent = 0
    for user in kc.users(args.realm):
        if is_service_account(user) or not user.get("email"):
            continue
        locale, _ = shown_locale(user, cfg)
        message = render(locale, cfg, args.effective_date, user, sender=cfg["SMTP_FROM"],
                         sender_name=cfg["SMTP_FROM_NAME"])
        path = out / f"{args.realm}-{user['username']}-{locale}.eml"
        path.write_text(message.as_string(), encoding="utf-8")
        if sending:
            smtp.send_message(message)
        print(f"  {'sent' if sending else 'rendered'} [{locale}] {user['email']} -> {path.name}")
        sent += 1
    if smtp:
        smtp.quit()
    print(f"realm {args.realm}: {sent} notice(s) {'sent' if sending else 'rendered to ' + str(out)}")
    if not sending:
        print("  nothing was emailed. Read the .eml files, then re-run with --send.")
    return 0


# ── entry point ─────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="command", required=True)

    def add(name, help_text):
        p = sub.add_parser(name, help=help_text)
        p.add_argument("--realm", default=DEFAULT_REALM,
                       help="a realm name, or 'all' for every realm in terms.env")
        return p

    add("status", "what every account has on record")
    p = add("stamp", "write version/locale record for accepted accounts")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--quiet", action="store_true",
                   help="say nothing when there was nothing to stamp, so every line "
                        "in the log is a real acceptance rather than a heartbeat")
    add("sweep", "delete registrations abandoned at the gate").add_argument(
        "--apply", action="store_true", help="actually delete (also needs SWEEP_APPLY=1)")
    p = add("enforce", "(re-)add the gate to accounts")
    p.add_argument("--all", action="store_true", help="everyone -- use after a version bump")
    p.add_argument("--dry-run", action="store_true")
    p = add("notify", "render/send the policy-change notice")
    p.add_argument("--effective-date", required=True, help="YYYY-MM-DD the new version applies")
    p.add_argument("--send", action="store_true")

    args = ap.parse_args()
    cfg = load_config()
    kc = Keycloak(cfg["KC_URL"])
    run = {"status": cmd_status, "stamp": cmd_stamp, "sweep": cmd_sweep,
           "enforce": cmd_enforce, "notify": cmd_notify}[args.command]
    if args.realm != "all":
        return run(kc, cfg, args)
    worst = 0
    for realm in cfg["REALMS"]:
        args.realm = realm
        worst = max(worst, run(kc, cfg, args) or 0)
        if not getattr(args, "quiet", False):
            print()
    return worst


if __name__ == "__main__":
    sys.exit(main())
