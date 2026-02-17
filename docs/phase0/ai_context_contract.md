# AI Context Contract (Phase 0)

## 1) Goal
This contract defines the minimum stable context required for AI-driven implementation of SCOUT SYSTEM.
It is intended to reduce ambiguity between planning, coding, and review.

## 2) Scope
- In scope:
  - scoring rubric
  - classification rules
  - structured output contract
  - trend extraction windows
  - failure/retry behavior for AI calls
- Out of scope:
  - queue migration (RQ/Redis)
  - multi-platform expansion (X/Twitch)

## 3) Canonical Entities
- `ScoutRun`
- `ScoutEntity`
- `ScoutSnapshot`
- `ScoutScore`
- `ScoutPin`
- `TrendObject`

All AI-generated content must be mappable to these entities.

## 4) Scoring Contract
### 4.1 Axis and bounds
- `demand_match`: integer [0, 30]
- `improvement_potential`: integer [0, 20]
- `ability_to_pay`: integer [0, 15]
- `ease_of_contact`: integer [0, 15]
- `style_fit`: integer [0, 20]

### 4.2 Derived value
- `total_score = sum(all axes)`

### 4.3 Classification
- `top`: top 10 by `total_score` in a run
- `hot`: `total_score >= 85` and `score_delta >= 5`
- `watch`: not top/hot and `total_score >= 60`
- `normal`: otherwise

## 5) AI Structured Output
AI must return JSON only (no prose outside JSON):

```json
{
  "demand_match": 0,
  "improvement_potential": 0,
  "ability_to_pay": 0,
  "ease_of_contact": 0,
  "style_fit": 0,
  "summary": "Japanese summary up to 200 chars",
  "fit_reasons": ["reason1", "reason2", "reason3"],
  "recommended_offer": "single-sentence recommendation"
}
```

Validation requirements:
- all numeric fields must be integers and within bounds
- `summary` must be <= 200 Japanese characters
- `fit_reasons` must contain 3 to 5 strings
- if validation fails, retry up to 2 times with the same input

## 6) Trend Extraction Contract
Windows:
- `7d`: burst discovery
- `30d`: stable growth discovery

Output schema:

```json
{
  "keyword": "vtuber cover en",
  "window": "7d",
  "growth_signal": "burst",
  "growth_rate": 2.8,
  "example_entities": [
    {"entity_id": "uuid", "name": "Channel A"}
  ]
}
```

Allowed `growth_signal` values: `burst`, `stable`, `emerging`.

## 7) Prompting Rules
- Use role-specific system prompts.
- Enforce JSON-only responses.
- Batch analysis by 5 entities.
- Keep prompts deterministic and avoid hidden instructions.

## 8) Error Policy
- Parse error / schema mismatch: retry (max 2)
- Partial batch failure: store per-entity error and continue
- Provider failure: mark run status as `error` with reason in run summary

## 9) Governance
Any change to this contract must be reviewed before implementation changes.
