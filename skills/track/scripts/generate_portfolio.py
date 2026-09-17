#!/usr/bin/env python3
"""
Regenerates PORTFOLIO.html at a scope root from the frontmatter of every
STATUS.md found under that scope. No external dependency (no PyYAML) —
the frontmatter is deliberately simple (key: value, a single list form)
so a hand-rolled parser is enough.

Usage: generate_portfolio.py <scope_root>
"""
import os
import re
import sys
from datetime import date, datetime
from html import escape
from pathlib import Path


# HTML-escaping convention — pick by *where the value lands*, not by language.
# A new locale's strings can contain apostrophes and quotes; the call name is
# what keeps every site correct:
#   _attr() — inside a double-quoted attribute ("aria-label=…", "href=…"). A
#             raw " or ' would break out of the attribute, so encode them.
#   _txt()  — element text between tags. Quotes are safe there, so leave them
#             readable ("aujourd'hui", not "aujourd&#x27;hui").
def _attr(value):
    return escape(value, quote=True)


def _txt(value):
    return escape(value, quote=False)


FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
REQUIRED_FIELDS = ["project", "status", "last_updated"]


def _config_dir():
    return Path.home() / ".claude" / "project-tracker"


def _config_lines(name):
    f = _config_dir() / name
    if not f.exists():
        return []
    out = []
    for line in f.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            out.append(line)
    return out


def _expand(path):
    return os.path.expanduser(os.path.expandvars(path))


def load_scopes():
    # No .resolve(): entries are compared as literal strings against
    # literal paths, the same way the shell hooks do it. `~`/`$VAR` are
    # expanded so a config written with `~/...` still works.
    return [Path(_expand(l.rstrip("/"))) for l in _config_lines("scopes.txt")]


def load_global_trackignore():
    return [_expand(l.rstrip("/")) for l in _config_lines("trackignore.txt")]


# Lines in portfolio.txt that start with one of these prefixes carry
# configuration, not the output path — every loader skips them so the
# file is order-independent.
_RESERVED_PORTFOLIO_PREFIXES = ("title:", "language:")


def load_portfolio_target():
    for raw in _config_lines("portfolio.txt"):
        if raw.startswith(_RESERVED_PORTFOLIO_PREFIXES):
            continue
        p = Path(os.path.abspath(_expand(raw)))  # normalise, no symlink resolution
        return p if p.suffix == ".html" else p / "PORTFOLIO.html"
    return None


def load_portfolio_title():
    for raw in _config_lines("portfolio.txt"):
        if raw.startswith("title:"):
            return raw[len("title:"):].strip() or None
    return None


_LANG_ALIASES = {
    "en": "en", "english": "en", "anglais": "en",
    "fr": "fr", "french": "fr", "francais": "fr", "français": "fr",
}


def _normalise_lang(raw):
    return _LANG_ALIASES.get(raw.strip().lower(), "en")


def load_language():
    """Machine-global output language ('en'/'fr'), from
    ~/.claude/project-tracker/language.txt. Default 'en'; unknown -> 'en'."""
    lines = _config_lines("language.txt")
    return _normalise_lang(lines[0]) if lines else "en"


def load_portfolio_language():
    """Portfolio language: the 'language:' line of portfolio.txt if it carries
    a non-empty value, else the machine-global load_language()."""
    for raw in _config_lines("portfolio.txt"):
        if raw.startswith("language:"):
            value = raw[len("language:"):].strip()
            if value:
                return _normalise_lang(value)
    return load_language()


def home_relative(p):
    p = Path(p)
    try:
        return "~/" + str(p.relative_to(Path.home()))
    except ValueError:
        return str(p)
STATUS_ORDER = ["active", "paused", "blocked", "archived"]
# Badge colours (white text on top) — identical in light/dark, only the
# page background changes theme, not the badges themselves.
# "paused" in blue (not violet): the accent is now violet (hue ~293),
# same logic as for "blocked" vs the old copper accent.
STATUS_COLORS = {
    "active": "oklch(0.55 0.15 145)",
    "paused": "oklch(0.55 0.19 255)",
    "blocked": "oklch(0.55 0.19 25)",
    "archived": "oklch(0.50 0.02 270)",
}
_UNKNOWN_STATUS_COLOR = "oklch(0.50 0.02 210)"

STRINGS = {
    "en": {
        "html_lang": "en",
        "page_title": "Project portfolio",
        "default_title": "My projects",
        "meta_line": "{count} tracked · {generated_at}",
        "status_active": "Active",
        "status_paused": "Paused",
        "status_blocked": "Blocked",
        "status_archived": "Archived",
        "freshness_today": "today",
        "freshness_yesterday": "yesterday",
        "freshness_days_ago": "{n} days ago",
        "freshness_month_ago": "~1 month ago",
        "freshness_months_ago": "~{n} months ago",
        "card_next_milestone": "Next milestone",
        "card_updated": "Updated",
        "card_aria_open_repo": "Open the {name} repository",
        "card_view_detail": "Details",
        "uncategorized": "Uncategorized",
        "empty_title": "No tracked projects yet.",
        "empty_body": "Open a Claude Code session in a folder of this scope — the project-tracker skill will offer to track it.",
        "stats_aria": "Filter by status",
        "stack_title": "Stack & tools",
        "stack_hint": "Click a technology to filter the projects that use it.",
        "stack_aria": "Filter by technology",
        "search_placeholder": "Search for a project…",
        "search_aria": "Search for a project by name",
        "reset_filters": "Reset filters",
        "filter_empty": "No project matches the filters.",
        "generated_note": "Regenerated automatically by project-tracker.",
        "subpage_state": "State",
        "subpage_next_actions": "Next actions",
        "subpage_current_phase": "Current phase",
        "subpage_recent_activity": "Recent activity",
        "subpage_latest_version": "Latest version: {version} ({date})",
        "subpage_subprojects_title": "Sub-projects",
        "subpage_subproject_tracked": "tracked",
        "subpage_subproject_listed": "listed",
        "subpage_view_repo": "View on GitHub",
        "subpage_back": "Back to portfolio",
        "subpage_page_title": "{name} — Portfolio",
    },
    "fr": {
        "html_lang": "fr",
        "page_title": "Portfolio de projets",
        "default_title": "Mes projets",
        "meta_line": "{count} suivis · {generated_at}",
        "status_active": "Actif",
        "status_paused": "En pause",
        "status_blocked": "Bloqué",
        "status_archived": "Archivé",
        "freshness_today": "aujourd'hui",
        "freshness_yesterday": "hier",
        "freshness_days_ago": "il y a {n} jours",
        "freshness_month_ago": "il y a ~1 mois",
        "freshness_months_ago": "il y a ~{n} mois",
        "card_next_milestone": "Prochain jalon",
        "card_updated": "Mis à jour",
        "card_aria_open_repo": "Ouvrir le dépôt {name}",
        "card_view_detail": "Détails",
        "uncategorized": "Sans catégorie",
        "empty_title": "Aucun projet suivi pour l'instant.",
        "empty_body": "Ouvre une session Claude Code dans un dossier de ce périmètre — le skill project-tracker proposera de le suivre.",
        "stats_aria": "Filtrer par statut",
        "stack_title": "Stack & outils",
        "stack_hint": "Clique sur une technologie pour filtrer les projets qui l'utilisent.",
        "stack_aria": "Filtrer par technologie",
        "search_placeholder": "Rechercher un projet…",
        "search_aria": "Rechercher un projet par son nom",
        "reset_filters": "Réinitialiser les filtres",
        "filter_empty": "Aucun projet ne correspond aux filtres.",
        "generated_note": "Régénéré automatiquement par project-tracker.",
        "subpage_state": "État",
        "subpage_next_actions": "Actions suivantes",
        "subpage_current_phase": "Phase actuelle",
        "subpage_recent_activity": "Activité récente",
        "subpage_latest_version": "Dernière version : {version} ({date})",
        "subpage_subprojects_title": "Sous-projets",
        "subpage_subproject_tracked": "suivi",
        "subpage_subproject_listed": "listé",
        "subpage_view_repo": "Voir sur GitHub",
        "subpage_back": "Retour au portfolio",
        "subpage_page_title": "{name} — Portfolio",
    },
}


def _strings(lang):
    return STRINGS.get(lang, STRINGS["en"])


def _status_label(status_key, s):
    return s.get(f"status_{status_key}", status_key or "?")


def parse_frontmatter(text):
    """Line-based, top-level-only: an indented line (e.g. an item inside a
    nested list like `subprojects:`) is skipped rather than misread as a
    top-level key — this parser does not understand nested YAML structures,
    it only needs to not corrupt the flat scalar keys around them."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None
    data = {}
    for line in m.group(1).splitlines():
        if line.startswith((" ", "\t")):
            continue
        line = line.rstrip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        if value.startswith("[") and value.endswith("]"):
            items = [v.strip().strip('"').strip("'") for v in value[1:-1].split(",") if v.strip()]
            data[key] = items
        else:
            data[key] = value.strip('"').strip("'")
    return data


def is_ignored(abs_path, entries, scope_roots):
    """Same rule as the shell hooks: an entry equal to a scope root
    matches exactly only; any other entry matches itself and its
    descendants."""
    for entry in entries:
        if abs_path == entry:
            return True
        if abs_path.startswith(entry + "/") and entry not in scope_roots:
            return True
    return False


PRUNED_DIR_NAMES = {"node_modules"}  # .venv etc. covered by the dot-prefix rule below


def _iter_status_files(scope_root):
    """Walks scope_root's tree and yields every STATUS.md found under
    <project>/docs/project-tracker/, pruning .git, node_modules, .venv
    and any folder whose name starts with a dot before descending into
    it."""
    for dirpath, dirnames, filenames in os.walk(scope_root):
        dirnames[:] = [
            d for d in dirnames
            if d not in PRUNED_DIR_NAMES and not d.startswith(".")
        ]
        candidate = Path(dirpath) / "docs" / "project-tracker" / "STATUS.md"
        if candidate.is_file():
            yield candidate


def _has_ancestor_in(rel_dir, dirs):
    """True if a (strict) ancestor of rel_dir, relative to scope_root, is
    itself in dirs (another folder carrying a STATUS.md)."""
    return any(ancestor in dirs for ancestor in rel_dir.parents)


def collect_projects(scope_root, ignore_entries, scope_roots):
    scope_root = Path(scope_root)
    projects = []
    warnings = []
    status_paths = sorted(_iter_status_files(scope_root))
    # Two passes to avoid any dependency on sort order: first determine
    # the complete set of folders carrying a STATUS.md, then keep only
    # those with no ancestor in that same set (the highest of each chain
    # wins).
    all_status_dirs = {p.parent.parent.parent.relative_to(scope_root) for p in status_paths}
    for status_path in status_paths:
        proj_dir = status_path.parent.parent.parent
        rel = proj_dir.relative_to(scope_root)
        if _has_ancestor_in(rel, all_status_dirs):
            continue
        if is_ignored(str(proj_dir), ignore_entries, scope_roots):
            continue
        text = status_path.read_text(encoding="utf-8", errors="replace")
        data = parse_frontmatter(text)
        if not data:
            warnings.append(f"{status_path}: no frontmatter, skipped")
            continue
        missing = [f for f in REQUIRED_FIELDS if f not in data]
        if missing:
            warnings.append(f"{status_path}: missing fields {missing}, skipped")
            continue
        data["_path"] = home_relative(proj_dir)
        data["_dir"] = str(proj_dir)
        data["scope"] = str(scope_root)
        data["category"] = data.get("category", "")
        projects.append(data)
    return projects, warnings


def aggregate_stack(projects):
    """Deduplicated union (by exact string) of all the projects' `stack`
    values, sorted case-insensitively. Each project is a real source —
    nothing is invented here, just aggregated."""
    items = set()
    for p in projects:
        for s in p.get("stack", []):
            if s:
                items.add(s)
    return sorted(items, key=str.lower)


def status_counts(projects):
    """Counts projects by status. Stable order: STATUS_ORDER first, then
    the unexpected statuses alphabetically."""
    counts = {}
    for p in projects:
        s = p.get("status", "?")
        counts[s] = counts.get(s, 0) + 1
    ordered = [(s, counts[s]) for s in STATUS_ORDER if s in counts]
    extra = sorted(s for s in counts if s not in STATUS_ORDER)
    ordered += [(s, counts[s]) for s in extra]
    return ordered


STALE_AFTER_DAYS = 30


def relative_freshness(date_str, today, s):
    """Relative label since last_updated, plus a "stale" boolean
    (>= STALE_AFTER_DAYS). Returns (None, False) if the date cannot be
    parsed (never invented). `s` is a _strings() dict."""
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None, False
    delta = (today - d).days
    if delta < 0:
        return None, False  # future date: nothing safe to display
    if delta == 0:
        return s["freshness_today"], False
    if delta == 1:
        return s["freshness_yesterday"], False
    if delta < STALE_AFTER_DAYS:
        return s["freshness_days_ago"].format(n=delta), False
    months = max(1, delta // 30)
    label = s["freshness_month_ago"] if months == 1 else s["freshness_months_ago"].format(n=months)
    return label, True


def sort_by_recency(projects):
    """Sorts by last_updated descending (most recent first). Unparseable
    dates are pushed to the end (stable sort, so their original relative
    order is kept among themselves)."""
    def key(p):
        try:
            d = datetime.strptime(p.get("last_updated", ""), "%Y-%m-%d").date()
            return (0, -d.toordinal())
        except (ValueError, TypeError):
            return (1, 0)
    return sorted(projects, key=key)


def render_card(p, s, today=None):
    if today is None:
        today = date.today()
    status_key = p.get("status", "")
    color = STATUS_COLORS.get(status_key, _UNKNOWN_STATUS_COLOR)
    label = _status_label(status_key, s)
    stack = p.get("stack", [])
    stack_html = "".join(f'<span class="tag">{_txt(tech)}</span>' for tech in stack)
    name = p.get("project", p["_path"])
    repo = p.get("repo", "")
    if not (repo.startswith("http://") or repo.startswith("https://")):
        repo = ""
    milestone = _txt(p.get("next_milestone", "")) or "—"
    # Normalised (lowercase) for the JS filters (Stack & tools, status)
    # — the display keeps the original case, only this is used for matching.
    stack_attr = _attr(",".join(tech.lower() for tech in stack))
    status_attr = _attr(status_key.lower())

    last_updated = p.get("last_updated", "?")
    freshness, is_stale = relative_freshness(last_updated, today, s)
    freshness_html = ""
    if freshness:
        cls = "freshness freshness-stale" if is_stale else "freshness"
        freshness_html = f' <span class="{cls}">({_txt(freshness)})</span>'

    # The whole card is the clickable target when a repo exists (large
    # click area rather than a small text link) — but the accessible name
    # stays short (aria-label), not the whole card content read at once.
    if repo:
        open_tag = (
            f'<a href="{_attr(repo)}" class="card" data-stack="{stack_attr}" '
            f'data-status="{status_attr}" aria-label="{_attr(s["card_aria_open_repo"].format(name=name))}">'
        )
        close_tag = "</a>"
        affordance = '<span class="card-arrow" aria-hidden="true">&#8599;</span>'
    else:
        open_tag = f'<article class="card" data-stack="{stack_attr}" data-status="{status_attr}">'
        close_tag = "</article>"
        affordance = ""

    slug = p.get("project", "")
    subpage_link = f'<a class="card-detail" href="portfolio/{_attr(slug)}.html">{_txt(s.get("card_view_detail", "Details"))}</a>' if slug else ""

    # The sub-page link is a SIBLING of {open_tag}/{close_tag}, never nested
    # inside it: when a repo exists, open_tag/close_tag is itself an <a>,
    # and an <a> inside an <a> is invalid HTML5 (the browser silently
    # closes the outer one, breaking whole-card click-to-repo and leaving
    # the arrow affordance outside any link). The outer .card-shell div is
    # the actual grid item; .card keeps data-stack/data-status (the JS
    # filters select .card[data-stack]/.card[data-status] directly).
    return f"""
    <div class="card-shell">
    {open_tag}
      <header class="card-header">
        <h2>{_txt(name)}</h2>
        <span class="status" style="background:{color}">{_txt(label)}</span>
      </header>
      <p class="path">{_txt(p["_path"])}</p>
      <div class="tags">{stack_html}</div>
      <dl class="meta">
        <div><dt>{_txt(s["card_next_milestone"])}</dt><dd>{milestone}</dd></div>
        <div><dt>{_txt(s["card_updated"])}</dt><dd>{_txt(last_updated)}{freshness_html}</dd></div>
      </dl>
      {affordance}
    {close_tag}
    {subpage_link}
    </div>"""


def _empty_state(s):
    return f"""
    <div class="empty">
      <p class="empty-title">{_txt(s["empty_title"])}</p>
      <p class="empty-body">{_txt(s["empty_body"])}</p>
    </div>"""


_INLINE_CODE_RE = re.compile(r"`([^`]+)`")
_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_BOLD_RE = re.compile(r"\*\*([^*]+)\*\*")
_ITALIC_RE = re.compile(r"(?<!\*)\*([^*]+)\*(?!\*)|_([^_]+)_")
_ORDERED_ITEM_RE = re.compile(r"^\d+\.\s+(.*)$")
_UNORDERED_ITEM_RE = re.compile(r"^[-*]\s+(.*)$")
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")


def _render_rich(raw_chunk):
    """Links, then bold, then italic, on a chunk guaranteed free of inline
    code. Link text/URL and the plain text around them are escaped exactly
    once (via _txt/_attr) before any tag is added, using numbered
    placeholders so bold/italic never re-enter an already-built <a> tag."""
    placeholders = []

    def stash(html_piece):
        placeholders.append(html_piece)
        return f"\x00{len(placeholders) - 1}\x00"

    def link_sub(m):
        return stash(f'<a href="{_attr(m.group(2))}">{_txt(m.group(1))}</a>')

    chunk = _LINK_RE.sub(link_sub, raw_chunk)
    chunk = _txt(chunk)  # escape what's left of the raw text exactly once
    chunk = _BOLD_RE.sub(lambda m: f"<strong>{m.group(1)}</strong>", chunk)
    chunk = _ITALIC_RE.sub(lambda m: f"<em>{m.group(1) or m.group(2)}</em>", chunk)
    for i, piece in enumerate(placeholders):
        chunk = chunk.replace(f"\x00{i}\x00", piece)
    return chunk


def _render_inline(raw_text):
    """Renders the targeted inline subset (code, links, bold, italic) of
    one raw (not yet HTML-escaped) line. Inline code is pulled out first
    so its content is never touched by the other patterns."""
    segments = []
    pos = 0
    for m in _INLINE_CODE_RE.finditer(raw_text):
        if m.start() > pos:
            segments.append(("rich", raw_text[pos:m.start()]))
        segments.append(("code", m.group(1)))
        pos = m.end()
    if pos < len(raw_text) or not segments:
        segments.append(("rich", raw_text[pos:]))
    return "".join(
        f"<code>{_txt(chunk)}</code>" if kind == "code" else _render_rich(chunk)
        for kind, chunk in segments
    )


def render_markdown_fragment(text):
    """Minimal Markdown -> HTML for the targeted subset used by the
    tracking files: headings, bulleted/numbered lists, bold/italic,
    links, inline code. Not a general-purpose parser -- anything outside
    this subset (tables, images, multi-line code blocks...) is rendered
    as plain paragraph text rather than interpreted, since none of it
    appears in the sections this feeds (see spec D4)."""
    lines = text.strip("\n").splitlines()
    html = []
    list_tag = []  # mutable single-item box so the closures below can write it
    list_buffer = []

    def flush_list():
        if list_buffer:
            items = "".join(f"<li>{_render_inline(i)}</li>" for i in list_buffer)
            html.append(f"<{list_tag[0]}>{items}</{list_tag[0]}>")
            list_buffer.clear()
            list_tag.clear()

    paragraph = []

    def flush_paragraph():
        if paragraph:
            html.append(f"<p>{_render_inline(' '.join(paragraph))}</p>")
            paragraph.clear()

    for raw in lines:
        line = raw.strip()
        if not line:
            flush_paragraph()
            flush_list()
            continue
        heading_m = _HEADING_RE.match(line)
        if heading_m:
            flush_paragraph()
            flush_list()
            level = len(heading_m.group(1))
            html.append(f"<h{level}>{_render_inline(heading_m.group(2))}</h{level}>")
            continue
        ordered_m = _ORDERED_ITEM_RE.match(line)
        unordered_m = _UNORDERED_ITEM_RE.match(line)
        if ordered_m or unordered_m:
            flush_paragraph()
            tag = "ol" if ordered_m else "ul"
            if list_tag and list_tag[0] != tag:
                flush_list()
            if not list_tag:
                list_tag.append(tag)
            list_buffer.append((ordered_m or unordered_m).group(1))
            continue
        flush_list()
        paragraph.append(line)
    flush_paragraph()
    flush_list()
    return "\n".join(html)


# Headings the skill already writes verbatim, per
# skills/track/references/i18n/{en,fr}.md (the source of truth for the
# wording -- duplicated here only to *recognise* them when reading a
# project's own files back, never to author new prose).
SOURCE_HEADINGS = {
    "en": {
        "where_it_stands": "Where it stands",
        "next_actions": "Next 3 actions",
        "current_focus": "Current focus",
        "in_progress": re.compile(r"^Phase \d+ — in progress$"),
    },
    "fr": {
        "where_it_stands": "État actuel",
        "next_actions": "3 prochaines actions",
        "current_focus": "Focus actuel",
        "in_progress": re.compile(r"^Phase \d+ — en cours$"),
    },
}


def _extract_section(body, heading, boundary_includes_h3=False):
    """Returns the raw Markdown between a top-level (##) heading matching
    `heading` (exact string, or a compiled pattern for a heading with a
    variable part like a phase number) and the next boundary -- another ##
    heading, or also the next ### heading when boundary_includes_h3 is
    True (used for "Where it stands", whose own "### What works"
    subsection must not be swept in). None if the heading isn't found."""
    lines = body.splitlines()
    start = None
    for i, line in enumerate(lines):
        m = re.match(r"^##\s+(.*)$", line)
        if not m:
            continue
        title = m.group(1).strip()
        matched = title == heading if isinstance(heading, str) else bool(heading.match(title))
        if matched:
            start = i + 1
            break
    if start is None:
        return None
    boundary_re = re.compile(r"^#{2,3}\s") if boundary_includes_h3 else re.compile(r"^##\s")
    end = len(lines)
    for j in range(start, len(lines)):
        if boundary_re.match(lines[j]):
            end = j
            break
    section = "\n".join(lines[start:end]).strip()
    return section or None


def extract_status_overview(status_body, lang):
    """Extracts the "Where it stands" section from a STATUS.md body,
    stopping before any ### subsections (e.g., "### What works")."""
    return _extract_section(status_body, SOURCE_HEADINGS[lang]["where_it_stands"], boundary_includes_h3=True)


def extract_status_next_actions(status_body, lang):
    """Extracts the "Next 3 actions" section from a STATUS.md body."""
    return _extract_section(status_body, SOURCE_HEADINGS[lang]["next_actions"])


def extract_roadmap_current(roadmap_body, lang):
    """Extracts current work from a ROADMAP.md body. Prefers a
    "Phase N — in progress" section; if not found, falls back to "Current focus"."""
    headings = SOURCE_HEADINGS[lang]
    section = _extract_section(roadmap_body, headings["in_progress"])
    return section if section is not None else _extract_section(roadmap_body, headings["current_focus"])


_JOURNAL_ENTRY_RE = re.compile(r"^##\s+(\d{4}-\d{2}-\d{2})\s+—\s+(.*)$")


def extract_journal_recent_entries(journal_body, count=3):
    """Returns up to `count` most recent entries as [(date, topic, body), ...],
    most recent first. JOURNAL.md is append-only and chronological (oldest
    first) -- see 'journal.entry_heading' in references/i18n/{en,fr}.md for
    the heading format, identical across languages (only the topic text
    itself is localised)."""
    entries = []
    current = None
    for line in journal_body.splitlines():
        m = _JOURNAL_ENTRY_RE.match(line)
        if m:
            if current:
                entries.append(current)
            current = [m.group(1), m.group(2), []]
        elif current:
            current[2].append(line)
    if current:
        entries.append(current)
    recent = list(reversed(entries[-count:]))
    return [(d, t, "\n".join(b).strip()) for d, t, b in recent]


_CHANGELOG_VERSION_RE = re.compile(r"^\[(\d+\.\d+\.\d+)\]\s+—\s+(\d{4}-\d{2}-\d{2})$")


def extract_changelog_latest_version(changelog_body):
    """Returns (version, date, body) for the first dated '## [X.Y.Z] —
    YYYY-MM-DD' heading (Keep a Changelog format, used verbatim regardless
    of language -- see CHANGELOG.md's own convention in this repo).
    '## [Unreleased]' never matches. None if no dated version exists yet."""
    lines = changelog_body.splitlines()
    for i, line in enumerate(lines):
        m = re.match(r"^##\s+(.*)$", line.strip())
        if not m:
            continue
        version_m = _CHANGELOG_VERSION_RE.match(m.group(1).strip())
        if not version_m:
            continue
        end = len(lines)
        for j in range(i + 1, len(lines)):
            if re.match(r"^##\s", lines[j]):
                end = j
                break
        return version_m.group(1), version_m.group(2), "\n".join(lines[i + 1:end]).strip()
    return None


_SUBPROJECT_ITEM_RE = re.compile(r"^\s*-\s+(.*)$")
_SUBPROJECT_FIELD_RE = re.compile(r"^\s*([a-z_]+):\s*(.*)$")


def parse_subprojects(status_text):
    """Parses the nested `subprojects:` list from a STATUS.md's frontmatter
    -- parse_frontmatter() deliberately skips this block (it only
    understands flat scalar keys), so this is a separate, small parser for
    the one nested structure the sub-page needs. Returns [] if the key is
    absent, empty, or the file has no frontmatter at all."""
    m = FRONTMATTER_RE.match(status_text)
    if not m:
        return []
    lines = m.group(1).splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.strip() == "subprojects:" and not line.startswith((" ", "\t")):
            start = i + 1
            break
    if start is None:
        return []
    items = []
    current = None
    for line in lines[start:]:
        if line and not line.startswith((" ", "\t")):
            break  # back to a top-level key: the nested block is over
        item_m = _SUBPROJECT_ITEM_RE.match(line)
        if item_m:
            if current is not None:
                items.append(current)
            current = {}
            line = "  " + item_m.group(1)  # re-present as a plain field line
        field_m = _SUBPROJECT_FIELD_RE.match(line)
        if field_m and current is not None:
            key, value = field_m.group(1), field_m.group(2).strip().strip('"').strip("'")
            current[key] = (value == "true") if key in ("tracked", "git") else value
    if current is not None:
        items.append(current)
    return items


def latest_subproject_changelog_date(changelog_path):
    """Reads a sub-project's own CHANGELOG.md and returns the date of its
    most recent dated version heading, or None if the file is missing or
    has no recognisable entry -- never guessed."""
    if not changelog_path.is_file():
        return None
    text = changelog_path.read_text(encoding="utf-8", errors="replace")
    found = extract_changelog_latest_version(text)
    return found[1] if found else None


def render_subprojects_section(subprojects, project_dir, s):
    """Renders the Sub-projects section: active sub-projects only (spec
    D9), name + tracked/listed + (if tracked) its own latest CHANGELOG
    date. Returns "" (section omitted) if there is no active sub-project."""
    active = [sp for sp in subprojects if sp.get("status") == "active"]
    if not active:
        return ""
    items = []
    for sp in active:
        name = sp.get("name", "?")
        if sp.get("tracked"):
            changelog_path = project_dir / sp.get("path", "") / "CHANGELOG.md"
            date_str = latest_subproject_changelog_date(changelog_path)
            detail = s["subpage_subproject_tracked"]
            if date_str:
                detail += f" — {_txt(date_str)}"
        else:
            detail = s["subpage_subproject_listed"]
        items.append(f"<li><strong>{_txt(name)}</strong> — {detail}</li>")
    return (
        f'<section class="subpage-subprojects">\n'
        f'  <h2>{_txt(s["subpage_subprojects_title"])}</h2>\n'
        f"  <ul>{''.join(items)}</ul>\n"
        f"</section>"
    )


def render_stats_section(projects, s):
    if not projects:
        return ""
    # Buttons rather than static divs: clicking a status filters the
    # grid, same mechanism as the Stack & tools chips.
    items = "".join(
        f'<button type="button" class="stat" data-status="{_attr(sk)}" aria-pressed="false">'
        f'<span class="stat-num">{n}</span>'
        f'<span class="stat-label">{_txt(_status_label(sk, s))}</span></button>'
        for sk, n in status_counts(projects)
    )
    return f'<section class="stats" role="group" aria-label="{_attr(s["stats_aria"])}">{items}</section>'


def render_stack_section(projects, s):
    stack = aggregate_stack(projects)
    if not stack:
        return ""
    # A single neutral colour by default — selecting (clicking) turns a
    # chip orange AND filters the cards that use that tech, rather than
    # an arbitrary alternation with no rule.
    chips = "".join(
        f'<button type="button" class="chip" data-tech="{_attr(tech.lower())}" '
        f'aria-pressed="false">{_txt(tech)}</button>'
        for tech in stack
    )
    return f"""
<section class="stack-section">
  <h2 class="section-title">{_txt(s["stack_title"])}</h2>
  <p class="stack-hint">{_txt(s["stack_hint"])}</p>
  <div class="stack-chips" role="group" aria-label="{_attr(s["stack_aria"])}">{chips}</div>
</section>"""


# Well-known, MIT-licensed GitHub mark (16x16 viewBox), used verbatim
# across the web as an inline icon -- no external asset, consistent with
# the "single self-contained file" rule.
GITHUB_MARK_SVG = (
    '<svg viewBox="0 0 16 16" width="16" height="16" fill="currentColor" aria-hidden="true">'
    '<path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 '
    '0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 '
    '1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 '
    '0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 '
    '2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 '
    '3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z">'
    "</path></svg>"
)

SUBPAGE_TEMPLATE = """<!doctype html>
<html lang="{html_lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{page_title}</title>
<style>
  :root {{
    color-scheme: light dark;
    --bg: oklch(1.000 0.000 0);
    --surface: oklch(0.972 0.006 293);
    --border: oklch(0.880 0.010 293);
    --ink: oklch(0.125 0.018 293);
    --muted: oklch(0.480 0.012 293);
    --accent: oklch(0.541 0.245 293);
    --accent2: oklch(0.705 0.191 42);
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{
      --bg: oklch(0.170 0.012 293);
      --surface: oklch(0.220 0.016 293);
      --border: oklch(0.330 0.016 293);
      --ink: oklch(0.948 0.005 293);
      --muted: oklch(0.580 0.008 293);
      --accent: oklch(0.714 0.148 293);
      --accent2: oklch(0.750 0.157 42);
    }}
  }}
  * {{ box-sizing: border-box; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, system-ui, sans-serif;
    max-width: 42rem;
    margin: 0 auto;
    padding: 3rem 1.5rem 4rem;
    background: var(--bg);
    color: var(--ink);
    line-height: 1.5;
  }}
  a {{ color: var(--accent2); }}
  .back {{ font-size: 0.85rem; display: inline-block; margin-bottom: 1.5rem; }}
  h1 {{ font-size: 1.5rem; margin: 0 0 1.75rem; letter-spacing: -0.01em; }}
  section {{ margin: 0 0 1.75rem; padding-top: 1.25rem; border-top: 1px solid var(--border); }}
  section:first-of-type {{ border-top: none; padding-top: 0; }}
  h2 {{ font-size: 1rem; font-weight: 700; margin: 0 0 0.6rem; }}
  h3 {{ font-size: 0.9rem; font-weight: 700; margin: 1rem 0 0.4rem; }}
  p, li {{ font-size: 0.9rem; }}
  code {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; background: var(--surface); padding: 0.1rem 0.3rem; border-radius: 4px; }}
  .repo-link a {{ display: inline-flex; align-items: center; gap: 0.4rem; font-weight: 600; text-decoration: none; }}
  .subpage-subprojects ul {{ padding-left: 1.2rem; margin: 0; }}
</style>
</head>
<body>
<a class="back" href="../{portfolio_filename}">&#8592; {back_link}</a>
<h1>{name}</h1>
{sections}
{repo_link}
</body>
</html>
"""


def build_subpage(project_dir, data, lang):
    """Assembles one project's detail sub-page: State, Next actions,
    Current phase, Recent activity, Latest version and Sub-projects
    sections, each omitted when it has nothing to show. Re-reads the
    project's own tracking files directly from project_dir rather than
    relying on data already collected for the aggregate portfolio page."""
    s = _strings(lang)
    name = data.get("project", "?")

    status_path = project_dir / "docs" / "project-tracker" / "STATUS.md"
    status_text = status_path.read_text(encoding="utf-8", errors="replace") if status_path.is_file() else ""
    status_body = FRONTMATTER_RE.sub("", status_text, count=1)
    overview = extract_status_overview(status_body, lang)
    next_actions = extract_status_next_actions(status_body, lang)

    roadmap_path = project_dir / "docs" / "project-tracker" / "ROADMAP.md"
    roadmap_text = roadmap_path.read_text(encoding="utf-8", errors="replace") if roadmap_path.is_file() else ""
    roadmap_current = extract_roadmap_current(roadmap_text, lang) if roadmap_text else None

    journal_path = project_dir / "docs" / "project-tracker" / "JOURNAL.md"
    journal_text = journal_path.read_text(encoding="utf-8", errors="replace") if journal_path.is_file() else ""
    journal_entries = extract_journal_recent_entries(journal_text, count=3) if journal_text else []

    changelog_path = project_dir / "docs" / "project-tracker" / "CHANGELOG.md"
    changelog_text = changelog_path.read_text(encoding="utf-8", errors="replace") if changelog_path.is_file() else ""
    latest_version = extract_changelog_latest_version(changelog_text) if changelog_text else None

    subprojects = parse_subprojects(status_text)
    subprojects_html = render_subprojects_section(subprojects, project_dir, s)

    sections = []
    if overview:
        sections.append(f'<section><h2>{_txt(s["subpage_state"])}</h2>{render_markdown_fragment(overview)}</section>')
    if next_actions:
        sections.append(f'<section><h2>{_txt(s["subpage_next_actions"])}</h2>{render_markdown_fragment(next_actions)}</section>')
    if roadmap_current:
        sections.append(f'<section><h2>{_txt(s["subpage_current_phase"])}</h2>{render_markdown_fragment(roadmap_current)}</section>')
    if journal_entries:
        entries_html = "".join(
            f"<article><h3>{_txt(d)} — {_txt(t)}</h3>{render_markdown_fragment(b)}</article>"
            for d, t, b in journal_entries
        )
        sections.append(f'<section><h2>{_txt(s["subpage_recent_activity"])}</h2>{entries_html}</section>')
    if latest_version:
        v, d, body = latest_version
        heading = _txt(s["subpage_latest_version"].format(version=v, date=d))
        sections.append(f"<section><h2>{heading}</h2>{render_markdown_fragment(body)}</section>")
    if subprojects_html:
        sections.append(subprojects_html)

    repo = data.get("repo", "")
    repo_html = ""
    if repo.startswith("http://") or repo.startswith("https://"):
        repo_html = (
            f'<p class="repo-link"><a href="{_attr(repo)}">'
            f'{GITHUB_MARK_SVG}<span>{_txt(s["subpage_view_repo"])}</span></a></p>'
        )

    return SUBPAGE_TEMPLATE.format(
        html_lang=_attr(s["html_lang"]),
        page_title=_txt(s["subpage_page_title"].format(name=name)),
        portfolio_filename="PORTFOLIO.html",
        back_link=_txt(s["subpage_back"]),
        name=_txt(name),
        sections="\n".join(sections),
        repo_link=repo_html,
    )


def _project_slug(data):
    """The project's filename slug for its sub-page -- its `project` key, unchanged."""
    return data.get("project", "")


def _subpage_dir(portfolio_target):
    """The `portfolio/` directory sitting next to the generated PORTFOLIO.html."""
    return portfolio_target.parent / "portfolio"


def _subpage_path(portfolio_target, slug):
    """The on-disk path for one project's sub-page, `portfolio/<slug>.html`."""
    return _subpage_dir(portfolio_target) / f"{slug}.html"


def _project_lang(data):
    """A project's own effective language (spec D6): its `language:`
    frontmatter override if set, else the machine-global language.txt,
    else 'en' -- same resolution SKILL.md itself documents."""
    override = (data.get("language") or "").strip()
    return _normalise_lang(override) if override else load_language()


def write_subpage(portfolio_target, project):
    """Builds and writes one project's sub-page file, skipping projects
    with no slug or no known directory."""
    slug = _project_slug(project)
    if not slug or not project.get("_dir"):
        return
    html = build_subpage(Path(project["_dir"]), project, _project_lang(project))
    path = _subpage_path(portfolio_target, slug)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")


def write_subpages(portfolio_target, projects, changed_dir=None):
    """Writes every project's sub-page, or -- when changed_dir is given --
    only the one project whose _dir matches it (spec D7: the hook already
    knows which project's STATUS.md just changed)."""
    for project in projects:
        if changed_dir is not None and project.get("_dir") != changed_dir:
            continue
        write_subpage(portfolio_target, project)


def clean_orphan_subpages(portfolio_target, projects):
    """Deletes any portfolio/*.html with no corresponding currently
    eligible project (spec D8) -- filename comparison only, cheap enough
    to run on every regeneration regardless of targeted vs full mode."""
    directory = _subpage_dir(portfolio_target)
    if not directory.is_dir():
        return
    valid = {f"{_project_slug(p)}.html" for p in projects if _project_slug(p)}
    for f in directory.glob("*.html"):
        if f.name not in valid:
            f.unlink()


PAGE_TEMPLATE = """<!doctype html>
<html lang="{html_lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{page_title}</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'><text y='13' font-size='14'>&#128193;</text></svg>">
<style>
  :root {{
    /* Neutres quasi blanc / quasi noir, accents violet + orange. */
    color-scheme: light dark;
    --bg: oklch(1.000 0.000 0);
    --surface: oklch(0.972 0.006 293);
    --surface-hover: oklch(0.958 0.010 293);
    --border: oklch(0.880 0.010 293);
    --border-strong: oklch(0.800 0.012 293);
    --ink: oklch(0.125 0.018 293);
    --muted: oklch(0.480 0.012 293);
    --accent: oklch(0.541 0.245 293);
    --accent2: oklch(0.705 0.191 42);
    --accent-tint: oklch(0.541 0.245 293 / 14%);
    --accent-border: oklch(0.541 0.245 293 / 35%);
    --accent2-tint: oklch(0.705 0.191 42 / 14%);
    --accent2-border: oklch(0.705 0.191 42 / 35%);
    --decor1: oklch(0.541 0.245 293 / 20%);
    --decor2: oklch(0.705 0.191 42 / 20%);
    --shadow-rest: 0 1px 2px oklch(0.125 0.018 293 / 6%);
    --shadow-hover: 0 10px 24px -12px oklch(0.125 0.018 293 / 20%);
    --radius: 0.5rem;
    --ease: cubic-bezier(0.22, 1, 0.36, 1);
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{
      /* anthracite tinted violet rather than a deep black — nicer than
         a near-pure "void", and consistent with the accent */
      --bg: oklch(0.170 0.012 293);
      --surface: oklch(0.220 0.016 293);
      --surface-hover: oklch(0.260 0.018 293);
      --border: oklch(0.330 0.016 293);
      --border-strong: oklch(0.410 0.018 293);
      --ink: oklch(0.948 0.005 293);
      --muted: oklch(0.580 0.008 293);
      --accent: oklch(0.714 0.148 293);
      --accent2: oklch(0.750 0.157 42);
      /* tints far more subtle than in light — the same opacity
         percentage reads much stronger on a near-black background */
      --accent-tint: oklch(0.714 0.148 293 / 10%);
      --accent-border: oklch(0.714 0.148 293 / 22%);
      --accent2-tint: oklch(0.750 0.157 42 / 10%);
      --accent2-border: oklch(0.750 0.157 42 / 22%);
      /* violet kept subtle (liked as is); orange bumped up to have
         more presence in the background */
      --decor1: oklch(0.714 0.148 293 / 8%);
      --decor2: oklch(0.750 0.157 42 / 16%);
      --shadow-rest: 0 1px 2px rgb(0 0 0 / 30%);
      --shadow-hover: 0 14px 28px -12px rgb(0 0 0 / 55%);
    }}
  }}
  * {{ box-sizing: border-box; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, system-ui, sans-serif;
    max-width: 72rem;
    margin: 0 auto;
    padding: 3rem 1.5rem 4rem;
    /* two radial blobs, larger and more present, fixed (no animation —
       a continuously moving background hurts readability) */
    background:
      radial-gradient(circle at 100% 0%, var(--decor1) 0%, transparent 62%),
      radial-gradient(circle at 0% 100%, var(--decor2) 0%, transparent 66%),
      var(--bg);
    background-attachment: fixed, fixed, fixed;
    color: var(--ink);
    line-height: 1.45;
  }}
  header.page {{
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 0.75rem 1.5rem;
    margin-bottom: 2.25rem;
    padding-bottom: 1.5rem;
    border-bottom: 1px solid var(--border);
  }}
  h1 {{
    font-size: 1.625rem;
    font-weight: 700;
    letter-spacing: -0.015em;
    margin: 0;
  }}
  h1 span {{ color: var(--accent); }}
  .tagline {{ font-size: 0.9rem; color: var(--muted); margin: 0.35rem 0 0; }}
  .meta-line {{
    font-size: 0.8rem;
    font-weight: 700;
    color: var(--accent2);
    background: var(--accent2-tint);
    border: 1px solid var(--accent2-border);
    padding: 0.3rem 0.7rem;
    border-radius: 999px;
    white-space: nowrap;
    flex-shrink: 0;
  }}
  .section-title {{ font-size: 1.1rem; font-weight: 700; letter-spacing: -0.01em; margin: 0 0 1rem; }}
  .category-group {{ margin: 0 0 2rem; }}
  .category-group[hidden] {{ display: none; }}
  .category-title {{
    font-size: 0.8rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--muted);
    margin: 1.75rem 0 0.9rem;
    padding-bottom: 0.4rem;
    border-bottom: 1px solid var(--border);
  }}
  .category-group:first-of-type .category-title {{ margin-top: 0; }}
  .stats {{ display: flex; flex-wrap: wrap; gap: 0.75rem; margin: 0 0 2.5rem; }}
  .stat {{
    display: flex;
    align-items: baseline;
    gap: 0.45rem;
    padding: 0.6rem 1rem;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    font: inherit;
    cursor: pointer;
    transition: border-color 150ms var(--ease), background 150ms var(--ease), transform 100ms var(--ease);
  }}
  .stat[aria-pressed="true"] {{ border-color: var(--accent2); background: var(--accent2-tint); }}
  .stat:active {{ transform: scale(0.97); }}
  .stat:focus-visible {{ outline: 2px solid var(--accent2); outline-offset: 2px; }}
  @media (hover: hover) and (pointer: fine) {{
    .stat:not([aria-pressed="true"]):hover {{ border-color: var(--accent2); }}
  }}
  .stat-num {{ font-size: 1.2rem; font-weight: 700; color: var(--accent2); }}
  .stat-label {{ font-size: 0.75rem; color: var(--muted); font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }}
  .search-row {{ display: flex; align-items: center; gap: 0.9rem; flex-wrap: wrap; margin: 0 0 1.1rem; }}
  .search-input {{
    font: inherit;
    font-size: 0.85rem;
    width: 100%;
    max-width: 22rem;
    padding: 0.5rem 0.8rem;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    color: var(--ink);
  }}
  .search-input::placeholder {{ color: var(--muted); }}
  .search-input:focus-visible {{ outline: 2px solid var(--accent2); outline-offset: 1px; border-color: var(--accent2); }}
  .reset-btn {{
    font: inherit;
    font-size: 0.8rem;
    color: var(--muted);
    background: none;
    border: none;
    padding: 0;
    cursor: pointer;
    text-decoration: underline;
    text-underline-offset: 2px;
  }}
  .reset-btn:focus-visible {{ outline: 2px solid var(--accent2); outline-offset: 2px; }}
  @media (hover: hover) and (pointer: fine) {{
    .reset-btn:hover {{ color: var(--accent2); }}
  }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.1rem; }}
  /* .card-shell is the actual grid item — it wraps .card (the click-to-repo
     link/article) and .card-detail as siblings, so the sub-page link never
     nests inside the repo <a>. Entrance animation and stagger live here
     (they animate the grid item as a whole); .card keeps its own hover/
     active motion for the click target itself. */
  .card-shell {{
    display: block;
    animation: cardIn 280ms var(--ease) both;
  }}
  @keyframes cardIn {{
    from {{ opacity: 0; transform: translateY(8px); }}
  }}
  .card-shell:nth-child(2) {{ animation-delay: 30ms; }}
  .card-shell:nth-child(3) {{ animation-delay: 60ms; }}
  .card-shell:nth-child(4) {{ animation-delay: 90ms; }}
  .card-shell:nth-child(5) {{ animation-delay: 120ms; }}
  .card-shell:nth-child(6) {{ animation-delay: 150ms; }}
  .card-shell:nth-child(7) {{ animation-delay: 180ms; }}
  .card-shell:nth-child(n+8) {{ animation-delay: 210ms; }}
  .card-shell[hidden] {{ display: none; }}
  .card {{
    display: block;
    position: relative;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.25rem 1.35rem;
    box-shadow: var(--shadow-rest);
    color: inherit;
    text-decoration: none;
    /* only transform is animated (GPU-only); border-color/box-shadow/
       background change instantly on the states below */
    transition: transform 180ms var(--ease);
  }}
  a.card {{ cursor: pointer; }}
  a.card:active {{
    transform: translateY(-1px) scale(0.985);
    transition-duration: 100ms;
  }}
  .card-arrow {{
    position: absolute;
    top: 1.1rem;
    right: 1.15rem;
    font-size: 0.9rem;
    color: var(--border-strong);
    transition: color 180ms var(--ease), transform 180ms var(--ease);
  }}
  /* hover only for precise pointers (mouse) — a tap on mobile/tablet
     must not leave the card "stuck" in hover */
  @media (hover: hover) and (pointer: fine) {{
    .card:hover {{
      transform: translateY(-3px);
      background: var(--surface-hover);
      border-color: var(--accent2);
      box-shadow: var(--shadow-hover);
    }}
    a.card:hover .card-arrow {{
      color: var(--accent2);
      transform: translate(1px, -1px);
    }}
  }}
  .card-header {{ display: flex; justify-content: space-between; align-items: flex-start; gap: 0.75rem; margin-bottom: 0.15rem; padding-right: 1.25rem; }}
  .card h2 {{ font-size: 1.05rem; font-weight: 650; margin: 0; letter-spacing: -0.005em; }}
  .status {{
    color: white;
    font-size: 0.6875rem;
    font-weight: 700;
    letter-spacing: 0.01em;
    padding: 0.2rem 0.55rem;
    border-radius: 999px;
    white-space: nowrap;
    flex-shrink: 0;
    font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  }}
  .path {{ font-size: 0.75rem; color: var(--muted); margin: 0.2rem 0 0.8rem; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }}
  .tags {{ display: flex; flex-wrap: wrap; gap: 0.4rem; margin: 0 0 0.95rem; }}
  .tag {{
    font-size: 0.7rem;
    font-weight: 600;
    padding: 0.18rem 0.55rem;
    border-radius: 999px;
    background: var(--accent-tint);
    border: 1px solid var(--accent-border);
    color: var(--accent);
    font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  }}
  .meta {{ margin: 0 0 0.85rem; display: grid; gap: 0.4rem; padding-top: 0.85rem; border-top: 1px solid var(--border); }}
  .meta > div {{ display: flex; justify-content: space-between; gap: 1rem; font-size: 0.8125rem; }}
  .meta dt {{ color: var(--muted); }}
  .meta dd {{ margin: 0; text-align: right; font-weight: 600; }}
  .freshness {{ font-weight: 500; color: var(--muted); }}
  .freshness-stale {{ font-weight: 700; color: var(--accent2); }}
  .stack-section {{ margin-top: 2.5rem; padding-top: 2rem; border-top: 1px solid var(--border); }}
  .stack-hint {{ font-size: 0.8rem; color: var(--muted); margin: 0 0 0.85rem; }}
  .stack-chips {{ display: flex; flex-wrap: wrap; gap: 0.5rem; }}
  .chip {{
    font: inherit;
    font-size: 0.75rem;
    font-weight: 600;
    font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
    padding: 0.3rem 0.65rem;
    border-radius: 8px;
    background: var(--accent-tint);
    border: 1px solid var(--accent-border);
    color: var(--accent);
    cursor: pointer;
    transition: background 150ms var(--ease), border-color 150ms var(--ease), color 150ms var(--ease), transform 100ms var(--ease);
  }}
  .chip[aria-pressed="true"] {{
    background: var(--accent2-tint);
    border-color: var(--accent2-border);
    color: var(--accent2);
  }}
  .chip:active {{ transform: scale(0.96); }}
  .chip:focus-visible {{ outline: 2px solid var(--accent2); outline-offset: 2px; }}
  @media (hover: hover) and (pointer: fine) {{
    .chip:not([aria-pressed="true"]):hover {{ border-color: var(--accent); }}
  }}
  .card-detail {{
    display: inline-block;
    margin: 0.5rem 1.35rem 0;
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--muted);
    text-decoration: none;
  }}
  .card-detail:focus-visible {{ outline: 2px solid var(--accent2); outline-offset: 2px; }}
  @media (hover: hover) and (pointer: fine) {{
    .card-detail:hover {{ color: var(--accent2); text-decoration: underline; }}
  }}
  .filter-empty {{
    text-align: center;
    padding: 2.5rem 1.5rem;
    margin-top: 1rem;
    color: var(--muted);
    font-size: 0.9rem;
  }}
  .empty {{
    grid-column: 1 / -1;
    text-align: center;
    padding: 4rem 1.5rem;
    border: 1px dashed var(--border-strong);
    border-radius: var(--radius);
    color: var(--muted);
    /* delight tier — rare (seen once, before the first tracked project) */
    animation: emptyIn 280ms var(--ease) both;
  }}
  @keyframes emptyIn {{
    from {{ opacity: 0; transform: scale(0.97); }}
  }}
  .empty-title {{ font-size: 1rem; font-weight: 700; color: var(--ink); margin: 0 0 0.4rem; }}
  .empty-body {{ font-size: 0.85rem; margin: 0; max-width: 40ch; margin-inline: auto; }}
  .generated {{ font-size: 0.75rem; color: var(--muted); margin-top: 3rem; text-align: center; }}
  @media (prefers-reduced-motion: reduce) {{
    .card-shell {{ animation: none !important; }}
    .card {{ transition: border-color 120ms linear; }}
    .card:hover, a.card:active {{ transform: none; }}
    .empty {{ animation: none !important; }}
  }}
</style>
</head>
<body>
<header class="page">
  <div>
    <h1>Portfolio<span>.</span></h1>
    <p class="tagline">{title}</p>
  </div>
  <p class="meta-line">{meta_line}</p>
</header>
{stats_section}
<div class="search-row">
  <input type="search" id="portfolio-search" class="search-input" placeholder="{search_placeholder}" aria-label="{search_aria}">
  <button type="button" id="reset-filters" class="reset-btn" hidden>{reset_filters}</button>
</div>
{groups}
<p class="filter-empty" hidden>{filter_empty}</p>
{stack_section}
<p class="generated">{generated_note}</p>
<script>
(function () {{
  var cards = document.querySelectorAll('.card[data-stack]');
  if (!cards.length) return;
  var chips = document.querySelectorAll('.chip[data-tech]');
  var statusButtons = document.querySelectorAll('.stat[data-status]');
  var searchInput = document.getElementById('portfolio-search');
  var resetBtn = document.getElementById('reset-filters');
  var emptyMsg = document.querySelector('.filter-empty');
  var selectedTech = new Set();
  var selectedStatus = new Set();
  var searchTerm = '';

  function applyFilter() {{
    var visible = 0;
    cards.forEach(function (card) {{
      var stacks = (card.getAttribute('data-stack') || '').split(',').filter(Boolean);
      var status = card.getAttribute('data-status') || '';
      var name = (card.querySelector('h2') || {{}}).textContent || '';
      var techMatch = selectedTech.size === 0 || stacks.some(function (s) {{ return selectedTech.has(s); }});
      var statusMatch = selectedStatus.size === 0 || selectedStatus.has(status);
      var nameMatch = !searchTerm || name.toLowerCase().indexOf(searchTerm) !== -1;
      var show = techMatch && statusMatch && nameMatch;
      // hidden toggles on .card-shell (the actual grid item) — .card sits
      // nested inside it now, alongside the sub-page link.
      (card.closest('.card-shell') || card).hidden = !show;
      if (show) visible++;
    }});
    document.querySelectorAll('.category-group').forEach(function (grp) {{
      var someVisible = Array.prototype.some.call(
        grp.querySelectorAll('.card-shell'), function (c) {{ return !c.hidden; }}
      );
      grp.hidden = !someVisible;
    }});
    var filterActive = selectedTech.size > 0 || selectedStatus.size > 0 || !!searchTerm;
    if (emptyMsg) emptyMsg.hidden = !(filterActive && visible === 0);
    if (resetBtn) resetBtn.hidden = !filterActive;
  }}

  function wireToggle(el, set, attr) {{
    el.addEventListener('click', function () {{
      var value = el.getAttribute(attr);
      var pressed = el.getAttribute('aria-pressed') === 'true';
      if (pressed) {{
        set.delete(value);
        el.setAttribute('aria-pressed', 'false');
      }} else {{
        set.add(value);
        el.setAttribute('aria-pressed', 'true');
      }}
      applyFilter();
    }});
  }}

  chips.forEach(function (chip) {{ wireToggle(chip, selectedTech, 'data-tech'); }});
  statusButtons.forEach(function (btn) {{ wireToggle(btn, selectedStatus, 'data-status'); }});
  if (searchInput) {{
    searchInput.addEventListener('input', function () {{
      searchTerm = searchInput.value.trim().toLowerCase();
      applyFilter();
    }});
  }}
  if (resetBtn) {{
    resetBtn.addEventListener('click', function () {{
      selectedTech.clear();
      selectedStatus.clear();
      searchTerm = '';
      chips.forEach(function (c) {{ c.setAttribute('aria-pressed', 'false'); }});
      statusButtons.forEach(function (b) {{ b.setAttribute('aria-pressed', 'false'); }});
      if (searchInput) searchInput.value = '';
      applyFilter();
    }});
  }}
}})();
</script>
</body>
</html>
"""


def _group_by_category(projects):
    """projects: recency-sorted. Returns [(label, [projects])] with the
    uncategorized group ("") first, then categories in first-appearance
    order (= most-recently-active first)."""
    buckets = {}
    order = []
    for p in projects:
        cat = (p.get("category", "") or "").strip()
        if cat == "non":
            cat = ""
        if cat not in buckets:
            buckets[cat] = []
            order.append(cat)
        buckets[cat].append(p)
    result = []
    if "" in buckets:
        result.append(("", buckets[""]))
    for cat in order:
        if cat:
            result.append((cat, buckets[cat]))
    return result


def build_page(projects, generated_at, title=None, lang="en"):
    s = _strings(lang)
    projects = sort_by_recency(projects)
    if not projects:
        groups_html = f'<div class="grid">{_empty_state(s)}</div>'
    else:
        parts = []
        for cat, members in _group_by_category(projects):
            label = cat if cat else s["uncategorized"]
            cards = "\n".join(render_card(p, s) for p in members)
            parts.append(
                f'<section class="category-group" data-category="{_attr(cat)}">\n'
                f'  <h3 class="category-title">{_txt(label)}</h3>\n'
                f'  <div class="grid">\n{cards}\n  </div>\n</section>'
            )
        groups_html = "\n".join(parts)
    resolved_title = title if title is not None else s["default_title"]
    return PAGE_TEMPLATE.format(
        html_lang=_attr(s["html_lang"]),
        page_title=_txt(s["page_title"]),
        groups=groups_html,
        title=_txt(resolved_title),
        meta_line=_txt(s["meta_line"].format(count=len(projects), generated_at=generated_at)),
        search_placeholder=_attr(s["search_placeholder"]),
        search_aria=_attr(s["search_aria"]),
        reset_filters=_txt(s["reset_filters"]),
        filter_empty=_txt(s["filter_empty"]),
        generated_note=_txt(s["generated_note"]),
        stats_section=render_stats_section(projects, s),
        stack_section=render_stack_section(projects, s),
    )


def _write_portfolio(target, projects, warnings, title=None, lang="en"):
    for w in warnings:
        print(f"WARNING: {w}", file=sys.stderr)
    html = build_page(projects, generated_at=datetime.now().strftime("%Y-%m-%d %H:%M"), title=title, lang=lang)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html, encoding="utf-8")
    print(f"PORTFOLIO.html regenerated: {len(projects)} project(s), {len(warnings)} warning(s) -> {target}")


def _resolve_out_arg(raw):
    p = Path(os.path.abspath(os.path.expandvars(os.path.expanduser(raw))))
    return p if p.suffix == ".html" else p / "PORTFOLIO.html"


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    title = None
    changed_dir = None
    write_pages = True
    if argv and argv[0] == "--out":
        if len(argv) < 3:
            print("usage: generate_portfolio.py --out <dir|file> <scope_root> [<scope_root>...]", file=sys.stderr)
            sys.exit(1)
        target = _resolve_out_arg(argv[1])
        scopes = [Path(s) for s in argv[2:]]
        ignore_entries = load_global_trackignore()
        scope_roots = [str(s) for s in scopes]
        write_pages = False
    elif argv and argv[0] == "--changed":
        if len(argv) != 2:
            print("usage: generate_portfolio.py --changed <project_root>", file=sys.stderr)
            sys.exit(1)
        changed_dir = str(Path(argv[1]))
        target = load_portfolio_target()
        if target is None:
            return
        scopes = load_scopes()
        ignore_entries = load_global_trackignore()
        scope_roots = [str(s) for s in scopes]
        title = load_portfolio_title()
    elif argv:
        print("usage: generate_portfolio.py [--out <dir|file> <scope_root>...] [--changed <project_root>]", file=sys.stderr)
        sys.exit(1)
    else:
        target = load_portfolio_target()
        if target is None:
            return  # not configured / off -> silent no-op
        scopes = load_scopes()
        ignore_entries = load_global_trackignore()
        scope_roots = [str(s) for s in scopes]
        title = load_portfolio_title()

    lang = load_portfolio_language()
    projects, warnings = [], []
    for scope in scopes:
        if not Path(scope).is_dir():
            warnings.append(f"{scope}: scope root not found, skipped")
            continue
        ps, ws = collect_projects(scope, ignore_entries, scope_roots)
        projects += ps
        warnings += ws
    _write_portfolio(target, projects, warnings, title=title, lang=lang)
    if write_pages:
        write_subpages(target, projects, changed_dir=changed_dir)
        clean_orphan_subpages(target, projects)


if __name__ == "__main__":
    main()
