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
    },
}


def _strings(lang):
    return STRINGS.get(lang, STRINGS["en"])


def _status_label(status_key, s):
    return s.get(f"status_{status_key}", status_key or "?")


def parse_frontmatter(text):
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None
    data = {}
    for line in m.group(1).splitlines():
        line = line.rstrip()
        if not line or line.lstrip().startswith("#") or ":" not in line:
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

    return f"""
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
    {close_tag}"""


def _empty_state(s):
    return f"""
    <div class="empty">
      <p class="empty-title">{_txt(s["empty_title"])}</p>
      <p class="empty-body">{_txt(s["empty_body"])}</p>
    </div>"""


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
    /* staggered entrance — page consulted occasionally, not
       continuously, so a brief bridge is justified rather than a raw display */
    animation: cardIn 280ms var(--ease) both;
  }}
  @keyframes cardIn {{
    from {{ opacity: 0; transform: translateY(8px); }}
  }}
  .card:nth-child(2) {{ animation-delay: 30ms; }}
  .card:nth-child(3) {{ animation-delay: 60ms; }}
  .card:nth-child(4) {{ animation-delay: 90ms; }}
  .card:nth-child(5) {{ animation-delay: 120ms; }}
  .card:nth-child(6) {{ animation-delay: 150ms; }}
  .card:nth-child(7) {{ animation-delay: 180ms; }}
  .card:nth-child(n+8) {{ animation-delay: 210ms; }}
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
  .card[hidden] {{ display: none; }}
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
    .card {{ transition: border-color 120ms linear; animation: none !important; }}
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
      card.hidden = !show;
      if (show) visible++;
    }});
    document.querySelectorAll('.category-group').forEach(function (grp) {{
      var someVisible = Array.prototype.some.call(
        grp.querySelectorAll('.card'), function (c) {{ return !c.hidden; }}
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
    if argv and argv[0] == "--out":
        if len(argv) < 3:
            print("usage: generate_portfolio.py --out <dir|file> <scope_root> [<scope_root>...]", file=sys.stderr)
            sys.exit(1)
        target = _resolve_out_arg(argv[1])
        scopes = [Path(s) for s in argv[2:]]
        ignore_entries = load_global_trackignore()
        scope_roots = [str(s) for s in scopes]
    elif argv:
        print("usage: generate_portfolio.py [--out <dir|file> <scope_root>...]", file=sys.stderr)
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


if __name__ == "__main__":
    main()
