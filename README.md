# blykker

**Book-shaped blygs, as a mod of [Blygger Studio](https://github.com/blygger/blygger-studio).**
blykker is not a separate client. It is a configuration-first mod that sets up a vanilla studio
blyg for writing and publishing books on the [Blygger protocol](https://github.com/blygger/blygger-spec),
and adds book features over time as further mods.

## Intent

A blyg is a stream of fragments and threads, written in public and revised in versions. A book
has a cover, a title page, a table of contents, chapters in order, endnotes, references and an
index, and eventually an EPUB and a print manuscript. blykker joins the two. You write a book as a
living blyg, with every section a thread and every note, reference and image record a fragment,
and the book's structure keeps itself in order as you work.

- **The table of contents is the book.** Edit the Contents thread to add, remove or reorder
  sections, and navigation, menus and the cover's "Start reading" link follow.
- **Use the protocol's own link grammar for everything.** Navigation, citations, notes and
  references are ordinary `[[id | text]]` links and `![[id]]` transclusions. Any blygger client can
  read a blykker book.

## A mod, not a fork

blykker starts as **a config file**: a `book.json` that turns a vanilla studio blyg into a book,
applied by a small tool that uses the studio's own owner API, as an author or editor would. Book
features are then added as **mods**, starting from what the studio already lets a node add (its
compiled-in extensions and their slots).

When a book feature needs a hook the studio doesn't have yet, such as public-page theming, a
"book mode" layout, or a place for a navigation surface, blykker proposes it **upstream as a pull
request to Blygger Studio**, so the feature can stay a mod. The goal is never to fork. That makes
blykker the first test case for a **mods model** for the studio: a real, demanding use that shows
which surfaces a mod needs.

## Quick start

[`book.template.json`](book.template.json) is the starting point. It says where to get Blygger
Studio (its [latest release](https://github.com/blygger/blygger-studio/releases/latest) and
[install guide](https://github.com/blygger/blygger-studio#install-the-worker-download)), lists the
setup steps in order, and holds the configuration that makes a fresh blyg look like the pilot book:
cover as the front page, title page, Contents, Preface, Chapter 1, References, Index and About; a
book palette and typeface; book links in the top menu. In short:

1. Install stock Blygger Studio on a subdomain of its own.
2. Copy `book.template.json` to `book.json` and fill in the `CHANGE-ME` values.
3. Run `tools/blykker.py book.json seed` (Python 3, standard library only).
4. Write in the studio. After editing Contents, run `tools/blykker.py book.json sync`.

## Pilot: *New Nature*

blykker is being bootstrapped by writing a real book with it. *New Nature: How artificial
intelligence and computational hardness are rewilding the planet* by Venkatesh Rao is written in
public at [newnature.venkateshrao.com](https://newnature.venkateshrao.com/), on stock Blygger
Studio plus blykker's config. Whatever that book needs, blykker builds, and whatever gets in its
way becomes the backlog: either a new mod, or a hook to propose upstream.

## Status

Config stage: the `book.json` format and `tools/blykker.py` (`seed`, `sync`), running against the
pilot book's blyg. The plan, conventions and backlog are in [PLAN.md](PLAN.md), and the target book
layout is in [design/book-layout.html](design/book-layout.html).

MIT licensed, like Blygger Studio.
