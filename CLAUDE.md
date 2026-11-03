# blykker — Project Instructions

> **Environment rules, keys & safety policies:** see [`Code/CLAUDE.md`](../../CLAUDE.md) and the `devops/` warnings files.
> **The protocol lives elsewhere:** [`../blygger-spec/`](../blygger-spec/). blykker is a mod of the studio, not where protocol decisions get made.

blykker is a **configuration-first mod of [`../blygger-studio/`](../blygger-studio/) for book-like
blygs, not an independent client** (reframed by Venkat 2026-11-02). It starts as a config file
(`book.json`) plus a tool that sets up and maintains a vanilla studio blyg as a book. Features come
later as mods on studio surfaces, and missing surfaces are proposed upstream as PRs to
blygger-studio, so blykker never forks. It is the first test case for a studio mods model. Created
2026-11-02. Public repo `blygger/blykker` (branch `main`, MIT).

## State: phase 1 — config + editorial assistant (started 2026-11-02)

Venkat started blykker on 2026-11-02 with a book-blyg design. **Read [`PLAN.md`](PLAN.md) first**:
the book model, the invisible-marker conventions, and the phased backlog. Phase 1 adds **no studio
code**. blykker is a config format (`book.json`, instance in `Publishing/newnature/`) plus
`tools/blykker.py`, which edits threads and settings through the owner API as an editor would.

| Path | What |
|---|---|
| `PLAN.md` | Book model, conventions, backlog (phases 1–3), open questions |
| `tools/blykker.py` | `seed` (create sections, reference fragments, cover image) and `sync` (Contents → nav, menus, settings, notes, references, index, cover link; `--dry-run`) |
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

The pilot blyg stays on stock blygger-studio, deployed from the studio repo's private config. When a
mod needs code, it is a studio extension compiled in via the studio's gitignored
`extensions.local.json`, and its source lives here. When the studio has no surface for it, write
up the hook in PLAN.md → *Upstream hooks* and propose it as a blygger-studio PR. Do not fork.

## Rules inherited from the studio (apply once mod code exists)

- **Model routing applies.** Anything touching protocol semantics, cross-client invariants,
  security/crypto or API-surface design is ⚠️ FABLE (see `../blygger-spec/CLAUDE.md`). Book
  features are mods, never protocol changes. An upstream hook PR that widens the studio's
  extension surface or `/api` is API-surface design: flag it as FABLE.
- **The generator stays `blygger-studio/x.y.z`.** A mod doesn't rename the client. Mod identity, if
  needed, goes in the studio's extension metadata.
- **Extension rules apply** (`../blygger-studio/docs/extensions.md`): own directory, prefixed CSS,
  imports only from the extension surface, reads-only server routes.
- Node, npm and Dropbox `node_modules` policy: `Code/devops/warnings-node.md`.

## Session rituals

**Base:** [`Code/devops/rituals.md`](../../devops/rituals.md) — v1.1.

**Ritual config**
- **Log:** `status.md`. (The program-wide DEVLOG stays in `../blygger-spec/`; add an entry there only when blykker work is part of a numbered blygger session.)
- **Startup extras (S5):** skim new items in `Publishing/newnature/blykker-notes.md`.
- **Verification (W2):** `sync --dry-run` against newnature, then look at the live blyg pages it changed.
- **Deploy policy:** only if Venkat says so.
- **Carry-overs (S6):** none
