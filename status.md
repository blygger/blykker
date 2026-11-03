# Status: blykker

**State:** config stage — a configuration-first mod of blygger-studio (not a client; reframed 2026-11-02). See PLAN.md.

## Active / Open
- Phase 1 backlog in PLAN.md: notes assembly, image checks, sync safety, trigger.

## Log
- 2026-11-02 — Created: local repo (GitHub `blygger/blykker`, public), MIT, README, CLAUDE.md. Linked to `Publishing/newnature` (first user) and its blyg at newnature.venkateshrao.com, which runs vanilla blygger-studio 0.50.0 for now.
- 2026-11-02 (later) — Started phase 1 on Venkat's book-blyg brief: PLAN.md (book model, invisible markers, backlog), `tools/blykker.py` (seed, sync: nav, TOC→links sidebar, settings, references, index; tested offline with a fake node, idempotent), `design/book-layout.html` (phase-2 target). Not yet run against the live blyg.
- 2026-11-02 (evening) — Ran against the live New Nature blyg: seeded cover (composed image), title page, Contents, Preface, Chapter 1, References (6 fragments), Index, About; menus (masthead = book links, bottom links = Blykker line), theme. Added notes assembly, image checks, cover Start-reading retarget, 429/network retry, author-text preservation outside nav markers. Bug found live and fixed: the Start-reading regex could span two links. Live dry-run idempotent.
- 2026-11-02 15:15 PST — wrap-up. README rewritten (intent; New Nature as pilot). Tool live-verified against newnature (dry-run clean). Next: phase 1 backlog items in PLAN.md as the book needs them.
- 2026-11-02 — Reframed (Venkat): blykker is a configuration-first mod of blygger-studio, not an independent client; features as mods, missing surfaces proposed as studio PRs; first test case for a mods model. README, PLAN (new *Upstream hooks* table), CLAUDE.md updated.
- 2026-11-02 — `book.template.json`: user starting point (studio release + install links, ordered setup steps, New Nature-style config with CHANGE-ME placeholders). Seed tested end to end on a fake node (publish order, menus, cover link, idempotent re-sync). Tool refuses configs with CHANGE-ME left. README Quick start added.
- 2026-11-02 19:14 PST — Session 1 closed (logged in `Publishing/newnature/DEVLOG.md`). blykker is run from newnature's sessions until it is managed on its own.
