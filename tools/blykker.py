#!/opt/homebrew/bin/python3
"""blykker.py — editorial assistant for a book-shaped blyg (see ../PLAN.md).

Acts on a vanilla blygger-studio node through its owner API, as an author or
editor would: it edits threads and settings and never touches studio code.

  blykker.py BOOK.json seed       create and publish the sections and reference
                                  fragments that have no id yet; write ids back
  blykker.py BOOK.json sync       from the TOC thread: rewrite nav blocks, the
                                  menu, settings, notes, references and index;
                                  retarget the cover's "Start reading"; check image
                                  records; publish threads that were published and changed,
                                  unless they have unpublished author edits (those only
                                  get their working copy updated)
  blykker.py BOOK.json sync --dry-run   report what sync would change

Auth: the owner password, read from the file and variable named in BOOK.json
(`password`). Stdlib only.
"""
import http.cookiejar, json, mimetypes, re, sys, time, urllib.error, urllib.parse, urllib.request, uuid
from pathlib import Path

ID = r"[0-9a-hjkmnp-tv-z]{26}"
LINK = re.compile(rf"(?<!!)\[\[({ID})(?:[ \t]*\|([^\n]*?))?\]\]")
DIRECTIVE = re.compile(rf"^[ \t]*!\[\[({ID})(?:[ \t]*\|[^\n]*?)?\]\][ \t]*$", re.M)
INDEX = re.compile(r"^\[index:\s*([^\]]+?)\]:\s*#\s*$", re.M)
NAV_TOP, NAV_BOTTOM = "[blykker-nav-top]: #", "[blykker-nav-bottom]: #"
GENERATED = "[blykker-generated]: #"
REF_MARK = "[blykker-ref]: #"
NOTE_MARK = "[blykker-note]: #"
IMAGE_MARK = "[blykker-image]: #"
NOTES_AT = "[blykker-notes]: #"
START = re.compile(rf"\[\[({ID})([ \t]*\|[^\n\]]*?Start reading[^\n\]]*?)\]\]")
NAV_NOTE = "Navigation updated"
USER_AGENT = "blykker/0.1"


class Blyg:
    def __init__(self, base: str, password: str):
        self.base = base.rstrip("/")
        self.op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        # Cloudflare refuses Python's default User-Agent; cookie writes need a same-origin Origin.
        self.h = {"Origin": self.base, "User-Agent": USER_AGENT}
        self.send(lambda: urllib.request.Request(self.base + "/studio/login", headers=self.h,
                                                 data=urllib.parse.urlencode({"password": password}).encode()),
                  "login", parse=False)

    def send(self, make, what: str, parse=True):
        """Open a request, waiting out 429s (Retry-After) and retrying dropped connections."""
        for attempt in range(6):
            try:
                with self.op.open(make()) as r:
                    return json.load(r) if parse else None
            except urllib.error.HTTPError as e:
                if e.code != 429 or attempt == 5:
                    sys.exit(f"{what} -> {e.code}: {e.read().decode()[:500]}")
                wait = min(int(e.headers.get("Retry-After") or 30), 300)
            except urllib.error.URLError as e:
                if attempt == 5:
                    sys.exit(f"{what} -> {e.reason}")
                wait = 5 * (attempt + 1)
            print(f"  ({what}: retrying in {wait}s)", file=sys.stderr)
            time.sleep(wait)

    def api(self, method: str, path: str, body=None):
        return self.send(lambda: urllib.request.Request(
            self.base + "/api" + path, method=method, headers={**self.h, "Content-Type": "application/json"},
            data=None if body is None else json.dumps(body).encode()), f"{method} {path}")

    def upload(self, item: dict, file: Path, alt: str) -> dict:
        """Attach an image to an item as inline media; returns {id, url, revision}."""
        boundary = "blykker" + uuid.uuid4().hex
        fields = {"itemId": item["id"], "expectedRevision": str(item["revision"]), "alt": alt, "inline": "true"}
        mime = mimetypes.guess_type(file.name)[0] or "application/octet-stream"
        body = b"".join(f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
                        for k, v in fields.items())
        body += (f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{file.name}"\r\n'
                 f"Content-Type: {mime}\r\n\r\n").encode() + file.read_bytes() + f"\r\n--{boundary}--\r\n".encode()
        return self.send(lambda: urllib.request.Request(
            self.base + "/api/media", method="POST", data=body,
            headers={**self.h, "Content-Type": f"multipart/form-data; boundary={boundary}"}), "POST /media")

    def item(self, id: str) -> dict:
        return self.api("GET", f"/items/{id}")

    def create(self, kind: str, text: str) -> dict:
        return self.api("POST", "/items", {"kind": kind, "contentMd": text})

    def write(self, item: dict, text: str, publish: bool, note: str) -> dict:
        """Set the working copy; publish when asked. Returns the item after."""
        rev = item["revision"]
        if text != item["contentMd"]:
            rev = self.api("PATCH", f"/items/{item['id']}", {"contentMd": text, "expectedRevision": rev})["revision"]
        if publish:
            return self.api("POST", f"/items/{item['id']}/publish", {"note": note, "expectedRevision": rev})
        return {**item, "revision": rev, "contentMd": text}


def live_text(item: dict) -> str:
    """The text readers see: the published version when the working copy has unpublished edits."""
    return item["published"]["contentMd"] if item["dirty"] and item["published"] else item["contentMd"]


def load_book(path: Path):
    raw = path.read_text("utf-8")
    if "CHANGE-ME" in raw:
        sys.exit(f"{path} still has CHANGE-ME values; fill them in first (see its `setup` list)")
    book = json.loads(raw)
    pw_file = (path.parent / book["password"]["file"]).resolve()
    var = book["password"]["var"] + "="
    pw = next((l[len(var):].strip() for l in pw_file.read_text().splitlines() if l.startswith(var)), "")
    if not pw:
        sys.exit(f"{book['password']['var']} is not set in {pw_file}")
    return book, pw


def save_book(path: Path, book: dict) -> None:
    path.write_text(json.dumps(book, indent=2, ensure_ascii=False) + "\n", "utf-8")


# ── text transforms (pure; testable offline) ──────────────────────────────────

def split_heading(text: str):
    """(first-line heading or "", the rest)."""
    text = text.strip()
    first, _, rest = text.partition("\n")
    return (first, rest.strip()) if first.startswith("#") else ("", text)


NAV_LINE = re.compile(rf"^\[\[{ID}[ \t]*\|[^\n\]]*\]\](?:[ \t]*·[ \t]*\[\[{ID}[ \t]*\|[^\n\]]*\]\])*$")


def not_nav(chunk: str) -> str:
    """A chunk outside the nav markers less its generated nav lines: anything an
    author typed there is kept, never discarded."""
    return "\n".join(l for l in chunk.strip().splitlines() if not NAV_LINE.match(l.strip())).strip()


def strip_nav(text: str) -> str:
    """The author's text with any generated nav blocks removed."""
    if NAV_TOP in text:
        above, text = text.split(NAV_TOP, 1)
        # The heading stays above the top nav (see with_nav); keep it.
        text = f"{not_nav(above)}\n\n{text.strip()}"
    if NAV_BOTTOM in text:
        text, below = text.rsplit(NAV_BOTTOM, 1)
        text = f"{text.rstrip()}\n\n{not_nav(below)}"
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def nav_line(prev, toc, nxt, here: str) -> str:
    parts = []
    if prev:
        parts.append(f"[[{prev[0]} | ← {prev[1]}]]")
    if toc and here != toc[0] and (not prev or prev[0] != toc[0]) and (not nxt or nxt[0] != toc[0]):
        parts.append(f"[[{toc[0]} | {toc[1]}]]")
    if nxt:
        parts.append(f"[[{nxt[0]} | {nxt[1]} →]]")
    return " · ".join(parts)


def with_nav(text: str, line: str) -> str:
    body = strip_nav(text)
    if not line:
        return body
    # The heading stays first: the studio names an item (tab title, feed card,
    # RSS headline) from its first text, which must not be the nav line.
    # Each marker starts its own block, so it renders as nothing (PLAN.md, Invisible markers).
    heading, rest = split_heading(body)
    top = f"{heading}\n\n{line}" if heading else line
    return f"{top}\n\n{NAV_TOP}\n\n{rest}\n\n{NAV_BOTTOM}\n\n{line}".replace("\n\n\n\n", "\n\n")


def toc_entries(toc_text: str):
    """[(id, label)] from the TOC's author text, in order, first occurrence only."""
    seen, out = set(), []
    for m in LINK.finditer(strip_nav(toc_text)):
        if m.group(1) not in seen:
            seen.add(m.group(1))
            out.append((m.group(1), (m.group(2) or "").strip() or m.group(1)))
    return out


def notes_cited(text: str, is_note) -> list:
    """Note fragment ids cited in the text, in first-citation order."""
    return list(dict.fromkeys(m.group(1) for m in LINK.finditer(text) if is_note(m.group(1))))


def renumber(text: str, notes: list) -> str:
    """Relabel every citation of a note with its number: [[id | 3]]."""
    n = {id: i + 1 for i, id in enumerate(notes)}
    return LINK.sub(lambda m: f"[[{m.group(1)} | {n[m.group(1)]}]]" if m.group(1) in n else m.group(0), text)


def notes_block(notes: list) -> str:
    # A directive must sit alone on its line; the number is its own paragraph.
    return "\n\n".join(f"**{i + 1}.**\n\n![[{id}]]" for i, id in enumerate(notes))


def with_chapter_notes(text: str, is_note, inline: bool) -> str:
    """Author text with its note citations renumbered and, when inline, the notes block rebuilt."""
    main = strip_nav(text).split(NOTES_AT, 1)[0].rstrip()
    notes = notes_cited(main, is_note)
    main = renumber(main, notes)
    if inline and notes:
        return f"{main}\n\n{NOTES_AT}\n\n### Notes\n\n{notes_block(notes)}"
    return main


def with_generated(text: str, generated: str) -> str:
    head = strip_nav(text).split(GENERATED, 1)[0].rstrip()
    return f"{head}\n\n{GENERATED}\n\n{generated}".rstrip()


def index_terms(text: str):
    """Index terms marked in an item's text; a trailing ' N' (uniqueness suffix) is dropped."""
    return [re.sub(r"\s+\d+$", "", m.group(1)).strip() for m in INDEX.finditer(text)]


def index_body(found: dict, listed) -> str:
    """found: term -> [(id, title)] in reading order."""
    terms = {t: found.get(t, []) for t in listed} | found
    lines = []
    for term in sorted(terms, key=lambda t: t.casefold()):
        name, _, sub = term.partition(";")
        label = f"**{name.strip()}**" + (f", {sub.strip()}" if sub else "")
        locs = ", ".join(f"[[{i} | {t}]]" for i, t in terms[term])
        lines.append(f"- {label}" + (f" — {locs}" if locs else ""))
    return "\n".join(lines)


# ── commands ──────────────────────────────────────────────────────────────────

def seed(path: Path, book: dict, blyg: Blyg) -> None:
    # References first: the References thread transcludes them, and a directive
    # needs a published source.
    for ref in book.get("references", []):
        if ref.get("id"):
            continue
        item = blyg.create("fragment", f"{REF_MARK}\n\n{ref['entry']}")
        blyg.write(item, item["contentMd"], True, "Reference entry")
        ref["id"] = item["id"]
        print(f"reference {ref['key']}: {item['id']}")
        save_book(path, book)
    secs = book["sections"]
    for key, s in secs.items():
        if not s.get("id"):
            s["id"] = blyg.create("thread", f"# {s['title']}")["id"]
            print(f"section {key}: created {s['id']}")
            save_book(path, book)
    ids = {k: s["id"] for k, s in secs.items()}
    # Publish what others link to before what links to it.
    order = ["chapter", "preface", "notes", "references", "index", "about", "title", "toc", "cover"]
    for key, s in sorted(secs.items(), key=lambda kv: order.index(kv[1]["role"]) if kv[1]["role"] in order else 0):
        item = blyg.item(s["id"])
        if item["status"] == "draft" and item["contentMd"] == f"# {s['title']}":
            text = s.get("seed", f"# {s['title']}")
            if img := s.get("image"):
                media = blyg.upload(item, (path.parent / img["file"]).resolve(), img["alt"])
                item = {**item, "revision": media.get("revision", item["revision"])}
                text = text.replace("{image}", media["url"])
            for k, v in ids.items():
                text = text.replace("{" + k + "}", v)
            blyg.write(item, text, True, "First version")
            print(f"section {key}: published")
    sync(path, book, blyg, dry=False)


def sync(path: Path, book: dict, blyg, dry: bool) -> None:
    secs = book["sections"]
    by_role = {s["role"]: s for s in secs.values()}
    toc = by_role["toc"]
    items = {}

    def get(id):
        if id not in items:
            items[id] = blyg.item(id)
        return items[id]

    # The chain: cover → title → toc → TOC entries.
    chain = [(s["id"], s["title"]) for r in ("cover", "title") if (s := by_role.get(r)) and s.get("id")]
    chain.append((toc["id"], toc["title"]))
    chain += [e for e in toc_entries(live_text(get(toc["id"]))) if e[0] not in {c[0] for c in chain}]
    toc_ref = (toc["id"], toc["title"])
    titles = dict(chain)
    print("chain: " + " → ".join(t for _, t in chain))

    planned = {}  # id -> new text
    # Assembled sections first, from the live author text of every chain thread:
    # unpublished edits must not reach readers through the index or references.
    found = {}
    cited = []
    for id, title in chain:
        text = strip_nav(live_text(get(id)))
        for term in index_terms(text):
            found.setdefault(term, [])
            if (id, title) not in found[term]:
                found[term].append((id, title))
        cited += [m.group(1) for m in LINK.finditer(text)]
    # Notes: renumber citations per chapter; assemble at chapter end or in the Notes thread.
    def is_note(i):
        return i not in titles and get(i)["kind"] == "fragment" and get(i)["contentMd"].startswith(NOTE_MARK)
    assembled = {by_role[r]["id"] for r in ("cover", "toc", "index", "references", "notes") if r in by_role and by_role[r].get("id")}
    book_notes = []
    for id, title in chain:
        if id in assembled:
            continue
        text = get(id)["contentMd"]
        new = with_chapter_notes(text, is_note, book.get("notes", "chapter") == "chapter")
        if new != strip_nav(text):
            planned[id] = new
        if notes := notes_cited(strip_nav(live_text(get(id))).split(NOTES_AT, 1)[0], is_note):
            book_notes.append((title, notes))
        # Image records: report what print production will need.
        for m in DIRECTIVE.finditer(strip_nav(text)):
            img = get(m.group(1))
            if img["contentMd"].startswith(IMAGE_MARK):
                missing = [k for k in ("rights", "source", "print") if f"[{k}:" not in img["contentMd"]]
                if missing:
                    print(f"warning: image {m.group(1)} in {title} lacks {', '.join(missing)}")
    if (s := by_role.get("notes")) and s.get("id"):
        planned[s["id"]] = with_generated(get(s["id"])["contentMd"], "\n\n".join(
            f"### {t}\n\n{notes_block(n)}" for t, n in book_notes))
    # The cover's "Start reading" link follows the TOC's first entry.
    if (s := by_role.get("cover")) and s.get("id") and chain.index(toc_ref) + 1 < len(chain):
        first = chain[chain.index(toc_ref) + 1][0]
        cover = planned.get(s["id"], get(s["id"])["contentMd"])
        planned[s["id"]] = START.sub(lambda m: f"[[{first}{m.group(2)}]]", cover)
    if (s := by_role.get("index")) and s.get("id"):
        planned[s["id"]] = with_generated(get(s["id"])["contentMd"], index_body(found, book.get("index", {}).get("terms", [])))
    if (s := by_role.get("references")) and s.get("id"):
        refs = [r["id"] for r in book.get("references", []) if r.get("id")]
        refs += [i for i in dict.fromkeys(cited) if i not in refs and i not in titles
                 and get(i)["kind"] == "fragment" and get(i)["contentMd"].startswith(REF_MARK)]
        entries = sorted(refs, key=lambda i: get(i)["contentMd"].removeprefix(REF_MARK).strip().casefold())
        planned[s["id"]] = with_generated(get(s["id"])["contentMd"], "\n\n".join(f"![[{i}]]" for i in entries))

    # Nav on every chain thread except the cover, which links onward itself.
    for n, (id, title) in enumerate(chain):
        base = planned.get(id, get(id)["contentMd"])
        if by_role.get("cover", {}).get("id") == id:
            planned[id] = strip_nav(base)
            continue
        prev = chain[n - 1] if n > 0 and chain[n - 1][0] != by_role.get("cover", {}).get("id") else None
        nxt = chain[n + 1] if n + 1 < len(chain) else None
        planned[id] = with_nav(base, nav_line(prev, toc_ref, nxt, id))

    for id, text in planned.items():
        item = get(id)
        # Publishing sends the whole working copy, so never publish over author edits.
        held = item["status"] == "public" and item["dirty"]
        if held:
            print(f"{titles.get(id, id)}: has unpublished edits; readers get its generated changes when you publish it")
        if text == item["contentMd"]:
            continue
        publish = item["status"] == "public" and not held
        print(f"{titles.get(id, id)}: {'update + publish' if publish else 'update draft'}")
        if not dry:
            blyg.write(item, text, publish, NAV_NOTE)

    settings = dict(book.get("settings", {}))
    if (s := by_role.get("cover")) and s.get("id"):
        settings["frontPage"] = s["id"]
    menu = book.get("menu")
    if menu:
        # Two menus (PLAN.md): `top` is the masthead's author links, the one menu
        # at the top of every page; `bottom` is the links section (set
        # linksPosition "bottom" in settings). Both take custom labels.
        first = chain[chain.index(toc_ref) + 1][0] if chain.index(toc_ref) + 1 < len(chain) else toc_ref[0]
        def url(entry):
            if "url" in entry:
                return entry["url"]
            target = first if entry["section"] == "@first" else secs[entry["section"]]["id"]
            return f"{book['blyg'].rstrip('/')}/t/{target}/"
        settings["linksThreads"] = []
        settings["authorLinks"] = [{"label": e["label"], "url": url(e)} for e in menu.get("top", [])]
        settings["linksExternal"] = [{"label": e["label"], "url": url(e)} for e in menu.get("bottom", [])]
    else:
        settings["linksThreads"] = [id for id, _ in chain if id != settings.get("frontPage")]
    print(f"settings: {', '.join(settings)}")
    if not dry:
        blyg.api("PATCH", "/settings", settings)


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 2 or args[1] not in ("seed", "sync"):
        sys.exit(__doc__)
    path = Path(args[0]).resolve()
    book, pw = load_book(path)
    blyg = Blyg(book["blyg"], pw)
    if args[1] == "seed":
        seed(path, book, blyg)
    else:
        sync(path, book, blyg, dry="--dry-run" in sys.argv)


if __name__ == "__main__":
    main()
