# blykker — plan and backlog

blykker makes a blyg read like a book. It is a **configuration-first mod of Blygger Studio, not an
independent client** (Venkat, 2026-11-02). It is the first test case for a mods model for the studio.

- **Config first.** Phase 1 is a `book.json` that sets up a vanilla studio blyg for book use, plus
  a tool (`tools/blykker.py`) that acts on the node through its owner API, as an author or editor
  would. No studio code.
- **Then mods.** Book features are added as mods on the studio's existing extension surfaces
  (compiled-in extensions: studio pages, reading-view slots, owner reads, feed orders). See
  blygger-studio `docs/extensions.md`.
- **Hooks go upstream.** When a feature needs a surface the studio lacks (public-page theming, a
  book layout, presentation-level nav, export routes), blykker opens a **PR to blygger-studio** for
  a general hook, so the feature stays a mod. Forking is not on the plan. Each hook request is
  logged in *Upstream hooks* below, because they are the evidence the mods model is built from.

First book: *New Nature* (`Code/Publishing/newnature/`, blyg at newnature.venkateshrao.com).

## The book model

Every section is a **thread**. Notes, references and image records are **fragments**. The studio's
own link grammar connects them: `[[id | text]]` links and `![[id]]` own-line transclusions.

```
cover (static front page) → title page → contents → preface → chapter 1 … chapter n
                                                  → notes (book-level only) → references → index
about (author bio): linked from the links section and the cover, outside the reading chain
```

| Section | Kind | Who writes it |
|---|---|---|
| Cover | thread, set as the studio's static front page | author: cover image + title |
| Title page | thread | author (title, subtitle, author, edition line) |
| Contents (TOC) | thread | **author**. The TOC defines the book's structure (see below) |
| Preface, chapters | threads | author |
| Notes | fragments, assembled into a section (chapter end or a book-level thread) | author writes notes; assistant assembles them |
| References | fragments, assembled into the References thread | author or assistant writes entries; assistant assembles them |
| Index | thread | assistant-generated from markers in the text |
| About | thread | author |

### The TOC is the source of truth for order

The contents thread is an ordered list of `[[id | Title]]` links. Editing it, by adding, removing or
reordering entries or changing a label, is how the book's structure changes. Then `blykker.py sync`:

1. Reads the TOC's working copy and builds the reading chain: `cover → title → toc → TOC entries…`.
2. Rewrites the navigation block at the top and bottom of every thread in the chain:
   `[[prev | ← Previous title]] · [[toc | Contents]] · [[next | Next title →]]`.
3. Sets studio settings: `frontPage` = cover, the two menus from `book.json` → `menu` (below),
   and theme, font, title and author from `book.json`. Retargets the cover's "Start reading" link
   to the first TOC entry.

**Menus.** The studio has two: the masthead's *author links* (top of every page) and the
*links section*. `menu.top` becomes the author links: book links only (Contents, Start reading →
the first TOC entry, About). `menu.bottom` becomes the links section, set to `linksPosition:
"bottom"`: the "Made with Blykker…" line, plus the studio's own "Find more blygs". Side effect:
author links are part of `blyg.json`'s `author.links` on the wire, so they carry book links there too.
4. Re-assembles notes, references and the index (below).
5. Publishes only threads that were already published and whose text changed, with the note
   "Navigation updated". Drafts are edited but stay drafts.

"Trigger" in phase 1 means running `sync` after a TOC edit. A watcher (cron, or a studio extension
button) comes later.

**Navigation links point to the live version**, because `[[id]]` resolves to the current version
(the blygger default). Pointing them at pinned versions is circular: pinning chapter 2 would change
chapter 1's link, so chapter 1 would need a new version. That would need presentation-level nav,
not baked links (phase 2). A **"pinned edition"** (a TOC whose entries are all pinned versions,
`/t/{id}/v{n}`) is a separate, later feature: it is how a fixed "first edition" would be cut.

### Invisible markers

The studio renders markdown with raw HTML off, so HTML comments show up as text. Markdown **link
reference definitions** on their own line, after a blank line, render as nothing. They survive in
the source, so the assistant can find them. blykker uses them for everything structural:

| Marker | Meaning |
|---|---|
| `[blykker-nav-top]: #` / `[blykker-nav-bottom]: #` | Bound the generated nav blocks. Everything above the first and below the second is regenerated. |
| `[blykker-notes]: #` | Chapter-level notes are assembled below this line (above bottom nav). |
| `[blykker-generated]: #` | In assembled threads (index, references, book notes): everything below is regenerated. |
| `[index: term]: #` | An index entry at this point in the text. `[index: term; sub]: #` for a subentry. Each label must be unique within an item, so repeat it as `[index: term 2]: #` (the trailing number is ignored). |
| `[blykker-note]: #` | First line of a fragment that is an endnote. |
| `[blykker-ref]: #` | First line of a fragment that is a reference entry. |
| `[blykker-image]: #` | First line of a fragment that is an image record (see Images). |

Rule: a marker must start its own block (blank line before it). Inside a paragraph it renders as text.

### Index (studio-side markup)

The author puts `[index: hardness]: #` after the paragraph where a term matters. `sync` scans every
chain thread and writes the Index thread: terms sorted A–Z, each followed by `[[id | Section title]]`
locators in reading order. Terms listed in `book.json` → `index.terms` appear even with no
locators yet, as reminders. Locators are section-level for the web. Paragraph-level locators and page
numbers belong to exports (phase 3).

### Notes: chapter-level or book-level (`book.json` → `notes`)

A note is a fragment starting `[blykker-note]: #`. The author cites it inline with
`[[noteid | 1]]`. The assistant renumbers the labels in citation order and assembles:
- `"notes": "chapter"`: below `[blykker-notes]: #` at the end of each chapter, as `![[noteid]]`
  transclusions in order;
- `"notes": "book"`: into a Notes thread (role `notes`, placed before References in the TOC),
  grouped by chapter.

### References

A reference is a fragment starting `[blykker-ref]: #`, then the formatted entry. It is cited inline
with `[[refid]]` or `[[refid | Author 2026]]`. The References thread transcludes every reference
fragment cited anywhere in the chain, plus everything registered in `book.json` →
`references`, sorted by entry text. It comes before the index.

### Images

An image record is a fragment: `[blykker-image]: #`, the web-resolution image (studio media
upload), a caption, then a credit line. Provenance and rights go in markers that stay invisible:
`[rights: CC BY 4.0]: #`, `[source: https://…]: #`, `[print: images/print/fig-1-1.tif]: #`.
Chapters transclude the record with `![[imgid]]`. Print-resolution files live in the book project
(`newnature/images/print/`, Dropbox, not git) and are named in the `print:` marker. A `sync`
check flags images missing rights or a print file.

## Phases and backlog

### Phase 1 — config + editorial assistant (now)
- [x] `book.json` format; New Nature instance (`Publishing/newnature/book.json`)
- [x] `tools/blykker.py`: `seed` (incl. image upload), `sync` (nav, menus, settings, references, index), `--dry-run`, 429/network retry
- [x] Chapter-level and book-level notes assembly with renumbering
- [x] Image record checks (rights, source, print file): warnings
- [x] Title page, preface, about threads for New Nature; cover image (composed: `newnature/scripts/make_cover.py`)
- [x] Text an author types outside the nav markers is kept, not discarded
- [ ] `sync` safety: report a hand-edited nav line instead of silently regenerating it
- [ ] Trigger: run `sync` from a cron or a studio extension button instead of by hand (pilot request; see below)
- [ ] Manuscript statistics: words per chapter and total, notes, references, index, images (`blykker.py stats`, then studio-side)
- [ ] Composition start page: private, Contents-ordered list of sections with edit links (studio extension page)

Feature requests from the pilot book are collected in `Publishing/newnature/blykker-notes.md` → *Feature to-do*.

### Phase 2 — book presentation of the public site (needs an upstream hook)
Possible by config today: custom theme colours, the "book" font stack, links sidebar as TOC,
static front page. Not possible without code: typography and layout. The target design is
`design/book-layout.html`:
- chapter opener (chapter number, title, generous top space), drop cap, centred narrow measure
- nav rendered as a book's running footer, not a link paragraph (blykker recognises the nav block)
- cover page as a full-bleed image with title overlay; no feed furniture on book pages
- notes and references typeset small, hanging indents; index in two columns
- hide feed-era apparatus on book threads (dates, changelog line) or move it to a colophon
- Then: presentation-level nav that can point at pinned versions (removes the circularity above)
Route: a PR to blygger-studio for a public-page presentation hook (e.g. operator CSS, or an
extension slot that can restyle public pages for chosen threads), then the book layout as a blykker
mod on that hook. Today extensions are studio-only by design ("The wire" and "Other screens" in
`docs/extensions.md`), so this is a real change of studio policy and goes through review there.

### Phase 3 — production outputs
- [ ] EPUB from the chain (pinned edition), notes per config, index with anchors
- [ ] Print manuscript: .docx for the Publishing pipeline (editor → Vellum), print-resolution images
- [ ] Pinned editions: cut "edition 1" as a TOC of pinned versions; colophon with version list (see *Editions* below)
- [ ] Word counts per edition: word-count extension v2 (see *Editions* below)
- [ ] Project dashboard: how far drafting is ahead of published, and published ahead of the stable edition
- [ ] Register the book in `Publishing/vgr-books/registry.json` at beta

## Editions (planned 2026-11-04, not built)

A book on a blyg has editions the way software has releases. Planned, not designed in detail.
Editions are **per book**: on a blyg with several books (see *Several books on one blyg*), each book is cut,
numbered and pinned on its own schedule.

| Edition | What it is | How a reader reaches it |
|---|---|---|
| **Bleeding edge** | The live book: every section at its current published version. `[[id]]` links already resolve here. | The blyg as it is today |
| **Newest stable** | The book's most recently cut edition: a fixed set of pinned versions | A "Stable edition" link on the book's cover and Contents, which blykker retargets on each cut. Not the global menu, which is shared by every book on the blyg. |
| **Older editions** | Every earlier cut. Pins are permanent public references (spec §2.8), so an old edition never stops resolving. | An editions list (colophon or an Editions thread) |

The author also has a **draft** state ahead of the bleeding edge: unpublished edits in working
copies. The draft is never public. It appears only in the Studio and the project dashboard.

### Cutting an edition (`blykker.py cut-edition`, sketch)

1. **Check.** Every section in the Contents outline is published with no unpublished edits, unless the cut is told to ignore drafts.
2. **Pin.** Pin each section's current published version, and the Contents' own (`PUT /api/items/{id}/versions/{v}/pin`).
3. **Manifest.** Write an **edition manifest** thread ("Edition 2 · 2027-03-01"). Its outline lists each section's pinned
   version, and its colophon gives the version list and word counts. Publish it and pin it.
4. **Record.** Add the edition to the book's config → `editions` (number, date, manifest id and version, section pins).
   Retarget the book's "Stable edition" link.

**The open problem: links to a version.** The bracket grammar has no versioned link: `![[id@vN]]` is reserved
and rejected at publish (§10.1), and there is no `[[id@vN]]`. Two options:
- **Today:** a manifest's outline is a list of plain markdown links to pinned version pages,
  `- [Chapter 1](/t/{id}/v3/)`. They work now, with no studio or spec change.
- **Later:** a versioned link form in the grammar. That is a protocol decision (⚠️ FABLE + Venkat,
  in blygger-spec), not a blykker or studio one. Propose it only if the markdown form proves inadequate.

**Navigation inside an edition is also unsolved.** Pinned versions carry their baked nav, which links to the live
version (see *The TOC is the source of truth for order*), so "Next →" inside a stable edition jumps to the
bleeding edge. This needs presentation-level nav (phase 2) or edition-aware rendering. Until then, an edition
is a citable, readable set of snapshots, but not something to read page to page.

### Word-count extension v2: counts for pinned versions

v1 is blygger-studio PR #117: published and draft counts for each reading entry, rolled up over
its outline tree. v2 adds counts for **pinned versions**, so an edition has a word count that never changes.

- **Counting:**
  - **Versions are immutable,** so a pinned version's count is a pure function of stored bytes. Computing it
    on demand from `versions.content_html` gives the same answer every time.
  - **"Saving" a count** therefore means recording it, not caching it for correctness:
    1. **In the edition manifest.** blykker writes the counts into the manifest's colophon at cut time, through
       the owner API. That is the author's own content, so it may be public. **Do this first.** It needs no studio change.
    2. **Computed on demand by the extension.** A new owner read, e.g. `GET /api/ext/word-count/edition?id=&v=`, walks a
       pinned manifest's outline. The outline parser learns a second link form: a list item that is only a link to a
       version page of one of our items, `[label](…/t/{id}/vN/)` or `…/f/{id}/vN/`. That gives (id, version) edges. The
       strict-tree rules and the reasons for no total stay as in v1.
    3. **A stored cache table.** Only if on-demand counting is measured to be too slow. Extension server halves are
       read-only and cannot add migrations, so this would be a core hook proposed upstream, and it does not clear
       the bar today.
- **Reporting:** for each edition, the stable total beside the bleeding-edge published total and the draft total, with the two gaps:
  - drafting ahead of published (v1 already has the data);
  - published ahead of the newest stable edition (needs v2).
  
  This feeds the project dashboard (phase 3) and the composition start page (phase 1).
- **Older editions** come free: any manifest version can be counted, and the counts never change.
- **Wire:** no change. Counts stay Studio furniture, except where the author writes them into a manifest's colophon as content.

## Several books on one blyg (planned 2026-11-04, not built)

A blyg may host several related books on one theme, as the Publishing tree already has series
(`Configurancy/`, 4 volumes; `artofgig/`, 3). New Nature is the first such blyg. Plan for many books
now, and build for one until the second one is real.

### Two levels of config

Today `book.json` mixes settings for the whole blyg with settings for the one book. When a second
book exists, split it:

| Level | File (sketch) | Holds |
|---|---|---|
| Blyg (the shelf) | `blyg.json`-adjacent config, e.g. `shelf.json` | blyg URL, password source, studio settings (theme, font, title, author), both menus, the front page, shared hoppers, the list of books |
| Book project | one `book.json` per book | slug, title, subtitle, author, sections and their ids, notes mode, references, index terms, editions, the book's own hoppers |

**Compatibility:** a lone `book.json` keeps working as "a shelf with one book", and nothing changes for New Nature
until a second book arrives. Section keys are namespaced by book slug (`newnature/ch1`) wherever they leave the book's file.

### The book project: the unit blykker creates

A **book project** is everything one book needs on a blyg, created in one step and then kept in step by `sync`. It is
blykker's main abstraction: a shelf is a blyg with one or more book projects. Today's `seed` is that step for a
blyg with exactly one book; it generalizes to:

`blykker.py new-book <slug> --title "…"` (sketch), which:
1. **Config.** Writes the book's `book.json` from `book.template.json` (title, subtitle, author, notes mode), and adds
   the book to the shelf's list of books.
2. **Section threads.** Creates the scaffold: cover, title page, Contents, preface, chapter 1, references and index,
   with the invisible nav markers, then writes their ids back into the config. They are published, as `seed` does now,
   because the Contents and shelf outlines link to them and a link to a draft will not publish.
3. **Staging hopper.** Creates `<slug>-manuscript` (private).
4. **Shelf entry.** Adds the book to the shelf thread's outline, so it gets a reading chain, nav blocks and a word-count
   roll-up on the next `sync`.
5. **Local folder.** Creates `<shelf project>/books/<slug>/` with a `status.md`, so the Publishing Dashboard tracks
   the book (and later a `vgr-books/registry.json` entry at beta).

What a book project does not own: the theme, the menus, the front page, the `notebook` and `meta` hoppers, and the
image register. Those belong to the shelf and are shared by every book on it.

The reverse operation, retiring a book, is deliberately left out of the plan for now. Withdrawal is public and
permanent per item, so it needs its own design.

### What changes when there are several books

- **Front page.** The front page becomes a **shelf** thread, not one book's cover. The shelf is an outline: a list of
  links to each book's cover or Contents. Each book keeps its own cover thread.
- **Word counts.** These work unchanged. The shelf's outline links to each book's Contents, so the word-count extension
  rolls up the whole shelf, and each book's Contents rolls up that book. A section shared by two books makes the
  shelf's tree repeat an item, so the shelf gets no total and each book still gets its own. That is the conservative rule
  doing its job.
- **Menus.** The studio's two menus are blyg-wide, so they hold shelf links (Library, About, Meta), not one book's
  "Start reading". A book's own links live in its cover, its Contents and its nav blocks.
- **Navigation.** Each book has its own reading chain (cover → title → Contents → sections). The nav line gains a
  link back to the shelf. Chains never cross books.
- **Notes, references and the index** are per book: endnote numbering, the References thread and the index all
  belong to the book.
  - **Reference fragments may be shared.** Two books' References threads can transclude the same fragment, and that is
    fine, because transclusions are not followed in roll-ups.
  - **A combined index across the shelf is a later option.**
- **Editions** are per book (see *Editions*).
- **Images:** one register per blyg (`images/index.json`), whose "where used" names book and section.
- **Project layout:** the blyg's project folder becomes the shelf, with one subfolder per book, each with its own
  `status.md` for the Publishing Dashboard and, at beta, its own `vgr-books/registry.json` entry, as series do today.
  Do not move anything until the second book exists.

### Hoppers: shelf-wide working material, per-book staging

A hopper is an unordered set of items, public or private. It can hold your own drafts and other people's posts.
**A hopper does not make anything private:** publishing puts an item in the main feed whatever hopper it is in,
and only a draft stays private.

| Hopper | Scope | Visibility | Holds |
|---|---|---|---|
| `notebook` | shelf | private | Notes to self, mostly unpublished drafts, plus other people's posts kept as raw material. One notebook serves every book, because material on a shared theme rarely knows which book it is for. Named `notebook`, not `notes`, because blykker's "notes" are endnotes. |
| `meta` | shelf | public | Published posts about the project: a making-of stream with its own page (`/h/meta/`) and, if hopper feeds are on, its own RSS feed |
| `<slug>-manuscript` | one per book | private | Material going into that book but not yet placed in its Contents. A staging area, not a copy of the Contents: the Contents outline remains the only source of a book's structure and order, so the hopper cannot drift from it. |

**Flow:** notebook (maybe) → `<slug>-manuscript` (yes, for this book, not yet placed) → the book's Contents (placed).
An item can sit in more than one hopper, so a note can be staged for two books at once.

**Planned tool support:**
- `seed` creates the hoppers from config.
- `sync` reports staged items missing from the Contents, and Contents sections missing from staging.
- A `promote` command (later, a Studio ⋯ action) moves an item one stage along.
- The word-count extension could total each hopper for the dashboard: notebook, staged, placed.

**Known friction:** a draft note cannot be quoted (`![[id]]`) or linked into a chapter. Drafts do not resolve, and
publishing a note puts it in the public feed. So a note reaches the manuscript by being published or by being copied
into a chapter. The planned tangling feature may be the real answer; log it as friction until then. Published notes
and meta posts also crowd the home page; that is the existing home-page-order hook.

### Decisions (Venkat)

- **Name — decided 2026-11-04 (Venkat):** "New Nature" is **both the shelf and its first volume**, the way a class of
  ships is named for its first ship. A later volume might be *The New Nature of Computing*. Consequences:
  - The blyg (`newnature.venkateshrao.com`) is the shelf, and its site title "New Nature" names the shelf.
  - Volume 1 keeps the title *New Nature*, and its book slug is `newnature`. Book slugs only need to be unique among
    the shelf's books; the shelf itself needs no slug, since it is the blyg and the project folder. A second volume
    would get a short slug of its own, such as `computing`.
  - Until a second volume exists nothing moves: the front page stays volume 1's cover. When one arrives, the front page
    becomes the shelf thread, and volume 1's title page may gain a series line ("New Nature, volume 1").
- **Notebook — decided 2026-11-04:** private drafts by default. A note is published only when it is meant to be public.
- **Manuscript hoppers — decided 2026-11-04:** staging only. A `<slug>-manuscript` hopper holds material for that book
  that is not yet placed. It is never a mirror of the book's sections, and the Contents outline stays the only source of
  structure and order.
- **Pending upstream (Venkat, 2026-11-04):** a studio feature that properly distinguishes *private* from *draft* status.
  When it lands, revisit the notebook design and the friction above (a draft note can't be quoted or linked into a
  chapter without being published to the feed). A private-but-resolvable state may remove that friction, and may change
  what "private drafts by default" means for the notebook.

## Upstream hooks (PRs to blygger-studio)

The surfaces blykker needs and the studio lacks. Each is proposed as a general hook, not a book
feature. Status: *idea* → *proposed* (issue/PR link) → *merged* / *declined*.

| Hook | Needed for | Status |
|---|---|---|
| Public-page presentation for chosen threads (CSS or an extension slot) | Phase 2 book layout | idea |
| A custom label for a thread in the links section | "Start reading" without an external link | idea |
| Hide or restyle feed apparatus (version line, changelog note, dates) per thread | Book pages that read like pages | idea |
| Feed order or filter that can leave out fragments carrying a marker | Keep notes and references out of Posts | idea (an extension feed order can already reorder; filtering is the gap) |
| Write-capable extension action, or a server hook on publish | Rebuild nav when Contents change, without an outside watcher | idea |

## Open questions
- Does publishing a nav-only change deserve a new public version every time? It adds changelog
  noise. The alternatives are presentation-level nav (phase 2) or leaving nav edits unpublished
  until the next content publish.
- Should reference fragments be visible in the public feed as items? They are published items,
  so they appear there. A feed order that hides `[blykker-*]` fragments would need an extension.
