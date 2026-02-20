# 進捗管理（AIセッション引き継ぎ）

## 現在のフェーズ
現在: **Phase 5 / API 実装（開始前）**

## 完了済みフェーズ
- Phase 1: Foundation
- Phase 2: Collector 実装
- Phase 3: Analyzer 実装
- Phase 4: Classifier & Notifier 実装

## 現フェーズの進捗
(Phase 4 完了)
- [x] db/queries.py（get_scores_by_run / update_score_classification 追加）
- [x] worker/scorer.py（分類ロジック実装: top/hot/watch/normal）
- [x] worker/notifier.py（Discord Webhook / 分割送信 / フォーマット実装）
- [x] 仮想環境（.venv）のセットアップと検証ルール化
- [x] ユニットテスト実行（pytest tests/test_scorer.py 正常終了）

## ブロッカー
- （なし）

## 次のセッション開始時の指示
Phase 5 (API) の実装を開始してください。FastAPI を使用して、クロール結果やスコアを取得するためのエンドポイントを構築します。

## 更新ルール（AIへの指示）
フェーズ完了時・セッション終了時に必ずこのファイルを更新すること。  
更新内容：完了タスクにチェック / 現在のフェーズ更新 / ブロッカー記録。
