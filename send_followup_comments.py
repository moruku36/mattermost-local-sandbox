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

users = ["tanaka", "sato", "suzuki", "takahashi", "watanabe"]
tokens = {}
user_ids = {}

for u in users:
    t, uid = login(u, "UserPassword123!")
    tokens[u] = t
    user_ids[u] = uid

print("=== 1. Town Square ===")
msg_town = "ご快諾ありがとうございます！それでは開発チームトップバッターで準備進めます。発表時間は質疑含めて15分程度を予定しています！"
post_message(tokens["tanaka"], TOWN_SQUARE, msg_town)
print(f"Town Square [tanaka]: {msg_town}")
time.sleep(0.5)

print("\n=== 2. Off-Topic ===")
msg_off = "企画ありがとうございます！金曜なら今のところ空いてるので参加したいです。お店は駅前のクラフトビールがあるイタリアンとかどうでしょう？🍺"
post_message(tokens["takahashi"], OFF_TOPIC, msg_off)
print(f"Off-Topic [takahashi]: {msg_off}")
time.sleep(0.5)

print("\n=== 3. DM: Tanaka ===")
dm_tanaka = get_dm_channel(tokens["tanaka"], user_ids["tanaka"], admin_id)
msg_dm_tanaka = "急ぎではないので、もし今週スケジュールがタイトでしたら来週月曜の週次定例の前後でも大丈夫ですので、無理のない範囲でご検討ください！"
post_message(tokens["tanaka"], dm_tanaka, msg_dm_tanaka)
print(f"DM [tanaka]: {msg_dm_tanaka}")
time.sleep(0.5)

print("\n=== 4. DM: Sato ===")
dm_sato = get_dm_channel(tokens["sato"], user_ids["sato"], admin_id)
msg_dm_sato = "あ、もしお忙しければ、デザインURLに直接コメント残していただくだけでも全然問題ありませんので、よろしくお願いします！🙇‍♀️"
post_message(tokens["sato"], dm_sato, msg_dm_sato)
print(f"DM [sato]: {msg_dm_sato}")
time.sleep(0.5)

print("\n=== 5. DM: Watanabe ===")
dm_watanabe = get_dm_channel(tokens["watanabe"], user_ids["watanabe"], admin_id)
msg_dm_watanabe = "マーケ側からは『今後のプロモーション連携のために開発の進捗感を把握しておきたい』とのことでした。念のため補足共有でした！"
post_message(tokens["watanabe"], dm_watanabe, msg_dm_watanabe)
print(f"DM [watanabe]: {msg_dm_watanabe}")

print("\n=== All follow-up comments sent successfully! ===")
