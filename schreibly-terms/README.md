# Schreibly terms-acceptance gate

Nobody reaches Schreibly without having **accepted the Terms of Service** and
**confirmed they have read the Privacy Policy**. It is enforced in Keycloak, so
all four clients — extension, macOS app, Windows app, website — are covered with
no client release.

Live on **`schreibly-dev`** and **`schreibly`** since 2026-08-29.

## The legal framing

Two different things, and they must never be merged into one sentence:

- **Terms of Service — accepted.** A contract. "I accept" is correct.
- **Privacy Policy — acknowledged, not consented to.** The legal basis is
  Art. 6(1)(b) GDPR (performance of the contract), not consent. Wording it as
  consent manufactures a consent the user could withdraw, and honouring that
  withdrawal would mean deleting their account. So: "I have read and understood",
  never "I consent to".

The data-collection / training consent is a different thing again — real consent
under Art. 6(1)(a), opt-in, separately withdrawable, and it lives on the account
as the `data-collection` role. **It must never be added to this screen.** Bundling
it here would invalidate it under Art. 7(4) GDPR. If a third checkbox ever seems
necessary, stop and ask.

## How it is built

Keycloak's **built-in `TERMS_AND_CONDITIONS` required action**
(`org.keycloak.authentication.requiredactions.TermsAndConditions`), enabled and
set as a default action on both realms. It already gates token issuance and
already writes the acceptance timestamp — there is no custom required-action SPI.

    Realm settings ▸ Authentication ▸ Required actions ▸ Terms and Conditions
        Enabled = On, Set as default action = On

### Enabling the action is not enough on its own

Required actions run during **browser authentication**. A client holding an offline
refresh token never authenticates again — it mints access tokens straight from the
token endpoint — so any install signed in before the gate went live bypasses it
indefinitely. On 2026-08-29 there were 26 such sessions (20 on `schreibly`, 6 on
`schreibly-dev`) held by the extension and desktop clients; they were revoked with
`revoke_pre_gate_tokens.py --realm all`, which deletes offline sessions, logs out
regular ones, and pushes a realm not-before so nothing in flight outlives it.

**Anything that re-introduces long-lived tokens re-opens this hole.** If the gate ever
looks like it "isn't showing", check `offline-session-count` before anything else.

### Where the screen lives

The screen is `login/terms.ftl`, added to the two **existing** login themes rather
than a new one, so the gate looks like the rest of the login and nothing else about
the realms' appearance changed:

    /srv/keycloak/themes/app.ui.schreibly/login/      → realm schreibly-dev
    /srv/keycloak/themes/app.ui.schreibly-v1/login/   → realm schreibly

`login/register.ftl` in the same two themes adds one sentence under the register
button — "The next step asks you to accept our Terms of Service and to confirm that
you have read our Privacy Policy", with both links. It is **not** an acceptance and
must never be reworded into one ("by registering you agree…"): nothing is accepted on
the registration form. It exists because the gate is the screen *after* registration,
and people looking at the form alone reasonably conclude the terms are missing.

Note that the registration page takes its language from the client's `ui_locales`.
`kc_locale` is ignored on `/protocol/openid-connect/auth` in this deployment — it only
takes effect on `/login-actions/*`, which is the path `terms.ftl` uses and why the
locale record works.

Both are bind-mounted into the container from `/srv/keycloak/themes`, so the theme
survives `docker compose up -d --force-recreate`. Nothing is written inside the
running container.

## What is stored, and where

Keycloak user attributes, on the user in the realm. They are **declared** on the
realm's user profile with `view`/`edit` permissions of `admin` only, so the account
the record is about cannot edit its own record — and so the record is visible to
the admin API on `schreibly-dev`, where unmanaged attributes are switched off.

| Attribute | Value | Written by |
|---|---|---|
| `terms_and_conditions` | acceptance timestamp, epoch seconds | Keycloak's built-in action |
| `terms_version` | e.g. `2026-08` | `schreibly_terms.py stamp` |
| `privacy_version` | e.g. `2026-08-29` | `schreibly_terms.py stamp` |
| `terms_locale` | `en` \| `de` \| `ar` — the language the text was shown in | `schreibly_terms.py stamp` |
| `terms_history` | one value per acceptance, ever | `schreibly_terms.py stamp` |

`terms_locale` is not decoration: proving acceptance means proving *which text* was
shown, and a German user read different words from an English one.

**No protocol mapper.** Nothing downstream needs these in a token — the gate is
enforced by Keycloak itself. Keep them out of the tokens.

### What the attribute is called

The brief for this work called it `termsAndConditions`. Keycloak 26.5.3 actually
writes **`terms_and_conditions`** (`TermsAndConditions.USER_ATTRIBUTE`). The name
is Keycloak's, not ours; it cannot be renamed, and everything here uses the real one.

### How the locale is known to be the one shown

`terms.ftl` appends `kc_locale=<the language it just rendered in>` to its own POST
target. `LoginActionsService` turns that into the `locale_user_requested` auth note,
and Keycloak's `update_user_locale` required action — already enabled, priority 1000,
so it runs later in the same request — persists it as the user's `locale` attribute.
The stamper reads that. The recorded language is therefore the language of the text
that was actually on screen, not a guess.

### The version strings are configuration

They live in `terms.env`, not in code and not in the template, so bumping a document
is a config change. They are the `updated:` date of the published document,
normalised to ISO — **the document date is the version**:

    https://schreibly.com/legal/terms    "Last updated: August 2026"     → 2026-08
    https://schreibly.com/legal/privacy  "Last updated: 29 August 2026"  → 2026-08-29

`check_versions.py` reads both live pages and shouts if they have drifted away from
`terms.env`. It runs daily from cron.

> **Open issue for the website side.** The Terms document's `updated:` frontmatter
> carries a month but no day, so `terms_version` can only be month-precise. Two Terms
> revisions published in the same month would be indistinguishable in the acceptance
> record. The fix belongs in `AppWebsite.Shared/Content/legal/<lang>/terms.md`: give
> it a full date, then bump `TERMS_VERSION` to match.

## The commands

All of them default to `--realm schreibly-dev`. Dev first, always.

    ./setup_realm.py --realm R [--dry-run] [--no-default-action]
        Puts the gate in place: required action on, the five attributes declared,
        locales pinned. Idempotent. `--no-default-action` enables the action
        without applying it to new accounts — use it to prove that realm's
        terms.ftl renders before a broken template can block every sign-in.

    ./schreibly_terms.py status  --realm R
        What every account has on record, and whether any account has neither a
        record nor the gate pending (that would be a hole).

    ./schreibly_terms.py stamp   --realm R [--dry-run] [--quiet]
        Writes terms_version / privacy_version / terms_locale and APPENDS to
        terms_history. Never overwrites a history entry. Runs from cron every
        5 minutes with --quiet, which prints nothing when there was nothing to
        do — so every line in logs/stamp.log is a real acceptance, not a
        heartbeat, and the log does not grow on its own.

    ./schreibly_terms.py sweep   --realm R [--apply]
        Deletes registrations abandoned at the gate. See below.

    ./schreibly_terms.py enforce --realm R [--all] [--dry-run]
        (Re-)adds the required action. Default: only accounts with no record
        (the backfill). `--all`: everybody — the re-acceptance sweep after a
        version bump. Paginated, idempotent, safe to re-run.

    ./schreibly_terms.py notify  --realm R --effective-date YYYY-MM-DD [--send]
        Renders the policy-change notice per user in their language. Sends
        nothing without `--send`, and refuses to send until the "what changed"
        paragraph exists.

    ./check_versions.py
        Live document dates vs terms.env. Exit 0 in sync, 1 drift, 2 unreadable.

Pass `--realm all` to any of them to run over every realm in `terms.env`.

Credentials are never stored here: `kc.py` reads the admin username and password
out of the running container's environment. Override with `KC_ADMIN` /
`KC_ADMIN_PASSWORD` if a dedicated service account is ever preferred.

## Scheduling

Installed as the `devopsuser` crontab on 2026-08-29 from `crontab.txt`: `stamp`
every 5 minutes per realm, `sweep` daily at 03:20 and 03:25, `check_versions.py`
daily at 08:00. Output goes to `logs/`.

    crontab -l                                    # what is scheduled
    tail -f /srv/keycloak/schreibly-terms/logs/stamp.log
    crontab /srv/keycloak/schreibly-terms/crontab.txt   # re-install after editing

## Declining

Refusing leaves the person without a usable account: no token is issued, and the
same screen blocks every later sign-in until they accept. Verified — a decline
returns `error=access_denied&error_description=termsAndConditionsDeclined` with no
authorization code, and the required action stays pending.

But with self-registration Keycloak creates the user row *first* and runs required
actions *after*, so a decline leaves a real account row — email address, display
name — belonging to somebody who refused our terms. It can never authenticate, but
holding personal data for a person who declined is a data-minimisation problem
(Art. 5(1)(c) GDPR), not just untidiness.

## The sweep

`sweep` deletes an account only if **all** of these hold:

1. it was created **after the gate went live on that realm** (`gate-live.json`),
2. the gate is still pending on it,
3. it has no `terms_and_conditions` and no `terms_history` — it never got through,
4. it holds no session, active or offline,
5. it is older than `SWEEP_AFTER_DAYS` (7).

Condition 1 is the important one. Login events are disabled on both realms, so
"never signed in" cannot be read from event history. For an account created after
the gate it does not need to be: the gate is mandatory, so an account that never
completed it never completed a login. For an account created **before** the gate,
that inference is false — it may have signed in for months and simply not been asked
yet. Without condition 1 the backfilled accounts would have looked like week-old
abandoned registrations and been deleted. `gate-live.json` is written once per realm
by `setup_realm.py`; the sweep refuses to run for a realm that has no entry.

7 days, not 7 minutes: someone who closed the tab to go and read the policy properly
must be able to come back and finish.

**Armed since 2026-08-29** (`SWEEP_APPLY=1` in `terms.env`), after dry runs on both
realms returned no candidates. The daily job will now delete what it lists. Set
`SWEEP_APPLY=0` to disarm — the job then only reports, and no other change is needed.

Note that the armed delete path has never actually removed an account: every run so
far, dry or armed, has found nothing to remove. The first deletion will be the first
time that code executes for real. `logs/sweep.log` names every account before it goes.

## Policy updates — notify, then require re-acceptance

When either document changes materially, every existing user must be **told**, and
must **re-accept** at their next sign-in.

1. **Write what changed** into `notify-changes/en.txt`, `de.txt`, `ar.txt`. One
   paragraph each. `notify --send` refuses without them — a notice that does not
   say what changed is not a notice.
2. **Notify, at least 30 days before the effective date:**

       ./schreibly_terms.py notify --realm schreibly --effective-date 2026-11-01
       # read notify-out/*.eml, then:
       ./schreibly_terms.py notify --realm schreibly --effective-date 2026-11-01 --send

   The notice states what changed, links both documents, and gives the date from
   which the new version applies. For a Terms change the user must have a real
   chance to leave instead of accepting — the copy says so explicitly.

   *SMTP:* both realms are configured for SendGrid as `auth@schreibly.com`, so
   Keycloak's own mail works. This tool cannot reuse it — the admin API masks the
   stored password — so `notify --send` needs a SendGrid API key in the file named
   by `SMTP_PASSWORD_FILE` (default `./smtp-password`, gitignored, does not exist).
   The website's own key is in `/srv/apps/Schreibly/website/prod/.env` as
   `SendGrid__ApiKey`; whether to reuse it is an operator's decision, not this
   tool's. No credentials were invented.
3. **On the effective date** — the day the new documents actually go live:

       # bump TERMS_VERSION / PRIVACY_VERSION in terms.env to the new dates
       ./check_versions.py                                   # confirm they match the site
       ./schreibly_terms.py enforce --realm schreibly --all  # everyone re-accepts

   Bump the config on the effective date, not 30 days earlier: the stamper records
   whatever `terms.env` says at the moment it runs, so bumping before the documents
   change would record acceptances against a version nobody had been shown.
4. Their next sign-in shows the screen again. The stamper overwrites the current
   four attributes with the new version, date and locale, and **appends** a new
   `terms_history` value — the earlier acceptance survives, so "which text did this
   user accept, and when" stays answerable for every version they were ever shown.

Re-acknowledging the Privacy Policy is fine to require, but it stays an
acknowledgement. Only the Terms are re-*accepted*.

## Known properties, honestly

- **The two checkboxes are enforced in the browser, not on the server.** They are
  `required`, so native HTML validation blocks the submit with no JavaScript — but
  Keycloak's built-in action only ever sees `accept`, and a hand-crafted POST could
  skip them. That is inherent to using the built-in action instead of a custom SPI.
  What is server-enforced is the thing that matters: no token without passing this
  screen.
- **The record lags acceptance by up to 5 minutes**, until the stamper next runs.
  Nothing downstream reads these attributes, so nothing is affected.
- **Message bundles are cached per theme and locale.** `KC_SPI_THEME_CACHE_THEMES=false`
  does not clear them: after editing a `messages_*.properties`, a locale that was
  already served keeps the old bundle. Recreate the container to pick it up —
  `cd /srv/keycloak && docker compose up -d --force-recreate keycloak`. This is
  how the English and German copy first failed to appear on the prod theme.
- `docker restart` does not re-read `.env` on this host. Always use
  `docker compose up -d --force-recreate`.

## Files

    kc.py                 Keycloak admin client; reads credentials from the container
    config.py             terms.env reader
    state.py              gate-live.json — when the gate started applying, per realm
    setup_realm.py        put the gate in place on a realm (idempotent)
    schreibly_terms.py    status / stamp / sweep / enforce / notify
    notify_templates.py   the policy-change notice, en/de/ar
    check_versions.py     live document dates vs terms.env
    revoke_pre_gate_tokens.py  kill sessions that predate the gate (one-off)
    terms.env             versions, locales, sweep settings, SMTP
    crontab.txt           the scheduled jobs
    gate-live.json        written by setup_realm.py — do not hand-edit
    backup-2026-08-29/    full realm export taken before any of this was applied
