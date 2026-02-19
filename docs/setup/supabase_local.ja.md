# ローカル Supabase 環境構築・運用手順

Docker を使用してローカルに Supabase 開発環境を構築し、運用する方法をまとめます。

## 1. 前提条件
以下のツールがインストールされている必要があります。
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)（起動していること）
- [Supabase CLI](https://supabase.com/docs/guides/cli/getting-started)

## 2. 環境の構築

### 初回セットアップ
プロジェクトのルートディレクトリで以下を実行します。

```bash
# Supabase の初期化
supabase init
```

### ローカルサーバーの起動
Docker コンテナを起動します。

```bash
# コンテナの起動（初回はイメージのダウンロードに時間がかかります）
supabase start
```

起動が完了すると、ターミナルに以下のような情報が表示されます。
- `API URL`: `http://127.0.0.1:54321`
- `anon key`: `eyJhbG...`
- `service_role key`: `eyJhbG...`
- `Studio URL`: `http://127.0.0.1:54323`（ブラウザでDBを確認できるGUI）

これらを `.env` ファイルに反映してください。

## 3. データベースの更新（マイグレーション）

### マイグレーションの適用
作成済みの `supabase/migrations/001_init.sql` をローカル環境に反映します。

```bash
# ローカルDBにマイグレーションを適用
supabase db reset
```
※ `db reset` はDBを初期化し、`migrations` フォルダ内のすべての SQL を再適用します。

### 新しいテーブルの追加手順
1. `supabase/migrations/` 内に新しい `.sql` ファイルを作成するか、既存のファイルを編集します。
2. `supabase db reset` を実行して反映します。

## 4. 日常の運用コマンド

| コマンド | 内容 |
| :--- | :--- |
| `supabase start` | ローカル環境を起動 |
| `supabase stop` | ローカル環境を停止 |
| `supabase status` | 現在の接続情報（URL/Key）を表示 |
| `supabase db reset` | DBを初期状態に戻し、マイグレーションを再実行 |

## 5. トラブルシューティング

### ポートが既に割り当てられている（port is already allocated）
他の Supabase プロジェクトが起動している場合、ポートが競合します。

**対応策：`supabase/config.toml` のポート番号を変更する**
`[api] port`, `[db] port`, `[studio] port` などの値を `54321` → `54331` のように変更して保存し、再度 `supabase start` を実行してください。

---

## 6. プロジェクトへの反映（.env）
ローカル Supabase 起動時に表示された値を `.env` に設定します。

```env
SUPABASE_URL=http://127.0.0.1:54321
SUPABASE_KEY=（表示された anon key を入力）
...
```
