#!/usr/bin/env python3
"""Read terms.env. Plain KEY=VALUE, no shell, no interpolation."""
import os
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
ENV_FILE = pathlib.Path(os.environ.get("TERMS_ENV", HERE / "terms.env"))

LISTS = {"REALMS", "SUPPORTED_LOCALES"}
INTS = {"SWEEP_AFTER_DAYS", "SWEEP_APPLY", "SMTP_PORT"}


def load_config(path=None):
    path = pathlib.Path(path) if path else ENV_FILE
    cfg = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip()
        if key in LISTS:
            cfg[key] = [v.strip() for v in value.split(",") if v.strip()]
        elif key in INTS:
            cfg[key] = int(value)
        else:
            cfg[key] = value
    # The environment wins, so a one-off run can override without editing the file.
    for key in list(cfg) + ["KC_URL"]:
        if key in os.environ:
            raw = os.environ[key]
            cfg[key] = ([v.strip() for v in raw.split(",") if v.strip()] if key in LISTS
                        else int(raw) if key in INTS else raw)
    missing = {"TERMS_VERSION", "PRIVACY_VERSION", "REALMS",
               "SUPPORTED_LOCALES", "DEFAULT_LOCALE"} - cfg.keys()
    if missing:
        raise SystemExit(f"{path}: missing required setting(s): {sorted(missing)}")
    return cfg
