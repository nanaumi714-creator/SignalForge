# SignalForge (SCOUT SYSTEM)

SignalForge は、YouTube のデータを自動収集し、AI（OpenAI）を活用して定性・定量分析を行うことで、有望な海外クリエイターを発掘・評価する AI 駆動型スカウト支援システムです。

## 🚀 主な機能

### 1. ハイブリッド・データ収集 (Hybrid 60)
- **追跡収集**: 登録済みの特定チャンネルの詳細データを定期取得。
- **キーワード探索**: 指定したキーワードから関連チャンネルを自動発見。

### 2. AI 駆動型分析 & スコアリング
- **OpenAI 連携**: 登録者数、再生数、投稿頻度に加え、最新の動画タイトル（通常・ライブ・ショート）からクリエイターの企画力や戦略を LLM が深く分析。
- **分析モード**:
  - `smart`: 有望な候補のみを精密分析。
  - `aggregated`: 複数チャンネルを一度に分析し、上位を抽出（低コスト）。**デフォルト。**
  - `full`: 全対象を精密分析。

### 3. スマート・フィルタリング
- 登録者数（例: 500人以上）やアクティビティ、過去の評価履歴に基づき、分析対象を自動で選別。無駄な API コストを削減します。

### 4. WEBディスカバリー
- OpenAI の検索機能を利用し、YouTube 外部のトレンドから注目クリエイターを自動発掘。

## 🛠 セットアップ

### 必要条件
- Python 3.11+
- Supabase (データベースとして利用)
- 各種 API キー (OpenAI, YouTube Data API v3)

### インストール
1. リポジトリをクローン:
   ```bash
   git clone https://github.com/nanaumi714-creator/SignalForge.git
   cd SignalForge
   ```

2. 仮想環境の作成と依存関係のインストール:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

3. 環境変数の設定:
   `.env.example` を `.env` にコピーし、必要な API キーを設定してください。

4. サーバー起動:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

## 🔑 認証

全ての API エンドポイントには `X-API-KEY` ヘッダーが必要です。

```
X-API-KEY: <.env の SCOUT_API_KEY に設定した値>
```

## 📖 使い方

### CLI からのスカウト実行
```bash
python main.py run --mode smart
```
`--mode` で `smart`, `aggregated`, `full` を選択可能です。

### API からのスカウト実行

#### Bash
```bash
curl -X POST http://localhost:8000/v1/scout/runs \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: your_api_key" \
  -d '{"run_type":"manual","notify_discord":false}'
```

#### PowerShell
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/v1/scout/runs" `
  -Method Post `
  -Headers @{ "Content-Type" = "application/json"; "X-API-KEY" = "your_api_key" } `
  -Body '{"run_type":"manual","notify_discord":false}'
```

## 📡 API リファレンス

### `POST /v1/scout/runs` — スカウト実行

新しいスカウトランを非同期で開始します。

#### Request Body

| パラメータ | 型 | デフォルト | 説明 |
|---|---|---|---|
| `run_type` | `string` | `"manual"` | 実行種別。`manual` または `scheduled` |
| `analysis_mode` | `string` | `"aggregated"` | 分析モード。`smart` / `aggregated` / `full` |
| `notify_discord` | `boolean` | `true` | Discord への通知を行うか |
| `config` | `object` | `{}` | 追加設定（例: `{"keywords": ["VTuber", "Cover"]}` ） |

#### Response

```json
{
  "run_id": "uuid-string",
  "status": "running"
}
```

#### リクエスト例

```json
// デフォルト（aggregated モード、Discord 通知あり）
{"run_type": "manual"}

// Smart モードで Discord 通知なし
{"run_type": "manual", "analysis_mode": "smart", "notify_discord": false}

// キーワード指定 + Full モード
{"run_type": "manual", "analysis_mode": "full", "config": {"keywords": ["VTuber", "Cover", "Singer"]}}
```

---

### `GET /v1/scout/runs/{run_id}` — ステータス確認

実行中・完了済みのランのステータスとサマリを取得します。

#### Response

| フィールド | 型 | 説明 |
|---|---|---|
| `run_id` | `string` | ランID |
| `status` | `string` | `running` / `success` / `failed` |
| `summary` | `object \| null` | 完了時のサマリ情報 |
| `started_at` | `string \| null` | 開始日時 |
| `finished_at` | `string \| null` | 終了日時 |

---

### `POST /v1/scout/pins` — ピン追加

クリエイターをピン（手動マーク）します。ピンされたクリエイターは次回以降の追跡対象に含まれます。

#### Request Body

| パラメータ | 型 | 必須 | 説明 |
|---|---|---|---|
| `entity_id` | `string` | ✅ | 対象エンティティのUUID |
| `note` | `string` | - | メモ |
| `pinned_by` | `string` | - | ピンした人 |

---

### `GET /v1/scout/pins` — ピン一覧

全てのピン済みエンティティを取得します。

---

### `DELETE /v1/scout/pins/{entity_id}` — ピン解除

指定したエンティティのピンを解除します。

---

### `POST /v1/scout/commands` — コマンド実行

スラッシュコマンド形式で操作を実行します。

#### Request Body

| パラメータ | 型 | 必須 | 説明 |
|---|---|---|---|
| `text` | `string` | ✅ | コマンド文字列（例: `/scout run VTuber Cover`） |

## ⚙️ 設定のカスタマイズ (.env)

| 変数名 | デフォルト | 説明 |
|---|---|---|
| `ANALYSIS_MODE` | `aggregated` | デフォルトの分析モード |
| `MIN_SUBSCRIBERS` | `500` | 分析対象とする最小登録者数 |
| `MIN_UPLOAD_FREQ_DAYS` | `30` | 非アクティブ判定の日数 |
| `RE_ANALYZE_DAYS` | `30` | 再分析までの日数 |
| `DISCOVERY_ENABLED` | `false` | Web探索機能を有効にするか |
| `HOT_THRESHOLD` | `85` | HOT判定のスコア閾値 |
| `BATCH_SIZE` | `5` | GPT呼び出しのバッチサイズ |

## 📁 ディレクトリ構造
- `api/`: FastAPI エンドポイント（runs, pins, commands）
- `worker/`: 収集、分析、通知、探索を担当するコアロジック。
- `db/`: Supabase への問い合わせロジック。
- `models/`: データ定義 (Pydantic スキーマ)。
- `tests/`: ユニットテスト。
- `docs/`: 各フェーズの要件定義および設計書。

---
*SignalForge は AI との対話を通じて継続的に進化しています。詳細は `.agents/progress.md` をご確認ください。*
