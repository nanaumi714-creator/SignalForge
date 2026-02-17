# Phase 5: API Integration

## 目的
全APIエンドポイントを実装し、`POST /v1/scout/runs` 1回で収集→分析→分類→通知を完走可能にする。

## 完了条件
- `curl` で `POST /v1/scout/runs` を実行すると run が完走し、Discord通知が届く

## タスクリスト
- [ ] 1. `worker/orchestrator.py` の実装
  - `run_scout(run_id, config, notify_discord) -> None`
  - 処理順:
    1) Tracked構成
    2) 収集
    3) snapshot保存
    4) GPT分析
    5) score保存
    6) 分類
    7) トレンド抽出
    8) Discord通知
    9) run完了更新
  - 例外時も run を `error` ステータスで完了させる

- [ ] 2. `api/runs.py` の実装
  - `POST /v1/scout/runs -> RunResponse`
  - `GET /v1/scout/runs/{run_id} -> RunStatusResponse`
  - `GET /v1/scout/runs/{run_id}/results -> RunResultsResponse`

- [ ] 3. `api/pins.py` の実装
  - `POST /v1/scout/pins -> PinResponse`
  - `DELETE /v1/scout/pins/{entity_id} -> 204`

- [ ] 4. `api/commands.py` の実装
  - `POST /v1/scout/commands`
  - ルーティング:
    - `/scout run`
    - `/scout trends`
    - `/scout analyze {entity_id}`
    - `/scout pitch {entity_id}`

- [ ] 5. `main.py` への router 登録
  - `api/runs`
  - `api/pins`
  - `api/commands`

## Request/Response 型
- 仕様書 Section 5 の JSON 例を Pydantic モデル化する

## 参照ファイル
- `docs/spec/scout_system_spec.md` Section 5 / Section 4
