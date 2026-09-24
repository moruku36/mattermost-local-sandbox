@echo off
echo Starting Mattermost Docker stack...
wsl.exe -d Ubuntu-24.04 -u root bash -c "cd /mnt/c/Users/kentaro/.gemini/antigravity/scratch/mattermost && docker compose up -d"
echo.
echo Mattermost is now running at http://localhost:3000/main-team/channels/ai-drafts
echo (You can close this window)
timeout /t 5
