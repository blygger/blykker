# blykker

**Book-shaped blygs.** blykker is for writing and publishing books on the
[Blygger protocol](https://github.com/blygger/blygger-spec), built on
[Blygger Studio](https://github.com/blygger/blygger-studio).

## Intent

A blyg is a stream of fragments and threads, written in public and revised in versions. A book
has a cover, a title page, a table of contents, chapters in order, endnotes, references and an
index, and eventually an EPUB and a print manuscript. blykker joins the two. You write a book as a
living blyg, with every section a thread and every note, reference and image record a fragment,
and the book's structure keeps itself in order as you work.

The idea is to stay as close to a vanilla blyg as possible:

- **The table of contents is the book.** Edit the Contents thread to add, remove or reorder
  sections, and navigation, menus and the cover's "Start reading" link follow.
- **Use the protocol's own link grammar for everything.** Navigation, citations, notes and
  references are ordinary `[[id | text]]` links and `![[id]]` transclusions. Any blygger client can
  read a blykker book.
- **Configuration first, code later.** blykker may turn out to be mostly a config file (`book.json`)
  plus an editorial assistant that acts on a standard studio node through its owner API. It forks
  the client only for what can't be done from outside: book typography for the public site, then
  EPUB and print exports.

## Pilot: *New Nature*

blykker is being bootstrapped by writing a real book with it. *New Nature: How artificial
intelligence and computational hardness are rewilding the planet* by Venkatesh Rao is written in
public at [newnature.venkateshrao.com](https://newnature.venkateshrao.com/). Whatever that book
needs, blykker builds, and whatever gets in its way becomes the backlog. The book comes first, and
blykker is shaped by what turns out to matter in practice.

## Status

Phase 1: a `book.json` format and `tools/blykker.py` (`seed`, `sync`) running against the pilot
book's blyg on stock Blygger Studio. The plan, conventions and backlog are in [PLAN.md](PLAN.md),
and the target book layout is in [design/book-layout.html](design/book-layout.html).

MIT licensed, like Blygger Studio.
