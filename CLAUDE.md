# blykker — Project Instructions

> **Environment rules, keys & safety policies:** see [`Code/CLAUDE.md`](../../CLAUDE.md) and the `devops/` warnings files.
> **The protocol lives elsewhere:** [`../blygger-spec/`](../blygger-spec/). blykker is a client, not where protocol decisions get made.

blykker is the **book-specific blyg client**: a planned fork of [`../blygger-studio/`](../blygger-studio/)
customized for book-like blygs. Created 2026-11-02. Public repo `blygger/blykker` (branch `main`, MIT).

## State: dormant — do not build yet

Venkat's instruction at creation: **don't do anything here until the book is further along.**
No fork, no code, no deploys until Venkat says to start. Sessions in other projects may read this
repo; they don't write to it except to keep this file and `status.md` accurate.

## First user and requirements source: the New Nature book

| Thing | Where |
|---|---|
| Book project | `Code/Publishing/newnature/` (repo `vgururao/newnature`, private) |
| Live blyg (vanilla studio for now) | https://newnature.venkateshrao.com/ — deployment in `Publishing/newnature/blyg.md` |
| Requirements log | `Publishing/newnature/blykker-notes.md` — friction and ideas gathered while writing |

When blykker starts: read `blykker-notes.md` first, fork from a tagged studio release (the blyg
runs 0.50.0 today), and plan to move the `newnature` deployment env from the studio's private
config into blykker's own. The first chapter of the book is the planned first real test.

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
- **Verification (W2):** n/a while dormant; once code exists, the studio's test suites and a look at the live blyg.
- **Deploy policy:** only if Venkat says so.
- **Carry-overs (S6):** none
