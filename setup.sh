#!/usr/bin/env bash
set -euo pipefail

if [[ ! -f .env ]]; then
  echo "Copy .env.example to .env and set POSTGRES_PASSWORD, DEMO_ADMIN_PASSWORD, and DEMO_USER_PASSWORD." >&2
  exit 1
fi
set -a
# This local configuration file is trusted shell input for the setup script.
source .env
set +a
for name in POSTGRES_PASSWORD DEMO_ADMIN_PASSWORD DEMO_USER_PASSWORD; do
  if [[ -z "${!name:-}" ]]; then
    echo "Set $name in .env before running setup." >&2
    exit 1
  fi
done

echo "=== 1. Starting Mattermost and Postgres containers ==="
docker compose up -d

echo "=== 2. Waiting for Mattermost to be ready ==="
for attempt in {1..60}; do
  if curl -fsS http://localhost:8065/api/v4/system/ping | grep -q '"status":"OK"'; then
    break
  fi
  echo "Waiting for Mattermost server..."
  sleep 3
done
curl -fsS http://localhost:8065/api/v4/system/ping | grep -q '"status":"OK"' || { echo "Mattermost did not become ready." >&2; exit 1; }

echo "=== 3. Creating Admin User and Team ==="
docker compose exec mattermost mmctl --local user create --email admin@example.com --username admin --password "$DEMO_ADMIN_PASSWORD" --system-admin || true
docker compose exec mattermost mmctl --local team create --name main-team --display-name "Main Team" --email admin@example.com || true
docker compose exec mattermost mmctl --local team users add main-team admin || true
docker compose exec mattermost mmctl --local channel users add main-team:town-square admin || true
docker compose exec mattermost mmctl --local channel users add main-team:off-topic admin || true

echo "=== 4. Setting Japanese Locale and Slack Theme ==="
docker compose exec mattermost mmctl --local config set LocalizationSettings.DefaultClientLocale "ja" || true
docker compose exec mattermost mmctl --local config set LocalizationSettings.DefaultServerLocale "ja" || true

cat apply_slack_theme.sql | docker compose exec -T postgres psql -U mmuser -d mattermost
cat update_user_prefs.sql | docker compose exec -T postgres psql -U mmuser -d mattermost

echo "=== 5. Seeding Demo Users, Channel Chats, and DMs ==="
python3 seed_data.py

echo "=== Setup Complete! ==="
echo "Access URL: http://localhost:8065 (or http://localhost:3000)"
echo "Admin Login: admin@example.com (password from your local .env)"
