#!/usr/bin/env bash
# Rotate the Sign in with Apple client-secret JWT on the Keycloak 'apple' IdP.
#
# Apple's client secret is a self-signed ES256 JWT valid for max 180 days. When
# it expires EVERY Apple login breaks at once, with no warning. Run this before
# expiry (the generator prints the exact date on each run) and set a calendar
# reminder ~2 weeks ahead.
#
# Both realms share ONE Apple Services ID (dev.codexo.app.ui.imeterrecorder.signin,
# with a Return URL registered per realm), so they share one secret JWT and must be
# rotated together -- updating only one leaves the other on an expired secret.
#
# Required env: TEAM_ID, KEY_ID, CLIENT_ID (Apple Services ID), P8 (path to
#   AuthKey_*.p8), KC_ADMIN_USER, KC_ADMIN_PASS
# Optional env: DAYS(=180) ALIAS(=apple) KC_CONTAINER(=keycloak)
#   REALMS(=imeterreader_dev,imeterreader) -- comma-separated; REALM=x still works
#   for a one-off single-realm run.
set -euo pipefail

: "${TEAM_ID:?set TEAM_ID}"
: "${KEY_ID:?set KEY_ID}"
: "${CLIENT_ID:?set CLIENT_ID (Apple Services ID)}"
: "${P8:?set P8 (path to AuthKey_*.p8)}"
: "${KC_ADMIN_USER:?set KC_ADMIN_USER}"
: "${KC_ADMIN_PASS:?set KC_ADMIN_PASS}"
DAYS="${DAYS:-180}"
REALMS="${REALMS:-${REALM:-imeterreader_dev,imeterreader}}"
ALIAS="${ALIAS:-apple}"
KC_CONTAINER="${KC_CONTAINER:-keycloak}"
HERE="$(cd "$(dirname "$0")" && pwd)"

# 1) generate the JWT (token -> stdout, issued/expiry -> stderr for the operator)
SECRET="$(python3 "$HERE/apple-client-secret.py" \
  --team-id "$TEAM_ID" --key-id "$KEY_ID" --client-id "$CLIENT_ID" \
  --p8 "$P8" --days "$DAYS")"

# 2) authenticate kcadm inside the container
docker exec "$KC_CONTAINER" /opt/keycloak/bin/kcadm.sh config credentials \
  --server http://localhost:8080 --realm master \
  --user "$KC_ADMIN_USER" --password "$KC_ADMIN_PASS" >/dev/null

# 3) per realm: read current provider, merge new clientId+clientSecret, push back
CUR="$(mktemp)"; NEXT="$(mktemp)"
trap 'rm -f "$CUR" "$NEXT"' EXIT
for REALM in ${REALMS//,/ }; do
  docker exec "$KC_CONTAINER" /opt/keycloak/bin/kcadm.sh get \
    "identity-provider/instances/$ALIAS" -r "$REALM" > "$CUR"
  CLIENT_ID="$CLIENT_ID" SECRET="$SECRET" python3 - "$CUR" > "$NEXT" <<'PY'
import json, os, sys
d = json.load(open(sys.argv[1]))
d.setdefault("config", {})
d["config"]["clientId"] = os.environ["CLIENT_ID"]
d["config"]["clientSecret"] = os.environ["SECRET"]
print(json.dumps(d))
PY
  # write as root + chmod so the container's keycloak user can read it (docker cp
  # would land it uid-1001/0600 and kcadm, running as keycloak, can't read it)
  docker exec -u root -i "$KC_CONTAINER" \
    sh -c 'cat > /tmp/apple-idp-next.json && chmod 644 /tmp/apple-idp-next.json' < "$NEXT"
  docker exec "$KC_CONTAINER" /opt/keycloak/bin/kcadm.sh update \
    "identity-provider/instances/$ALIAS" -r "$REALM" -f /tmp/apple-idp-next.json
  docker exec -u root "$KC_CONTAINER" rm -f /tmp/apple-idp-next.json

  echo "Rotated '$ALIAS' clientId+clientSecret in realm '$REALM'."
done
