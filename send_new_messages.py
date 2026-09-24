import json
import time
import urllib.request

BASE_URL = "http://localhost:8065/api/v4"

TOWN_SQUARE = "rf35sxhecfdqjpfgfh91de67fw"
OFF_TOPIC = "56usekcsj7rf5ntzz1pg1j7wbh"


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


# Adminと各ユーザーのログイン
admin_token, admin_id = login("admin", "MattermostAdmin2026!")

users = ["tanaka", "sato", "suzuki", "watanabe"]
tokens = {}
user_ids = {}

for u in users:
    t, uid = login(u, "UserPassword123!")
    tokens[u] = t
    user_ids[u] = uid

print("=== Sending message to Town Square ===")
msg_town = "@admin 明日の全体定例の発表順ですが、開発チームから先に進めて問題ないでしょうか？"
post_message(tokens["tanaka"], TOWN_SQUARE, msg_town)
print(f"Posted to Town Square by tanaka: {msg_town}")
time.sleep(0.5)

print("=== Sending message to Off-Topic ===")
msg_off = "来週の金曜日に歓迎会を兼ねてオフィス近くで飲み会を企画しようと思うのですが、みなさん参加できそうな日程や希望のお店ありますか？"
post_message(tokens["suzuki"], OFF_TOPIC, msg_off)
print(f"Posted to Off-Topic by suzuki: {msg_off}")
time.sleep(0.5)

print("=== Sending DMs to Admin ===")
# 1. 田中 太郎 からのDM
dm_tanaka = get_dm_channel(tokens["tanaka"], user_ids["tanaka"], admin_id)
msg_dm_tanaka = "明日のご相談の件ですが、15:00から30分ほどお時間いただけますでしょうか？オンラインでも対面でもどちらでも大丈夫です！"
post_message(tokens["tanaka"], dm_tanaka, msg_dm_tanaka)
print(f"DM from tanaka: {msg_dm_tanaka}")
time.sleep(0.5)

# 2. 佐藤 美咲 からのDM
dm_sato = get_dm_channel(tokens["sato"], user_ids["sato"], admin_id)
msg_dm_sato = "先ほどのバナーデザイン案ですが、A案（シンプル系）とB案（ポップ系）のどちらの方向性が良さそうか、ざっくりご意見を伺えますでしょうか？"
post_message(tokens["sato"], dm_sato, msg_dm_sato)
print(f"DM from sato: {msg_dm_sato}")
time.sleep(0.5)

# 3. 渡辺 彩 からのDM
dm_watanabe = get_dm_channel(tokens["watanabe"], user_ids["watanabe"], admin_id)
msg_dm_watanabe = "進捗MTGのアジェンダDocを作成しました！事前に目を通しておいていただけると助かります。何か追加したい項目はありますでしょうか？"
post_message(tokens["watanabe"], dm_watanabe, msg_dm_watanabe)
print(f"DM from watanabe: {msg_dm_watanabe}")

print("=== All test messages sent successfully! ===")
