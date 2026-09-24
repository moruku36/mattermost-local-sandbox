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
ブラウザで [http://localhost:8065](http://localhost:8065) を開き、上記の管理者アカウントでログインしてください。
