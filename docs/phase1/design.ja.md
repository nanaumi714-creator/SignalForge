# Phase 1 設計書（Foundation）

## 1. 目的とスコープ
Phase 1 では、以降のフェーズ（Collector / Analyzer / API）が依存する「設定・DB・永続化I/F」の最小基盤を確立する。

### スコープ内
- `.env.example` 整備
- `config.py`（`pydantic-settings`）での設定一元化
- `supabase/migrations/001_init.sql` で初期スキーマ定義
- `db/client.py` で Supabase クライアントのシングルトン化
- `db/queries.py` で run 管理クエリ（insert / status update）実装
- 最小疎通確認（import / insert / select）

### スコープ外
- YouTube 収集ロジック
- GPT 分析ロジック
- スコア分類ロジック
- Discord 通知フォーマット

---

## 2. 設計方針

1. **設定の単一入口**
   - すべての環境変数参照は `config.py` に集中。
   - 他モジュールが `os.getenv` を直接使わない。

2. **DB操作の単一入口**
   - DBアクセスは `db/queries.py` 経由のみ。
   - 他モジュールは Supabase クライアントを直接呼ばない。

3. **失敗を握りつぶさない**
   - DB/API エラーは `try/except` で補足し、ログに文脈付きで記録。
   - 例外は必要に応じて再送出し、上位で run status を失敗に遷移可能にする。

4. **後続フェーズ互換の最小スキーマ**
   - Phase 2 以降で追加 migration を避けるため、`scout_runs / entities / snapshots / scores / pins` を初期作成。
   - `UNIQUE(platform, platform_id)` を `scout_entities` に設定。

---

## 3. コンポーネント設計

## 3.1 `.env.example`
必須キー:
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `OPENAI_API_KEY`
- `OPENAI_MODEL`（default: `gpt-4o-mini`）
- `YOUTUBE_API_KEY`
- `DISCORD_WEBHOOK_URL`
- `HOT_THRESHOLD`（default: `85`）
- `BATCH_SIZE`（default: `5`）

**設計意図**
- ローカル起動時の設定漏れを初期段階で可視化。
- CI/デプロイ時の環境変数契約を固定化。

## 3.2 `config.py`

### 推奨構成
- `Settings(BaseSettings)`
- 型付きフィールド（`str`, `int`, `AnyUrl` など）
- `model_config = SettingsConfigDict(env_file=".env", extra="ignore")`
- `@lru_cache` 付き `get_settings()`

### 設計意図
- 設定読み込みの都度パースを回避（キャッシュ）。
- 型で不正値を早期検出。

## 3.3 `supabase/migrations/001_init.sql`

### テーブル（最小）
1. `scout_runs`
   - run 実行単位（manual / scheduled）
   - status（running / success / failed）
   - summary JSON

2. `scout_entities`
   - 候補チャンネルのマスタ
   - `UNIQUE(platform, platform_id)`

3. `scout_snapshots`
   - 収集時点のメトリクス記録

4. `scout_scores`
   - GPT/ルール評価結果

5. `scout_pins`
   - 人手ピン留め管理

### インデックス方針（初期）
- `scout_runs(created_at desc)`
- `scout_entities(platform, platform_id)`
- `scout_scores(run_id, total_score desc)`

## 3.4 `db/client.py`

### 推奨I/F
- `get_supabase_client() -> Client`
- モジュール内グローバルに遅延初期化

### 設計意図
- コネクション設定の重複回避
- テスト時のモック差し替え容易化

## 3.5 `db/queries.py`

### Phase 1 実装対象関数
- `insert_run(run_type: str, config: dict) -> str`
- `update_run_status(run_id: str, status: str, summary: dict | None = None) -> None`

### 入出力契約
- `insert_run` は UUID 文字列を返す
- `update_run_status` は成功時 `None`
- 失敗時はログ出力後に例外再送出（上位制御用）

---

## 4. シーケンス設計

1. API/Worker が `insert_run("manual", config)` 呼び出し
2. `db/queries.py` が client 取得
3. `scout_runs` に `running` で insert
4. 正常終了時 `update_run_status(..., "success", summary)`
5. 異常終了時 `update_run_status(..., "failed", {"error": ...})`

---

## 5. 実装順序（推奨）

1. `.env.example` 作成
2. `config.py` 実装
3. migration SQL 実装
4. `db/client.py` 実装
5. `db/queries.py` 実装
6. 疎通コマンドで検証

---

## 6. テスト設計

## 6.1 最低限チェック（Definition of Done）
- `python -c "from db.queries import insert_run; print(insert_run('manual', {}))"`
- `python -c "from db.queries import update_run_status; print('ok')"`
- Supabase 上で `scout_runs` の select 成功

## 6.2 推奨追加チェック
- `config.py` の必須キー欠落時に ValidationError になること
- `insert_run` 失敗時に例外再送出されること
- `update_run_status` が summary なし/あり両方で更新できること

---

## 7. リスクと対策

- **Supabase 認証情報の未設定**
  - 対策: `.env.example` を先に整備し、起動前チェックを明文化。

- **status 値の揺れ（running/success/failed 以外）**
  - 対策: DB 側 CHECK 制約またはアプリ側 enum バリデーションを導入。

- **後続フェーズでのスキーマ不足**
  - 対策: Phase 1 時点で5テーブルを作成し、nullable で拡張余地を確保。

---

## 8. 完了判定
以下を満たしたら Phase 1 完了とする。
- `.env.example` / `config.py` / `db/client.py` / `db/queries.py` / `001_init.sql` が作成済み
- DoD コマンドが通過
- `.agents/progress.md` が更新されている
