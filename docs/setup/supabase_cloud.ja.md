# Supabase Cloud 利用ガイド

SignalForge のデータベースとして、Supabase Cloud (PaaS) を利用する際の手順です。

## 1. プロジェクトの作成
1. [Supabase Dashboard](https://supabase.com/dashboard/projects) にアクセスし、新しいプロジェクトを作成します。
2. データベースのパスワードを安全な場所に保管してください。

## 2. ローカル環境とのリンク
Supabase CLI を使用して、ローカルプロジェクトとクラウドプロジェクトを接続します。

```bash
# Supabase にログイン（初回のみ）
supabase login

# プロジェクト ID を指定してリンク
# プロジェクト ID は Dashboard の URL (https://supabase.com/dashboard/project/<project_id>) から確認できます
supabase link --project-ref <your-project-id>
```

## 3. データベースの同期（マイグレーション）
ローカルの `supabase/migrations` にある定義をクラウドの DB に反映します。

```bash
# マイグレーションをクラウド DB にプッシュ
supabase db push
```

## 4. 環境変数の設定
クラウドプロジェクトの接続情報を `.env` に反映します。

1. Supabase Dashboard の `Project Settings > API` から以下の値をコピーします。
    - `Project URL` → `SUPABASE_URL`
    - `anon public` → `SUPABASE_KEY`
2. `.env` を更新します。

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
```

## 5. 運用時の注意点
- **本番環境への反映**: 開発時はローカルで `supabase start` を使い、変更が確定したら `supabase db push` でクラウドに反映するフローを推奨します。
- **Secrets Management**: GitHub Actions 等でデプロイする場合は、これらキーを GitHub Secrets に登録してください（詳細は [DEPLOY.md](../../DEPLOY.md) を参照）。
