# blykker — Project Instructions

> **Environment rules, keys & safety policies:** see [`Code/CLAUDE.md`](../../CLAUDE.md) and the `devops/` warnings files.
> **The protocol lives elsewhere:** [`../blygger-spec/`](../blygger-spec/). blykker is a client, not where protocol decisions get made.

blykker is the **book-specific blyg client**: a planned fork of [`../blygger-studio/`](../blygger-studio/)
customized for book-like blygs. Created 2026-11-02. Public repo `blygger/blykker` (branch `main`, MIT).

## State: phase 1 — config + editorial assistant (started 2026-11-02)

Venkat started blykker on 2026-11-02 with a book-blyg design. **Read [`PLAN.md`](PLAN.md) first**:
the book model, the invisible-marker conventions, and the phased backlog. Phase 1 adds **no studio
code**. blykker is a config format (`book.json`, instance in `Publishing/newnature/`) plus
`tools/blykker.py`, which edits threads and settings through the owner API as an editor would.

| Path | What |
|---|---|
| `PLAN.md` | Book model, conventions, backlog (phases 1–3), open questions |
| `tools/blykker.py` | `seed` (create sections + reference fragments) and `sync` (TOC → nav blocks, links sidebar, settings, references, index; `--dry-run`) |
| `design/book-layout.html` | Phase-2 target layout for public pages (cover, contents, chapter, references, index) |

Run against a book: `tools/blykker.py ../../Publishing/newnature/book.json sync --dry-run`.
`sync` publishes threads that were already published and changed. **That is outward-facing**, so
run it without `--dry-run` only when Venkat says so.

## First user and requirements source: the New Nature book

| Thing | Where |
|---|---|
| Book project | `Code/Publishing/newnature/` (repo `vgururao/newnature`, private) |
| Live blyg (vanilla studio for now) | https://newnature.venkateshrao.com/ — deployment in `Publishing/newnature/blyg.md` |
| Requirements log | `Publishing/newnature/blykker-notes.md` — friction and ideas gathered while writing |

If phase 2 needs a fork: read `blykker-notes.md` first, fork from a tagged studio release (the blyg
runs 0.50.0 today), and move the `newnature` deployment env from the studio's private config into
blykker's own. Prefer proposing a theming hook upstream first (PLAN.md, phase 2).

## Rules inherited from the studio (apply once code exists)

- **Model routing applies.** Anything touching protocol semantics, cross-client invariants,
  security/crypto or API-surface design is ⚠️ FABLE (see `../blygger-spec/CLAUDE.md`) — book
  features must be client-side or extensions, not protocol changes made here.
- **Client version ≠ protocol version.** blykker gets its own `CLIENT` name/version; don't reuse
  `blygger-studio`'s generator string.
- **Deploy config is not committed** (studio session 28 pattern): `wrangler.private.jsonc` and
  `deploy-targets.json` are gitignored here too.
- Node, npm and Dropbox `node_modules` policy: `Code/devops/warnings-node.md`.

## Session rituals

**Base:** [`Code/devops/rituals.md`](../../devops/rituals.md) — v1.1.

**Ritual config**
- **Log:** `status.md`. (The program-wide DEVLOG stays in `../blygger-spec/`; add an entry there only when blykker work is part of a numbered blygger session.)
- **Startup extras (S5):** skim new items in `Publishing/newnature/blykker-notes.md`.
- **Verification (W2):** `sync --dry-run` against newnature, then look at the live blyg pages it changed.
- **Deploy policy:** only if Venkat says so.
- **Carry-overs (S6):** none
