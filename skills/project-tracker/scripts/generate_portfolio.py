#!/usr/bin/env python3
"""
Régénère PORTFOLIO.html à la racine d'un scope à partir du frontmatter de
chaque STATUS.md trouvé sous ce scope. Aucune dépendance externe (pas de
PyYAML) — le frontmatter est volontairement simple (clé: valeur, une seule
forme de liste) donc un parseur fait main suffit.

Usage: generate_portfolio.py <scope_root>
"""
import os
import re
import sys
from datetime import date, datetime
from html import escape
from pathlib import Path

FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
REQUIRED_FIELDS = ["project", "status", "last_updated"]
STATUS_ORDER = ["active", "paused", "blocked", "archived"]
# Couleurs de badge (texte blanc dessus) — identiques en clair/sombre,
# seul le fond de page change de thème, pas les badges eux-mêmes.
# "paused" en ambre : l'accent de cette palette est bleu, donc ambre
# reste distinct (contrairement à la palette or où il fallait le
# décaler vers le bleu pour la même raison, en miroir).
# "paused" en bleu (pas violet) : l'accent est maintenant violet
# (hue ~293), meme logique que pour "blocked" vs l'ancien accent cuivre.
STATUS_LABELS = {
    "active": ("Actif", "oklch(0.55 0.15 145)"),
    "paused": ("En pause", "oklch(0.55 0.19 255)"),
    "blocked": ("Bloque", "oklch(0.55 0.19 25)"),
    "archived": ("Archive", "oklch(0.50 0.02 270)"),
}


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


def load_trackignore(scope_root):
    ignore_file = scope_root / ".trackignore"
    entries = set()
    if ignore_file.exists():
        for line in ignore_file.read_text(encoding="utf-8").splitlines():
            line = line.strip().rstrip("/")
            if line and not line.startswith("#"):
                entries.add(line)
    return entries


def is_ignored(rel_path, ignored):
    parts = rel_path.parts
    return any("/".join(parts[:i]) in ignored for i in range(1, len(parts) + 1))


PRUNED_DIR_NAMES = {"node_modules", ".venv"}


def _iter_status_files(scope_root):
    """Marche dans l'arborescence de scope_root et rend chaque STATUS.md
    trouve sous <projet>/docs/project-tracker/, en elaguant .git,
    node_modules, .venv et tout dossier dont le nom commence par un point
    avant d'y descendre."""
    for dirpath, dirnames, filenames in os.walk(scope_root):
        dirnames[:] = [
            d for d in dirnames
            if d not in PRUNED_DIR_NAMES and not d.startswith(".")
        ]
        candidate = Path(dirpath) / "docs" / "project-tracker" / "STATUS.md"
        if candidate.is_file():
            yield candidate


def _has_ancestor_in(rel_dir, dirs):
    """True si un ancetre (strict) de rel_dir, relatif a scope_root, est
    lui-meme dans dirs (un autre dossier portant un STATUS.md)."""
    return any(ancestor in dirs for ancestor in rel_dir.parents)


def collect_projects(scope_root):
    ignored = load_trackignore(scope_root)
    projects = []
    warnings = []
    status_paths = sorted(_iter_status_files(scope_root))
    # Deux passes pour eviter toute dependance a l'ordre de tri : on
    # determine d'abord l'ensemble complet des dossiers portant un
    # STATUS.md, puis on ne retient que ceux qui n'ont pas d'ancetre dans
    # ce meme ensemble (le plus haut de chaque chaine gagne).
    all_status_dirs = {p.parent.parent.parent.relative_to(scope_root) for p in status_paths}
    for status_path in status_paths:
        rel = status_path.parent.parent.parent.relative_to(scope_root)
        if _has_ancestor_in(rel, all_status_dirs):
            continue
        if is_ignored(rel, ignored):
            continue
        text = status_path.read_text(encoding="utf-8", errors="replace")
        data = parse_frontmatter(text)
        if not data:
            warnings.append(f"{status_path}: pas de frontmatter, ignore")
            continue
        missing = [f for f in REQUIRED_FIELDS if f not in data]
        if missing:
            warnings.append(f"{status_path}: champs manquants {missing}, ignore")
            continue
        data["_path"] = str(rel)
        projects.append(data)
    return projects, warnings


def aggregate_stack(projects):
    """Union dédupliquée (par chaîne exacte) de tous les `stack` des
    projets, triée insensible à la casse. Chaque projet est une source
    réelle — rien n'est inventé ici, juste agrégé."""
    items = set()
    for p in projects:
        for s in p.get("stack", []):
            if s:
                items.add(s)
    return sorted(items, key=str.lower)


def status_counts(projects):
    """Compte les projets par statut. Ordre stable : STATUS_ORDER
    d'abord, puis les statuts non prévus par ordre alphabétique."""
    counts = {}
    for p in projects:
        s = p.get("status", "?")
        counts[s] = counts.get(s, 0) + 1
    ordered = [(s, counts[s]) for s in STATUS_ORDER if s in counts]
    extra = sorted(s for s in counts if s not in STATUS_ORDER)
    ordered += [(s, counts[s]) for s in extra]
    return ordered


STALE_AFTER_DAYS = 30


def relative_freshness(date_str, today):
    """Étiquette relative ('il y a N jours', 'hier'…) depuis last_updated,
    et un booléen "obsolète" (>= STALE_AFTER_DAYS). Renvoie (None, False)
    si la date ne peut pas être interprétée (jamais d'invention)."""
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None, False
    delta = (today - d).days
    if delta < 0:
        return None, False  # date future : rien de sûr à afficher
    if delta == 0:
        return "aujourd'hui", False
    if delta == 1:
        return "hier", False
    if delta < STALE_AFTER_DAYS:
        return f"il y a {delta} jours", False
    months = max(1, delta // 30)
    label = "il y a ~1 mois" if months == 1 else f"il y a ~{months} mois"
    return label, True


def sort_by_recency(projects):
    """Trie par last_updated décroissant (le plus récent d'abord). Les
    dates non interprétables sont poussées à la fin (tri stable, donc
    leur ordre relatif d'origine est conservé entre elles)."""
    def key(p):
        try:
            d = datetime.strptime(p.get("last_updated", ""), "%Y-%m-%d").date()
            return (0, -d.toordinal())
        except (ValueError, TypeError):
            return (1, 0)
    return sorted(projects, key=key)


def render_card(p, today=None):
    if today is None:
        today = date.today()
    status_key = p.get("status", "")
    label, color = STATUS_LABELS.get(status_key, (status_key or "?", "oklch(0.50 0.02 210)"))
    stack = p.get("stack", [])
    stack_html = "".join(f'<span class="tag">{escape(s)}</span>' for s in stack)
    name = p.get("project", p["_path"])
    repo = p.get("repo", "")
    if not (repo.startswith("http://") or repo.startswith("https://")):
        repo = ""
    milestone = escape(p.get("next_milestone", "")) or "—"
    # Normalisé (minuscules) pour les filtres JS (Stack & outils, Progression)
    # — l'affichage garde la casse d'origine, seul ceci sert au matching.
    stack_attr = escape(",".join(s.lower() for s in stack))
    status_attr = escape(status_key.lower())

    last_updated = p.get("last_updated", "?")
    freshness, is_stale = relative_freshness(last_updated, today)
    freshness_html = ""
    if freshness:
        cls = "freshness freshness-stale" if is_stale else "freshness"
        freshness_html = f' <span class="{cls}">({escape(freshness)})</span>'

    # Toute la carte est la cible cliquable quand un dépôt existe (zone de
    # clic large plutôt qu'un petit lien texte) — mais l'accessible name
    # reste court (aria-label), pas tout le contenu de la carte lu en bloc.
    if repo:
        open_tag = (
            f'<a href="{escape(repo)}" class="card" data-stack="{stack_attr}" '
            f'data-status="{status_attr}" aria-label="Ouvrir le dépôt de {escape(name)}">'
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
        <h2>{escape(name)}</h2>
        <span class="status" style="background:{color}">{escape(label)}</span>
      </header>
      <p class="path">{escape(p["_path"])}</p>
      <div class="tags">{stack_html}</div>
      <dl class="meta">
        <div><dt>Prochain jalon</dt><dd>{milestone}</dd></div>
        <div><dt>Mis à jour</dt><dd>{escape(last_updated)}{freshness_html}</dd></div>
      </dl>
      {affordance}
    {close_tag}"""


EMPTY_STATE = """
    <div class="empty">
      <p class="empty-title">Aucun projet suivi pour l'instant.</p>
      <p class="empty-body">Ouvre une session Claude Code dans un dossier de ce périmètre — le skill <code>project-tracker</code> te proposera de le suivre.</p>
    </div>"""


def render_stats_section(projects):
    if not projects:
        return ""
    # Boutons plutôt que divs statiques : cliquer un statut filtre la
    # grille, même mécanisme que les chips de Stack & outils.
    items = "".join(
        f'<button type="button" class="stat" data-status="{escape(s)}" aria-pressed="false">'
        f'<span class="stat-num">{n}</span>'
        f'<span class="stat-label">{escape(STATUS_LABELS.get(s, (s, ""))[0])}</span></button>'
        for s, n in status_counts(projects)
    )
    return f'<section class="stats" role="group" aria-label="Filtrer par statut">{items}</section>'


def render_stack_section(projects):
    stack = aggregate_stack(projects)
    if not stack:
        return ""
    # Une seule couleur neutre par défaut — la sélection (clic) fait
    # passer une chip en orange ET filtre les cartes qui utilisent cette
    # techno, plutôt qu'une alternance arbitraire sans règle.
    chips = "".join(
        f'<button type="button" class="chip" data-tech="{escape(s.lower())}" '
        f'aria-pressed="false">{escape(s)}</button>'
        for s in stack
    )
    return f"""
<section class="stack-section">
  <h2 class="section-title">Stack &amp; outils</h2>
  <p class="stack-hint">Clique sur une techno pour filtrer les projets qui l'utilisent.</p>
  <div class="stack-chips" role="group" aria-label="Filtrer par technologie">{chips}</div>
</section>"""

PAGE_TEMPLATE = """<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Portfolio de projets</title>
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
      /* anthracite teinté violet plutôt qu'un noir profond — plus
         agréable qu'un "void" quasi pur, et cohérent avec l'accent */
      --bg: oklch(0.170 0.012 293);
      --surface: oklch(0.220 0.016 293);
      --surface-hover: oklch(0.260 0.018 293);
      --border: oklch(0.330 0.016 293);
      --border-strong: oklch(0.410 0.018 293);
      --ink: oklch(0.948 0.005 293);
      --muted: oklch(0.580 0.008 293);
      --accent: oklch(0.714 0.148 293);
      --accent2: oklch(0.750 0.157 42);
      /* teintes bien plus discretes qu'en clair — le meme pourcentage
         d'opacite lit beaucoup plus fort sur un fond quasi noir */
      --accent-tint: oklch(0.714 0.148 293 / 10%);
      --accent-border: oklch(0.714 0.148 293 / 22%);
      --accent2-tint: oklch(0.750 0.157 42 / 10%);
      --accent2-border: oklch(0.750 0.157 42 / 22%);
      /* violet gardé discret (apprécié tel quel) ; orange remonté pour
         avoir plus de présence dans le fond */
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
    /* deux taches radiales, plus grandes et plus presentes, fixes (pas
       d'animation — un fond qui bouge en continu nuit a la lisibilite) */
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
    /* seul transform est anime (GPU-only) ; border-color/box-shadow/
       background changent instantanement sur les etats ci-dessous */
    transition: transform 180ms var(--ease);
    /* entree en escalier — page consultee occasionnellement, pas en
       continu, donc justifie un bref pont plutot qu'un affichage brut */
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
  /* hover uniquement pour les pointeurs precis (souris) — un tap sur
     mobile/tablette ne doit pas laisser la carte "collee" en hover */
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
    grid-column: 1 / -1;
    text-align: center;
    padding: 2.5rem 1.5rem;
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
    /* delight tier — rare (vu une fois, avant le premier projet suivi) */
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
    <p class="tagline">Suivi de mes projets de code — actifs, en pause, ou archivés.</p>
  </div>
  <p class="meta-line">{count} suivi(s) · {generated_at}</p>
</header>
{stats_section}
<h2 class="section-title">Mes projets</h2>
<div class="search-row">
  <input type="search" id="portfolio-search" class="search-input" placeholder="Rechercher un projet…" aria-label="Rechercher un projet par nom">
  <button type="button" id="reset-filters" class="reset-btn" hidden>Réinitialiser les filtres</button>
</div>
<div class="grid">
{cards}
<p class="filter-empty" hidden>Aucun projet ne correspond aux filtres.</p>
</div>
{stack_section}
<p class="generated">Régénéré automatiquement par project-tracker.</p>
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


def main():
    if len(sys.argv) != 2:
        print("usage: generate_portfolio.py <scope_root>", file=sys.stderr)
        sys.exit(1)
    scope_root = Path(sys.argv[1]).resolve()
    if not scope_root.is_dir():
        print(f"erreur: {scope_root} n'existe pas ou n'est pas un dossier", file=sys.stderr)
        sys.exit(1)
    projects, warnings = collect_projects(scope_root)
    for w in warnings:
        print(f"WARNING: {w}", file=sys.stderr)
    projects = sort_by_recency(projects)
    today = date.today()
    cards = "\n".join(render_card(p, today=today) for p in projects) if projects else EMPTY_STATE
    generated_at = datetime.now().strftime("%d/%m/%Y à %H:%M")
    html = PAGE_TEMPLATE.format(
        cards=cards,
        count=len(projects),
        generated_at=generated_at,
        stats_section=render_stats_section(projects),
        stack_section=render_stack_section(projects),
    )
    out_path = scope_root / "PORTFOLIO.html"
    out_path.write_text(html, encoding="utf-8")
    print(f"PORTFOLIO.html regenere : {len(projects)} projet(s), {len(warnings)} avertissement(s)")


if __name__ == "__main__":
    main()
