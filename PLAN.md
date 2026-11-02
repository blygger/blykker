# blykker — plan and backlog

blykker makes a blyg read like a book. **Phase 1 is a configuration file plus an editorial
assistant**: a `book.json` that describes a book, and a script (`tools/blykker.py`) that acts on a
vanilla blygger-studio node through its owner API, the way an author or editor would. It adds no
code to the studio. If phase 1 is enough, blykker stays a config format and a tool. It becomes a
client fork only for things the studio cannot do from outside: public-page presentation (phase 2),
then exports (phase 3).

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
- [ ] Trigger: run `sync` from a cron or a studio extension button instead of by hand

### Phase 2 — book presentation of the public site (needs client code)
Possible by config today: custom theme colours, the "book" font stack, links sidebar as TOC,
static front page. Not possible without code: typography and layout. The target design is
`design/book-layout.html`:
- chapter opener (chapter number, title, generous top space), drop cap, centred narrow measure
- nav rendered as a book's running footer, not a link paragraph (blykker recognises the nav block)
- cover page as a full-bleed image with title overlay; no feed furniture on book pages
- notes and references typeset small, hanging indents; index in two columns
- hide feed-era apparatus on book threads (dates, changelog line) or move it to a colophon
- Then: presentation-level nav that can point at pinned versions (removes the circularity above)
Route: propose a theming hook upstream (custom CSS or "book mode") to blygger-studio first; fork
only if that is refused or too slow.

### Phase 3 — production outputs
- [ ] EPUB from the chain (pinned edition), notes per config, index with anchors
- [ ] Print manuscript: .docx for the Publishing pipeline (editor → Vellum), print-resolution images
- [ ] Pinned editions: cut "edition 1" as a TOC of pinned versions; colophon with version list
- [ ] Register the book in `Publishing/vgr-books/registry.json` at beta

## Open questions
- Does publishing a nav-only change deserve a new public version every time? It adds changelog
  noise. The alternatives are presentation-level nav (phase 2) or leaving nav edits unpublished
  until the next content publish.
- Should reference fragments be visible in the public feed as items? They are published items,
  so they appear there. A feed order that hides `[blykker-*]` fragments would need an extension.
