# Status: blykker

**State:** phase 1 — config + editorial assistant (see PLAN.md).

## Active / Open
- Seed newnature (`tools/blykker.py …/book.json seed`) once its owner secrets are set — blocked on `scripts/set-blyg-secrets.sh` there.
- Phase 1 backlog in PLAN.md: notes assembly, image checks, sync safety, trigger.

## Log
- 2026-11-02 — Created: local repo (GitHub `blygger/blykker`, public), MIT, README, CLAUDE.md. Linked to `Publishing/newnature` (first user) and its blyg at newnature.venkateshrao.com, which runs vanilla blygger-studio 0.50.0 for now.
- 2026-11-02 (later) — Started phase 1 on Venkat's book-blyg brief: PLAN.md (book model, invisible markers, backlog), `tools/blykker.py` (seed, sync: nav, TOC→links sidebar, settings, references, index; tested offline with a fake node, idempotent), `design/book-layout.html` (phase-2 target). Not yet run against the live blyg.
