#!/usr/bin/env python3
"""Compare the versions in terms.env against what the live site actually serves.

The version strings are supposed to BE the document date -- if the website
publishes a new `updated:` date and terms.env is not bumped, every acceptance
recorded from then on names a document that is no longer the one being shown.
Nothing in Keycloak can notice that, so this does.

Exit status 0 = in sync, 1 = drift, 2 = could not check.
"""
import pathlib
import re
import sys
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from config import load_config  # noqa: E402

MONTHS = {m: f"{i:02d}" for i, m in enumerate(
    ["january", "february", "march", "april", "may", "june", "july",
     "august", "september", "october", "november", "december"], start=1)}

UPDATED = re.compile(r'class="schr-legal-updated"[^>]*>\s*Last updated:\s*([^<]+?)\s*<')


def iso_version(text):
    """'29 August 2026' -> 2026-08-29 ; 'August 2026' -> 2026-08."""
    match = re.match(r"(?:(\d{1,2})\.?\s+)?([A-Za-z]+)\s+(\d{4})$", text.strip())
    if not match:
        return None
    day, month, year = match.groups()
    month = MONTHS.get(month.lower())
    if not month:
        return None
    return f"{year}-{month}-{int(day):02d}" if day else f"{year}-{month}"


def published(url):
    request = urllib.request.Request(url, headers={"Accept-Language": "en"})
    with urllib.request.urlopen(request, timeout=30) as response:
        html = response.read().decode("utf-8", "replace")
    match = UPDATED.search(html)
    if not match:
        return None, None
    return match.group(1), iso_version(match.group(1))


def main():
    cfg = load_config()
    drift = failed = False
    for label, url_key, version_key in (
            ("Terms of Service", "TERMS_URL", "TERMS_VERSION"),
            ("Privacy Policy", "PRIVACY_URL", "PRIVACY_VERSION")):
        raw, live = published(cfg[url_key])
        configured = cfg[version_key]
        if live is None:
            print(f"  ?? {label}: could not read a date from {cfg[url_key]} "
                  f"(found {raw!r}). Check the page markup.")
            failed = True
        elif live == configured:
            print(f"  ok {label}: {configured}  (site says {raw!r})")
        else:
            print(f"  !! {label}: terms.env says {configured}, the site says {raw!r} "
                  f"-> {live}. Bump {version_key} and follow the re-acceptance "
                  f"procedure in README.md.")
            drift = True
    return 2 if failed else 1 if drift else 0


if __name__ == "__main__":
    sys.exit(main())
