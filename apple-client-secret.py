#!/usr/bin/env python3
r"""
Generate the "client secret" JWT that Keycloak pastes into the Apple OIDC
identity provider's Client Secret field.

Apple does not issue a static secret. The secret IS a short-lived ES256 JWT you
sign with your Sign in with Apple (.p8) private key. Max lifetime is 6 months;
when it expires, EVERY Apple login breaks at once with no warning.

Usage:
    pip install pyjwt cryptography
    python3 apple-client-secret.py \
        --team-id   ABCDE12345 \
        --key-id    KEY1234567 \
        --client-id dev.codexo.imeterreader.signin \   # the Services ID
        --p8        ./AuthKey_KEY1234567.p8 \
        --days      180
"""
import argparse, datetime, jwt   # PyJWT

APPLE_AUD = "https://appleid.apple.com"
APPLE_MAX_DAYS = 180  # Apple rejects secrets valid > 6 months

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--team-id",   required=True, help="Apple Developer Team ID (iss)")
    p.add_argument("--key-id",    required=True, help="Key ID of the .p8 (JWT header kid)")
    p.add_argument("--client-id", required=True, help="Services ID = Keycloak clientId (sub)")
    p.add_argument("--p8",        required=True, help="Path to AuthKey_XXX.p8")
    p.add_argument("--days",      type=int, default=APPLE_MAX_DAYS)
    a = p.parse_args()

    if a.days > APPLE_MAX_DAYS:
        raise SystemExit(f"Apple rejects secrets valid > {APPLE_MAX_DAYS} days")

    now = datetime.datetime.now(datetime.timezone.utc)
    exp = now + datetime.timedelta(days=a.days)

    with open(a.p8, "r") as f:
        key = f.read()

    token = jwt.encode(
        {
            "iss": a.team_id,
            "iat": int(now.timestamp()),
            "exp": int(exp.timestamp()),
            "aud": APPLE_AUD,
            "sub": a.client_id,
        },
        key,
        algorithm="ES256",
        headers={"kid": a.key_id, "alg": "ES256"},
    )

    print(token)
    print(f"\n# issued : {now:%Y-%m-%d %H:%M UTC}", file=__import__("sys").stderr)
    print(f"# EXPIRES: {exp:%Y-%m-%d %H:%M UTC}  <-- set a calendar reminder ~2 weeks before",
          file=__import__("sys").stderr)

if __name__ == "__main__":
    main()
