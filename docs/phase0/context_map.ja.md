# コンテキストマップ（Phase別 / Task別）

## Phase 0: AIコンテキスト整備
- Task 0-1: 用語と評価軸の固定
  - 参照: `ai_context_contract.md` (Scoring Contract)
- Task 0-2: JSON出力契約の固定
  - 参照: `ai_context_contract.md` (Structured Output)
- Task 0-3: エラーポリシーの固定
  - 参照: `ai_context_contract.md` (Error Policy)

## Phase 1: 基盤
- Task 1-1: 環境変数/設定
  - 必要コンテキスト: APIキー、バッチサイズ、しきい値
- Task 1-2: DB接続とマイグレーション
  - 必要コンテキスト: canonical entities とテーブル対応

## Phase 2: 収集
- Task 2-1: Tracked/New構成
  - 必要コンテキスト: 重複排除ルール
- Task 2-2: Snapshot保存
  - 必要コンテキスト: collector→snapshot変換仕様

## Phase 3: 分析
- Task 3-1: GPTバッチ分析
  - 必要コンテキスト: structured output, retry policy
- Task 3-2: Score保存
  - 必要コンテキスト: axis bounds, total_score derivation

## Phase 4: 分類/通知
- Task 4-1: Top/Hot/Watch分類
  - 必要コンテキスト: classification rules
- Task 4-2: Discord通知
  - 必要コンテキスト: 2000文字分割、重複表示ルール

## Phase 5: API統合
- Task 5-1: Run起動〜完了
  - 必要コンテキスト: run status lifecycle
- Task 5-2: Results返却
  - 必要コンテキスト: response schema

## Phase 6: 60件フル運用
- Task 6-1: Trend派生拡張
  - 必要コンテキスト: Trend Extraction Contract
- Task 6-2: 週次運用準備
  - 必要コンテキスト: error policy, observability
