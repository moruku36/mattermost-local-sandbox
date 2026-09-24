import json
import urllib.request

BASE_URL = "http://localhost:8065/api/v4"
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
    payload = {"channel_id": channel_id, "message": message}
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


# watanabe でログイン
token_watanabe, _ = login("watanabe", "UserPassword123!")

# Off-Topic に kentaro メンションなしでメッセージ送信
message = "kentaroさん、先ほど淹れていただいたオフィスのコーヒー豆の銘柄って何でしたっけ？すごく香りが良くて美味しかったので、自宅用にも買おうと思っていて！☕"

res = post_message(token_watanabe, OFF_TOPIC, message)
print(f"Posted to Off-Topic without mention! Post ID: {res['id']}")
print(f"Message: {res['message']}")
