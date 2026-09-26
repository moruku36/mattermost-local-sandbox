import json
import os
import subprocess
import time
import urllib.request
from urllib.parse import quote

ADMIN_PASSWORD = os.environ.get("DEMO_ADMIN_PASSWORD", "")
USER_PASSWORD = os.environ.get("DEMO_USER_PASSWORD", "")
if not ADMIN_PASSWORD or not USER_PASSWORD:
    raise SystemExit("Set DEMO_ADMIN_PASSWORD and DEMO_USER_PASSWORD before seeding.")

USERS = [
    {
        "username": "tanaka",
        "email": "tanaka@example.com",
        "password": USER_PASSWORD,
        "firstname": "太郎",
        "lastname": "田中",
        "nickname": "タナカ",
    },
    {
        "username": "sato",
        "email": "sato@example.com",
        "password": USER_PASSWORD,
        "firstname": "美咲",
        "lastname": "佐藤",
        "nickname": "サトウ",
    },
    {
        "username": "suzuki",
        "email": "suzuki@example.com",
        "password": USER_PASSWORD,
        "firstname": "一郎",
        "lastname": "鈴木",
        "nickname": "スズキ",
    },
    {
        "username": "takahashi",
        "email": "takahashi@example.com",
        "password": USER_PASSWORD,
        "firstname": "健太",
        "lastname": "高橋",
        "nickname": "タカハシ",
    },
    {
        "username": "watanabe",
        "email": "watanabe@example.com",
        "password": USER_PASSWORD,
        "firstname": "彩",
        "lastname": "渡辺",
        "nickname": "ワタナベ",
    },
]

# 1. mmctl でユーザー作成とチーム・チャンネル追加
for u in USERS:
    # ユーザー作成
    subprocess.run(
        ["docker", "compose", "exec", "-T", "mattermost", "mmctl", "--local", "user", "create",
         "--email", u["email"], "--username", u["username"], "--password", u["password"],
         "--firstname", u["firstname"], "--lastname", u["lastname"]],
        check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )

    # チーム追加
    subprocess.run(
        ["docker", "compose", "exec", "-T", "mattermost", "mmctl", "--local", "team", "users", "add", "main-team", u["username"]],
        check=False,
    )
    # チャンネル追加
    subprocess.run(
        ["docker", "compose", "exec", "-T", "mattermost", "mmctl", "--local", "channel", "users", "add", "main-team:town-square", u["username"]],
        check=False,
    )
    subprocess.run(
        ["docker", "compose", "exec", "-T", "mattermost", "mmctl", "--local", "channel", "users", "add", "main-team:off-topic", u["username"]],
        check=False,
    )

print("Users created and added to channels.")

BASE_URL = "http://localhost:8065/api/v4"


def get_json(token, path):
    req = urllib.request.Request(
        f"{BASE_URL}{path}", headers={"Authorization": f"Bearer {token}"}
    )
    with urllib.request.urlopen(req) as res:
        return json.load(res)


def channel_id(token, team_name, channel_name):
    team = get_json(token, f"/teams/name/{quote(team_name)}")
    channel = get_json(token, f"/teams/{team['id']}/channels/name/{quote(channel_name)}")
    return channel["id"]


def existing_messages(token, channel_id):
    messages = set()
    page = 0
    while True:
        result = get_json(token, f"/channels/{channel_id}/posts?page={page}&per_page=200")
        batch = list(result["posts"].values())
        messages.update((p["user_id"], p["message"]) for p in batch)
        if len(batch) < 200:
            return messages
        page += 1


def post_once(token, user_id, channel_id, message, existing):
    key = (user_id, message)
    if key not in existing:
        post_message(token, channel_id, message)
        existing.add(key)
        time.sleep(0.3)


def login(username, password):
    req = urllib.request.Request(
        f"{BASE_URL}/users/login",
        data=json.dumps({"login_id": username, "password": password}).encode(
            "utf-8"
        ),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as res:
        token = res.headers.get("Token")
        data = json.loads(res.read().decode("utf-8"))
        return token, data["id"]


def post_message(token, channel_id, message, root_id=None):
    payload = {"channel_id": channel_id, "message": message}
    if root_id:
        payload["root_id"] = root_id
    req = urllib.request.Request(
        f"{BASE_URL}/posts",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
    )
    with urllib.request.urlopen(req) as res:
        return json.loads(res.read().decode("utf-8"))


def create_dm_channel(token, user_id, other_id):
    req = urllib.request.Request(
        f"{BASE_URL}/channels/direct",
        data=json.dumps([user_id, other_id]).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
    )
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read().decode("utf-8"))
        return data["id"]


# 各ユーザーのトークンとIDを取得
tokens = {}
user_ids = {}
for u in USERS:
    t, uid = login(u["username"], u["password"])
    tokens[u["username"]] = t
    user_ids[u["username"]] = uid

# AdminのIDを取得
admin_token, admin_id = login("admin", ADMIN_PASSWORD)

# チャンネルID
TOWN_SQUARE = channel_id(admin_token, "main-team", "town-square")
OFF_TOPIC = channel_id(admin_token, "main-team", "off-topic")
town_existing = existing_messages(admin_token, TOWN_SQUARE)
off_existing = existing_messages(admin_token, OFF_TOPIC)

# --- Town Square 投稿 ---
town_square_posts = [
    (
        "watanabe",
        "みなさん、今週もお疲れ様です！本日の全社ミーティングの資料を共有ドライブに格納しました。確認をお願いします。",
    ),
    ("tanaka", "共有ありがとうございます！確認しておきます。"),
    (
        "suzuki",
        "資料確認しました。開発側のスライドについて1点だけ補足を入れておきました。",
    ),
    (
        "watanabe",
        "@suzuki 迅速な対応ありがとうございます！助かります。",
    ),
    (
        "takahashi",
        "本日のステージング環境デプロイ、先ほど完了しました。テスト開始可能です。",
    ),
    (
        "tanaka",
        "了解です。新機能のE2Eテスト結果、後ほどレポートください。",
    ),
    ("takahashi", "承知いたしました！夕方までにまとめます。"),
    (
        "sato",
        "新しいUIコンポーネントのデザインガイドラインをFigmaに反映しました。気になる点があればいつでもコメントください！",
    ),
    (
        "suzuki",
        "@sato デザイン見ました！カラーパレットがかなり見やすくなってますね。",
    ),
    ("sato", "ありがとうございます！フィードバックお待ちしています〜"),
]

print("Posting to town-square...")
for username, msg in town_square_posts:
    post_once(tokens[username], user_ids[username], TOWN_SQUARE, msg, town_existing)

# --- Off-Topic 投稿 ---
off_topic_posts = [
    (
        "sato",
        "今日のランチ、オフィスの近くに新しくできたカレー屋さんに行ってきたんですがすごく美味しかったですよ！🍛",
    ),
    (
        "tanaka",
        "あそこのお店気になってたんですよね。ナンはおかわり自由でした？",
    ),
    ("sato", "はい！焼きたてで大きくて最高でした！"),
    ("watanabe", "今度チームみんなで行きましょう〜"),
    ("suzuki", "カレーいいですね！明日のランチ候補にします😋"),
    (
        "takahashi",
        "最近キーボードを新調したんですが、打鍵感が良すぎて仕事のモチベーション上がってます笑",
    ),
    ("tanaka", "メカニカルですか？何軸にしました？"),
    (
        "takahashi",
        "静音赤軸にしました！オフィスでも音が静かで快適です。",
    ),
    ("suzuki", "静音赤軸は鉄板ですね〜自分も買い替え検討中です。"),
]

print("Posting to off-topic...")
for username, msg in off_topic_posts:
    post_once(tokens[username], user_ids[username], OFF_TOPIC, msg, off_existing)

# --- Admin宛て ダイレクトメッセージ (DM) ---
dms = [
    (
        "tanaka",
        "adminさん、お疲れ様です！来期のインフラ構成について少しご相談したいのですが、明日の午後お時間よろしいでしょうか？",
    ),
    (
        "sato",
        "お疲れ様です！先ほど依頼いただいたバナーデザインのラフを作成しました。お時間のある時にご確認いただけますと幸いです！🎨",
    ),
    (
        "watanabe",
        "こんにちは！今週の進捗MTGのアジェンダをまとめておきました。後ほどリンクを送りますね。",
    ),
]

print("Sending DMs to admin...")
for username, msg in dms:
    dm_chan = create_dm_channel(tokens[username], user_ids[username], admin_id)
    post_once(tokens[username], user_ids[username], dm_chan, msg, existing_messages(tokens[username], dm_chan))

print("Seed completed successfully!")
