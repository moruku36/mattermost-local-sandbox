#!/usr/bin/env bash
set -e

echo "=== 1. Starting Mattermost and Postgres containers ==="
docker compose up -d

echo "=== 2. Waiting for Mattermost to be ready ==="
until curl -s http://localhost:8065/api/v4/system/ping | grep -q '"status":"OK"'; do
  echo "Waiting for Mattermost server..."
  sleep 3
done

echo "=== 3. Creating Admin User and Team ==="
docker compose exec mattermost mmctl --local user create --email admin@example.com --username admin --password "MattermostAdmin2026!" --system-admin || true
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
echo "Admin Login: admin@example.com / MattermostAdmin2026!"
