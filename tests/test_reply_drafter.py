import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import reply_drafter as drafter


class PollingTests(unittest.TestCase):
    def test_draft_is_posted_only_to_private_channel(self):
        post = {"id": "source", "message": "hello", "root_id": ""}
        source = {"id": "source-channel", "team_name": "main-team", "name": "town-square", "type": "O"}
        drafts = {"id": "private-channel", "team_name": "main-team", "name": "ai-drafts", "type": "P"}
        with patch.object(drafter, "generate_reply", return_value="draft"), patch.object(drafter, "api_json") as api:
            drafter.create_draft("http://localhost", "token", "ollama", "model", "instructions", "http://localhost", "", "low", 800, post, [], source, drafts)
        self.assertEqual(api.call_count, 1)
        self.assertEqual(api.call_args.args[2:4], ("POST", "/posts"))
        self.assertEqual(api.call_args.args[4]["channel_id"], "private-channel")

    def test_pages_back_past_one_hundred_posts(self):
        posts = [{"id": str(i), "create_at": i, "message": f"message {i}", "user_id": "user"} for i in range(1, 152)]

        def fake_api(_base, _token, method, path, _payload=None):
            self.assertEqual(method, "GET")
            page = int(path.split("page=")[1].split("&")[0])
            batch = list(reversed(posts))[page * 100:(page + 1) * 100]
            return {"posts": {p["id"]: p for p in batch}}

        with patch.object(drafter, "api_json", side_effect=fake_api):
            result = drafter.get_recent_posts("http://localhost", "token", "channel", (1, "1"))
        self.assertEqual(len(result), 150)
        self.assertEqual(result[0]["id"], "2")
        self.assertEqual(result[-1]["id"], "151")

    def test_failed_draft_retries_without_advancing_cursor(self):
        posts = [{"id": "a", "create_at": 1, "message": "request", "user_id": "user"}]
        channel = {"id": "watched", "name": "town-square"}
        drafts = {"id": "drafts", "name": "ai-drafts"}
        state = {"channels": {"watched": {"initialized": True, "seen_ids": [], "cursor": [0, ""]}}}
        args = ("http://localhost", "token", "bot", "ollama", "model", "instructions", "http://localhost", "", "low", 800, channel, drafts, state, {})
        with tempfile.TemporaryDirectory() as tmp, patch.object(drafter, "STATE_FILE", Path(tmp) / "state.json"), patch.object(drafter, "get_recent_posts", return_value=posts), patch.object(drafter, "create_draft", side_effect=[RuntimeError("offline"), None]) as create:
            drafter.poll_channel(*args)
            self.assertEqual(state["channels"]["watched"]["cursor"], [0, ""])
            drafter.poll_channel(*args)
            self.assertEqual(state["channels"]["watched"]["cursor"], [1, "a"])
            self.assertEqual(create.call_count, 2)


if __name__ == "__main__":
    unittest.main()
