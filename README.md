# SignalForge (SCOUT SYSTEM)

SignalForge は、YouTube のデータを自動収集し、AI（OpenAI）を活用して定性・定量分析を行うことで、有望な海外クリエイターを発掘・評価する AI 駆動型スカウト支援システムです。

## 🚀 主な機能

### 1. ハイブリッド・データ収集 (Hybrid 60)
- **追跡収集**: 登録済みの特定チャンネルの詳細データを定期取得。
- **キーワード探索**: 指定したキーワードから関連チャンネルを自動発見。

### 2. AI 駆動型分析 & スコアリング
- **OpenAI 連携**: 登録者数、再生数、投稿頻度に加え、最新の動画タイトル（通常・ライブ・ショート）からクリエイターの企画力や戦略を LLM が深く分析。
- **分析モード**:
  - `Smart`: 有望な候補のみを精密分析。
  - `Aggregated`: 複数チャンネルを一度に分析し、上位を抽出（低コスト）。
  - `Full`: 全対象を精密分析。

### 3. スマート・フィルタリング
- 登録者数（例: 500人以上）やアクティビティ、過去の評価履歴に基づき、分析対象を自動で選別。無駄な API コストを削減します。

### 4. WEBディスカバリー (Phase 10)
- OpenAI の検索機能を利用し、YouTube 外部のトレンドから注目クリエイターを自動発掘。

## 🛠 セットアップ

### 必要条件
- Python 3.10+
- Supabase (データベースとして利用)
- 各種 API キー (OpenAI, YouTube Data API v3, [Tavily ※オプション])

### インストール
1. リポジトリをクローン:
   ```bash
   git clone https://github.com/nanaumi714-creator/SignalForge.git
   cd SignalForge
   ```

2. 仮想環境の作成と依存関係のインストール:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

3. 環境変数の設定:
   `.env.example` を `.env` にコピーし、必要な API キーを設定してください。

## 📖 使い方

### スカウト実行 (CLI)
```bash
python main.py run --mode smart
```
`--mode` で `smart`, `aggregated`, `full` を選択可能です。

### 設定のカスタマイズ (.env)
- `MIN_SUBSCRIBERS`: 分析対象とする最小登録者数。
- `ANALYSIS_MODE`: デフォルトの分析モード。
- `DISCOVERY_ENABLED`: Web探索機能を有効にするか (true/false)。

## 📁 ディレクトリ構造
- `worker/`: 収集、分析、通知、探索を担当するコアロジック。
- `db/`: Supabase への問い合わせロジック。
- `models/`: データ定義 (Pydantic スキーマ)。
- `tests/`: ユニットテスト。
- `docs/`: 各フェーズの要件定義および設計書。

---
*SignalForge は AI との対話を通じて継続的に進化しています。詳細は `.agents/progress.md` をご確認ください。*
