-- SCOUT SYSTEM initial schema

create extension if not exists pgcrypto;

create table if not exists scout_runs (
  id uuid primary key default gen_random_uuid(),
  run_type text not null check (run_type in ('manual', 'scheduled')),
  status text not null check (status in ('running', 'success', 'failed')),
  config jsonb not null default '{}'::jsonb,
  summary jsonb,
  started_at timestamptz not null default now(),
  finished_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists scout_entities (
  id uuid primary key default gen_random_uuid(),
  platform text not null,
  platform_id text not null,
  channel_title text,
  channel_description text,
  country text,
  language text,
  published_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (platform, platform_id)
);

create table if not exists scout_snapshots (
  id uuid primary key default gen_random_uuid(),
  run_id uuid not null references scout_runs(id) on delete cascade,
  entity_id uuid not null references scout_entities(id) on delete cascade,
  subscriber_count bigint,
  view_count bigint,
  video_count bigint,
  collected_at timestamptz not null default now(),
  created_at timestamptz not null default now()
);

create table if not exists scout_scores (
  id uuid primary key default gen_random_uuid(),
  run_id uuid not null references scout_runs(id) on delete cascade,
  entity_id uuid not null references scout_entities(id) on delete cascade,
  total_score numeric(5,2) not null,
  category text not null,
  score_reason jsonb,
  trend_summary text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (run_id, entity_id)
);

create table if not exists scout_pins (
  id uuid primary key default gen_random_uuid(),
  entity_id uuid not null references scout_entities(id) on delete cascade,
  note text,
  pinned_by text,
  created_at timestamptz not null default now(),
  unique (entity_id)
);

create index if not exists idx_scout_runs_created_at_desc on scout_runs (created_at desc);
create index if not exists idx_scout_entities_platform_platform_id on scout_entities (platform, platform_id);
create index if not exists idx_scout_scores_run_id_total_score_desc on scout_scores (run_id, total_score desc);
