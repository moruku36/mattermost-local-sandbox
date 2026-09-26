@echo off
echo Starting Mattermost Docker stack...
wsl.exe -d Ubuntu-24.04 bash -c "cd '$(wslpath '%~dp0')' && docker compose up -d"
echo.
echo Mattermost is now running at http://localhost:3000/main-team/channels/ai-drafts
echo (You can close this window)
timeout /t 5
