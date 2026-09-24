-- 日本語ロケール設定
UPDATE users SET locale = 'ja' WHERE username = 'admin';

-- 表示設定（全幅表示）
INSERT INTO preferences (userid, category, name, value)
SELECT id, 'display_settings', 'channel_display_mode', 'full' FROM users WHERE username = 'admin'
ON CONFLICT (userid, category, name) DO UPDATE SET value = EXCLUDED.value;
