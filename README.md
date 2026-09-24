# Mattermost Local Sandbox (Slack-Style)

Docker Compose を利用した、ローカル検証用の **Mattermost**（Slack ライク社内チャット）環境です。  
Slack 風のクラシックテーマ（Aubergine / 茄子紫）、日本語ロケール、折りたたみスレッド（Collapsed Reply Threads）を適用し、5 名の擬似ユーザーによるチャンネル投稿および管理者宛てダイレクトメッセージ（DM）のシードデータが投入された状態を再現しています。

---

## 構成概要

- **Mattermost Team Edition**: 最新版公式コンテナ（`mattermost/mattermost-team-edition:latest`）
- **PostgreSQL 16**: 公式コンテナ（`postgres:16-alpine`）
- **ポートマッピング**: 
  - `http://localhost:8065`（メインポート）
  - `http://localhost:3000`（サブポート・フォワード）
- **永続化**: Docker Named Volume による DB・設定・添付データの安全な永続化

---

## 実装・カスタマイズ内容

1. **Slack クラシックテーマ（Aubergine）適用**
   - サイドバーを Slack 標準の濃い紫（`#3F0E40`）に設定し、UI を Slack 風に統一（`apply_slack_theme.sql`）。
2. **日本語ロケール & 表示最適化**
   - デフォルトクライアント・サーバーロケールを「日本語（ja）」に設定。
   - 画面幅全体を使うフルワイド表示を有効化（`update_user_prefs.sql`）。
3. **Slack 同等のスレッド表示（Collapsed Reply Threads）**
   - メッセージの返信が右側サイドペインに展開され、左サイドバーに「スレッド」メニューが表示されるモード（常時有効）。
4. **擬似利用環境（デモデータ投入）**
   - 5 名の擬似ユーザー（開発リーダー、デザイナー、フロントエンド、QA、PM）を自動生成。
   - `Town Square`（業務連絡・10 件）および `Off-Topic`（ランチ・機材雑談・9 件）の会話履歴を自動投入。
   - 管理者（`admin`）宛てのダイレクトメッセージ（DM・3 件）を事前送信（`seed_data.py`）。

---

## アカウント認証情報

### 管理者（自分）
- **ユーザー名 / メールアドレス**: `admin` / `admin@example.com`
- **パスワード**: `MattermostAdmin2026!`
- **権限**: システム管理者（System Admin）
- **初期チーム**: `Main Team`

### デモユーザー（5 名）
| ユーザー名 | 表示名 | 役職 / ロール | メールアドレス | パスワード |
| :--- | :--- | :--- | :--- | :--- |
| `tanaka` | 田中 太郎 | 開発リーダー | `tanaka@example.com` | `UserPassword123!` |
| `sato` | 佐藤 美咲 | デザイナー | `sato@example.com` | `UserPassword123!` |
| `suzuki` | 鈴木 一郎 | フロントエンド | `suzuki@example.com` | `UserPassword123!` |
| `takahashi` | 高橋 健太 | QA・テスター | `takahashi@example.com` | `UserPassword123!` |
| `watanabe` | 渡辺 彩 | プロダクトマネージャー | `watanabe@example.com` | `UserPassword123!` |

---

## クイックスタート手順

### 1. 起動（初回または再セットアップ）
```bash
# スクリプトによる一括起動＆シードデータ投入
bash setup.sh
```

### 2. 通常のコンテナ起動・停止
```bash
# 起動
docker compose up -d

# 停止
docker compose down
```

### 3. ブラウザでアクセス
ブラウザで [http://localhost:3000/main-team/channels/ai-drafts](http://localhost:3000/main-team/channels/ai-drafts)（または [http://localhost:8065](http://localhost:8065)）を開き、上記の管理者アカウントでログインしてください。

---

## Windows自動起動・常駐設定

PC起動時にMattermost環境が自動的にバックグラウンド起動するよう、Windowsスタートアップフォルダにスクリプトを登録しています。
- **スタートアップ登録場所**: `shell:startup`（`start_mattermost.vbs`）
- **手動起動用スクリプト**:
  - `start.bat`: ダブルクリックで起動確認できるバッチスクリプト
  - `start_silent.vbs`: 黒い画面を出さずにバックグラウンド起動するVBScript

---

## AI返信案アシスタント（ローカルLLM）

新着のMattermost投稿を監視し、ローカルのOllamaで返信案を作成して、本人とBotだけが参加する非公開 `ai-drafts` チャンネルへ投稿します。Town SquareとOff-Topicは設定例に含まれています。**元のチャンネルやDMへ返信を送る機能はありません**。内容を確認・編集して、返信は人間が元の投稿へ手動で送信します。

メッセージ本文はMattermost APIからこのPC上のプロセスへ渡り、Ollama（既定 `qwen2.5:14b`）で処理されます。外部LLMへは送信しません。監視対象は `.env` の `WATCH_CHANNELS` と `WATCH_DM_CHANNEL_IDS` で明示したものだけです。各チャンネルでBotが読める必要があります。起動時点より前の投稿は既読扱いになり、返信案は作られません。

### 初回設定

1. 管理者がMattermostのBotアカウント作成を有効にし、専用Botアカウントを作成します。作成時に表示されるBot access tokenを控えます。Botに管理者権限や全チャンネル投稿権限を付けず、対象のチャンネルと`ai-drafts`だけに参加させます。
2. Mattermostに非公開 `ai-drafts` チャンネルを作成し、自分と専用Botだけを参加させます。
3. `.env.example` を `.env` にコピーし、Botトークンを `MATTERMOST_BOT_TOKEN` に設定します。`MATTERMOST_URL` はブラウザーで開いている方に合わせます（`http://localhost:3000` または `http://localhost:8065`）。`.env` と会話文脈・処理状態ファイルはGit管理外です。
4. Ollamaをインストールして起動し、モデルを取得します（例: `ollama pull qwen2.5:14b`）。モデル変更は `OLLAMA_MODEL` で行えます。Pythonの追加パッケージは不要です。

### 起動

```powershell
Copy-Item .env.example .env
# .env の MATTERMOST_BOT_TOKEN を編集
python .\reply_drafter.py
```

初回起動では現在ある投稿を監視済みにし、それ以降の新着だけを処理します。監視対象を増やすときは `WATCH_CHANNELS` に `team-slug:channel-slug` をカンマ区切りで指定し、各チャンネルへBotを参加させてからプロセスを再起動します。状態ファイルには重複防止用の投稿IDのみを保存します。停止は `Ctrl+C` です。Mattermost停止後はMattermostを起動し直し、同じコマンドでこのプロセスも起動します。

### DMの返信案

DMも返信案を作れますが、Botが参加しているDMだけが対象です。管理者宛ての既存1対1 DMにBotを追加すると、相手にもBotが参加者として見える新しいグループDMになります。元の1対1 DMは監視できず、既存の履歴もグループDMには引き継がれません。相手と共有することを確認してから、Mattermost上で新しいグループDMを作成してください。

追加後、`python .\reply_drafter.py --list-dms` を実行すると、Botが現在参加しているDMの相手とチャンネルIDを表示します。対象のIDだけを `.env` の `WATCH_DM_CHANNEL_IDS` に指定します。複数指定はカンマ区切りです。Botが参加しているDMのうち、ここに明記したIDだけを監視します。DM内の直近の会話を文脈に含め、返信案は引き続き `ai-drafts` に投稿します。新しいDMを監視対象に加えた初回起動では、既存投稿を読み取り済みにして、その後の新着から返信案を作ります。

`WATCH_DM_CHANNEL_IDS` を空欄にするとDMは監視しません。監視を始める際はプロセスを再起動してください。

Mattermostでは既存の1対1 DMへ新しい参加者を加えると、履歴のない新しいグループDMが作られます。旧DMの文脈も必要な場合は、対象を選んで `data/reply-drafter-context.json` にグループDMチャンネルIDをキーとして保存すると、返信案の文脈に加えられます。このファイルはGit管理外で、読み込んだ投稿文はローカルOllamaだけに渡ります。個人DMの内容を共有する際は、必ず参加者の同意を得てください。

### 設定項目

| 変数 | 用途 | 既定値 |
|---|---|---|
| `MATTERMOST_URL` | Mattermost APIのURL | `http://localhost:3000` |
| `MATTERMOST_BOT_TOKEN` | 専用Botのアクセストークン | 必須 |
| `WATCH_CHANNELS` | 監視する公開・非公開チャンネル | `main-team:town-square,main-team:off-topic` |
| `WATCH_DM_CHANNEL_IDS` | 監視を許可するDM IDの一覧 | 空（DM監視なし） |
| `DRAFTS_CHANNEL` | 下書き出力先 | `main-team:ai-drafts` |
| `OLLAMA_URL` / `OLLAMA_MODEL` | ローカルLLMの接続先・モデル | `http://127.0.0.1:11434` / `qwen2.5:14b` |
| `POLL_SECONDS` / `CONTEXT_POSTS` | 確認間隔・プロンプトに含める文脈数 | `5` / `8` |

`.env` のサンプルは `.env.example` を参照してください。BotのDM一覧は `python .\reply_drafter.py --list-dms` で確認できます。

