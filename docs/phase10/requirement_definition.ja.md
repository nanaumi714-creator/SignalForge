# Phase 10: WEBサーチ機能の統合 要件定義書

## 1. 背景と目的
YouTubeのキーワード検索だけでは、特定の文脈（例：「今TikTokでバズっている海外ミュージシャン」「Redditで話題のVTuber」など）に基づいた柔軟なチャンネル開拓が困難である。OpenAIのWEBサーチ能力（または外部検索APIとの連携）を活用し、インターネット上のトレンドから有望なクリエイターを逆引きする機能を実現する。

## 2. 実装要件

### 2.1 外部検索ツールの導入
OpenAI APIだけでは最新のWEB情報にアクセスできない場合があるため、以下のいずれかのアプローチを採用する。
- **OpenAI Search Tool (if available)**: OpenAIが提供する検索機能。
- **Custom Search Tool (推奨)**: Tavily Search API または Serper.dev などのAPIを OpenAI の Function Calling を通じて呼び出す。

### 2.2 サーチプロトコル
1.  **プロンプト生成**: `ScoutRun` の設定（keywords等）に基づき、「[カテゴリ]で今注目されている海外YouTubeチャンネル」といった検索クエリをLLMに生成させる。
2.  **WEB検索の実行**: 生成されたクエリを用いてWEB検索を実行し、候補となるクリエイター名、チャンネル名、ハンドル名を抽出する。
3.  **情報抽出**: 検索結果のテキストから YouTube に関連する情報（チャンネルURL、ハンドル名、タイトル）を抽出する。

### 2.3 YouTube ID への解決 (Resolution)
抽出された名前情報を YouTube Data API を用いて一意のチャンネルIDに解決する。
- YouTube Search API (`type=channel`, `q=[抽出された名前]`) を使用。
- 最も関連性の高い上位の結果を採用し、重複チェックを行う。

### 2.4 オブザーバビリティと履歴
- どのような検索クエリでどのチャンネルが発見されたかの履歴を `ScoutRun` のログまたは新規テーブルに記録する。

## 3. 処理フロー案
1.  **Discovery**: LLM + Search Tool が候補名リスト（例：["Creator A", "@handle_b"]）を生成。
2.  **Resolution**: `YouTubeCollector` がリストの各項目をチャンネルIDに変換。
3.  **Injection**: 新しく発見されたIDを `scout_entities` に追加。
4.  **Collection**: 通常の収集・分析プロセス（Phase 2-4）へ合流。

## 4. 設定項目の追加
- `SEARCH_API_KEY`: 使用する検索API（Tavily等）のキー。
- `DISCOVERY_KEYWORDS`: WEB検索に使用するベースキーワード。
