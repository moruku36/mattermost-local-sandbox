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


# tanaka と sato でログイン
token_tanaka, _ = login("tanaka", "UserPassword123!")
token_sato, _ = login("sato", "UserPassword123!")

# 1. Town Square: kentaroにメンションしない形で呼びかける
msg_town = "kentaroさん、先ほど共有いただいた企画書の確認事項について、2点ほどご相談したい箇所があるのですが、後ほどお時間よろしいでしょうか？"
post_message(token_tanaka, TOWN_SQUARE, msg_town)
print(f"Posted to Town Square (no mention) by tanaka: {msg_town}")

time.sleep(0.8)

# 2. Off-Topic: kentaroにメンションする形でチャット
msg_off = "@kentaro 今日のランチですが、先日話していた駅前の新しいパスタ屋さんに行きませんか？何時頃出られそうでしょうか？🍝"
post_message(token_sato, OFF_TOPIC, msg_off)
print(f"Posted to Off-Topic (with mention) by sato: {msg_off}")

print("Done!")
