import json
import time
import urllib.request

BASE_URL = "http://localhost:8065/api/v4"


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


def post_message(token, channel_id, message):
    req = urllib.request.Request(
        f"{BASE_URL}/posts",
        data=json.dumps({"channel_id": channel_id, "message": message}).encode(
            "utf-8"
        ),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
    )
    with urllib.request.urlopen(req) as res:
        return json.loads(res.read().decode("utf-8"))


def get_dm_channel(token, user_id, other_id):
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


# Adminログイン
admin_token, admin_id = login("admin", "MattermostAdmin2026!")

# 送信対象3名
users = ["tanaka", "sato", "watanabe"]
tokens = {}
user_ids = {}

for u in users:
    t, uid = login(u, "UserPassword123!")
    tokens[u] = t
    user_ids[u] = uid

# 各ユーザーのDMチャンネル取得
dm_channels = {
    u: get_dm_channel(tokens[u], user_ids[u], admin_id) for u in users
}

# --- 1. 田中 太郎 (tanaka) からの追加3件 ---
tanaka_messages = [
    "ちなみに主な相談内容としては、現状のAWSコスト削減に向けたリザーブドインスタンスの購入検討と、一部コンテナ環境の移行スケジュールについてです。",
    "事前にこちらで用意しておくべき試算シートや、確認しておいてほしい数値データなどは何かございますでしょうか？",
    "もし明日の15:00のご都合が悪ければ、16:30以降または明後日の午前中でも調整可能ですので、ご都合の良さそうな時間帯を教えていただけますと幸いです！",
]

# --- 2. 佐藤 美咲 (sato) からの追加3件 ---
sato_messages = [
    "個人的にはターゲット層（20〜30代女性）を意識すると、配色を明るくして親しみやすさを出したB案（ポップ系）の方がCTRが上がりそうかなと感じています。",
    "今回のキャンペーンで最も強くアピールしたいキャッチコピーは、『手軽に始められる点』と『コストパフォーマンス』のどちらをメインに押し出したいでしょうか？",
    "修正作業の締め切りを明日夕方に設定しているのですが、ざっくり方向性のレビューだけでも本日中にお時間いただけそうでしょうか…？",
]

# --- 3. 渡辺 彩 (watanabe) からの追加3件 ---
watanabe_messages = [
    "今回のアジェンダでは、特にQ3のロードマップ見直しと、一部機能のリバースによるスケジュール遅延への対策を重点的に議論したいと考えています。",
    "現在各チームの進捗共有に10分ずつ割り当てていますが、全体ディスカッションの時間をもう少し多め（20分程度）に確保した方がよろしいでしょうか？",
    "あと、マーケティング部からオブザーバーとして2名ほど同席したいとの要望が来ているのですが、参加許可しても問題ないでしょうか？",
]

print("=== Sending contextual DMs from Tanaka ===")
for msg in tanaka_messages:
    post_message(tokens["tanaka"], dm_channels["tanaka"], msg)
    print(f"Tanaka -> Admin: {msg}")
    time.sleep(0.8)

print("\n=== Sending contextual DMs from Sato ===")
for msg in sato_messages:
    post_message(tokens["sato"], dm_channels["sato"], msg)
    print(f"Sato -> Admin: {msg}")
    time.sleep(0.8)

print("\n=== Sending contextual DMs from Watanabe ===")
for msg in watanabe_messages:
    post_message(tokens["watanabe"], dm_channels["watanabe"], msg)
    print(f"Watanabe -> Admin: {msg}")
    time.sleep(0.8)

print("\n=== All contextual messages sent successfully! ===")
