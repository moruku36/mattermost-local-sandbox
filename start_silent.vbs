Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "wsl.exe -d Ubuntu-24.04 -u root bash -c ""cd /mnt/c/Users/kentaro/.gemini/antigravity/scratch/mattermost && docker compose up -d && sleep infinity""", 0, False
