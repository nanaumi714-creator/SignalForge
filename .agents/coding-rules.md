# Coding Rules (AI Context)

## Determinism first
- Keep scoring and classification deterministic.
- Isolate side effects in adapters (API/DB/Notifier).
- Prefer pure functions for derivation logic.

## Schema discipline
- Validate all external input explicitly.
- Enforce strict JSON contracts for AI outputs.
- Fail fast on schema mismatch, then apply bounded retry.

## Observability
- Log module boundaries (collector/analyzer/scorer/notifier/db).
- Include `run_id` and `entity_id` whenever available.
- Never log secrets (API keys, tokens, webhook URLs).

## Safety
- Do not add try/catch around imports.
- Do not introduce hidden fallback behavior without docs update.
- Update contract docs before behavior changes.

## Testing
- Unit-test pure logic first (score sum, classification, dedup, delta).
- Add integration checks for external adapters.
- **Always run tests and development commands within the virtual environment (`.venv`).**
