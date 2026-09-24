import json
import urllib.request

BASE_URL = "http://localhost:8065/api/v4"
TOWN_SQUARE = "rf35sxhecfdqjpfgfh91de67fw"
ROOT_POST_ID = "7yhfj47zwtrkjcfqkpjhkwzh7o"


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


def post_reply(token, channel_id, root_id, message):
    payload = {"channel_id": channel_id, "root_id": root_id, "message": message}
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


# tanaka でログイン
token_tanaka, _ = login("tanaka", "UserPassword123!")

# スレッド返信（@kentaro メンション付き）
reply_message = "@kentaro ご確認ありがとうございます！具体的には『第2フェーズの開発スコープの優先順位』と『外部API連携におけるセキュリティ要件』の2点になります。特に後者は準備が必要かと思いますので、事前にドキュメントをスレッドに共有しておきますね！"

res = post_reply(token_tanaka, TOWN_SQUARE, ROOT_POST_ID, reply_message)
print(f"Reply posted successfully! Post ID: {res['id']}")
print(f"Message: {res['message']}")
