#!/bin/sh
set -eu
umask 077

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
SECRETS_FILE="$SCRIPT_DIR/../secrets/alertmanager.env"
OUTPUT_FILE="$SCRIPT_DIR/alertmanager.runtime.yml"

set -a
. "$SECRETS_FILE"
set +a

: "${SMTP_USERNAME:?SMTP_USERNAME is required}"
: "${SMTP_PASSWORD:?SMTP_PASSWORD is required}"

export SMTP_USERNAME SMTP_PASSWORD

python3 - "$OUTPUT_FILE" <<'PY'
import os
import sys

def yaml_quote(value):
    return "'" + value.replace("'", "''") + "'"

username = yaml_quote(os.environ["SMTP_USERNAME"])
password = yaml_quote(os.environ["SMTP_PASSWORD"])
output = sys.argv[1]

config = f"""global:
  resolve_timeout: 5m
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: {username}
  smtp_auth_username: {username}
  smtp_auth_password: {password}
  smtp_require_tls: true

route:
  receiver: email-alerts
  group_by:
    - alertname
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h

receivers:
  - name: email-alerts
    email_configs:
      - to: {username}
        send_resolved: true
"""

fd = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
with os.fdopen(fd, "w", encoding="utf-8") as f:
    f.write(config)

os.chmod(output, 0o600)
print("Runtime configuration created securely.")
PY
