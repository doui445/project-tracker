#!/usr/bin/env python3
"""Tests for generate_portfolio.py — stdlib only.
Run with: python3 -m unittest test_generate_portfolio -v
(from the scripts/ folder)
"""
import sys
import tempfile
import unittest
import unittest.mock
from datetime import date
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import generate_portfolio as gp


class ConfigLoaderTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.cfg = self.home / ".claude" / "project-tracker"
        self.cfg.mkdir(parents=True)
        self._env = unittest.mock.patch.dict("os.environ", {"HOME": str(self.home)})
        self._env.start()
        self.addCleanup(self._env.stop)

    def test_load_scopes_reads_absolute_paths_and_skips_comments(self):
        (self.cfg / "scopes.txt").write_text("# c\n\n/a/b\n/c/d/\n", encoding="utf-8")
        self.assertEqual(gp.load_scopes(), [Path("/a/b"), Path("/c/d")])

    def test_load_scopes_missing_file_returns_empty(self):
        self.assertEqual(gp.load_scopes(), [])

    def test_load_global_trackignore_reads_entries(self):
        (self.cfg / "trackignore.txt").write_text("# x\n/a/b\n/c/d/\n", encoding="utf-8")
        self.assertEqual(gp.load_global_trackignore(), ["/a/b", "/c/d"])

    def test_load_portfolio_target_directory_appends_filename(self):
        (self.cfg / "portfolio.txt").write_text("# c\n/tmp/out\n", encoding="utf-8")
        self.assertEqual(gp.load_portfolio_target(), Path("/tmp/out/PORTFOLIO.html"))

    def test_load_portfolio_target_html_line_used_as_is(self):
        (self.cfg / "portfolio.txt").write_text("/tmp/out/custom.html\n", encoding="utf-8")
        self.assertEqual(gp.load_portfolio_target(), Path("/tmp/out/custom.html"))

    def test_load_portfolio_target_expands_tilde(self):
        (self.cfg / "portfolio.txt").write_text("~/Desktop\n", encoding="utf-8")
        self.assertEqual(gp.load_portfolio_target(), self.home / "Desktop" / "PORTFOLIO.html")

    def test_load_portfolio_target_missing_or_comments_only_returns_none(self):
        self.assertIsNone(gp.load_portfolio_target())
        (self.cfg / "portfolio.txt").write_text("# only a comment\n\n", encoding="utf-8")
        self.assertIsNone(gp.load_portfolio_target())

    def test_load_portfolio_target_skips_title_line(self):
        (self.cfg / "portfolio.txt").write_text("title: My stuff\n/tmp/out\n", encoding="utf-8")
        self.assertEqual(gp.load_portfolio_target(), Path("/tmp/out/PORTFOLIO.html"))

    def test_load_portfolio_target_skips_language_line(self):
        (self.cfg / "portfolio.txt").write_text("language: fr\n~/Documents\n", encoding="utf-8")
        self.assertEqual(
            gp.load_portfolio_target(), self.home / "Documents" / "PORTFOLIO.html"
        )

    def test_load_portfolio_title_read(self):
        (self.cfg / "portfolio.txt").write_text("/tmp/out\ntitle:  Foo bar \n", encoding="utf-8")
        self.assertEqual(gp.load_portfolio_title(), "Foo bar")

    def test_load_portfolio_title_returns_none_when_absent(self):
        self.assertIsNone(gp.load_portfolio_title())
        (self.cfg / "portfolio.txt").write_text("/tmp/out\ntitle:   \n", encoding="utf-8")
        self.assertIsNone(gp.load_portfolio_title())

    def test_load_scopes_expands_tilde(self):
        (self.cfg / "scopes.txt").write_text("~/foo\n$HOME/bar\n", encoding="utf-8")
        self.assertEqual(gp.load_scopes(), [self.home / "foo", self.home / "bar"])

    def test_load_language_reads_code(self):
        (self.cfg / "language.txt").write_text("fr\n", encoding="utf-8")
        self.assertEqual(gp.load_language(), "fr")

    def test_load_language_normalises_and_is_case_insensitive(self):
        (self.cfg / "language.txt").write_text("# lang\nFrançais\n", encoding="utf-8")
        self.assertEqual(gp.load_language(), "fr")

    def test_load_language_missing_defaults_to_en(self):
        self.assertEqual(gp.load_language(), "en")

    def test_load_language_unknown_defaults_to_en(self):
        (self.cfg / "language.txt").write_text("kl\n", encoding="utf-8")
        self.assertEqual(gp.load_language(), "en")

    def test_normalise_lang_accepts_the_spec_aliases_only(self):
        for raw in ("en", "EN", "english", "Anglais"):
            self.assertEqual(gp._normalise_lang(raw), "en")
        for raw in ("fr", "FR", "french", "francais", "Français"):
            self.assertEqual(gp._normalise_lang(raw), "fr")
        # ISO 639-2 codes are not in the spec's tolerance list -> default
        self.assertEqual(gp._normalise_lang("eng"), "en")
        self.assertEqual(gp._normalise_lang("fra"), "en")

    def test_load_portfolio_language_from_portfolio_txt(self):
        (self.cfg / "portfolio.txt").write_text("~/Documents\nlanguage: fr\n", encoding="utf-8")
        self.assertEqual(gp.load_portfolio_language(), "fr")

    def test_load_portfolio_language_falls_back_to_global(self):
        (self.cfg / "language.txt").write_text("fr\n", encoding="utf-8")
        (self.cfg / "portfolio.txt").write_text("~/Documents\n", encoding="utf-8")
        self.assertEqual(gp.load_portfolio_language(), "fr")

    def test_load_portfolio_language_defaults_to_en(self):
        self.assertEqual(gp.load_portfolio_language(), "en")

    def test_load_portfolio_language_empty_value_falls_back_to_global(self):
        (self.cfg / "language.txt").write_text("fr\n", encoding="utf-8")
        (self.cfg / "portfolio.txt").write_text("~/Documents\nlanguage:\n", encoding="utf-8")
        self.assertEqual(gp.load_portfolio_language(), "fr")

    def test_load_portfolio_language_empty_value_defaults_to_en(self):
        (self.cfg / "portfolio.txt").write_text("~/Documents\nlanguage:   \n", encoding="utf-8")
        self.assertEqual(gp.load_portfolio_language(), "en")


class ParseFrontmatterTests(unittest.TestCase):
    def test_parses_flat_fields_and_list(self):
        text = (
            "---\n"
            "project: Example\n"
            "status: active\n"
            "stack: [Python, FastAPI]\n"
            "last_updated: 2026-08-23\n"
            "---\n"
            "File body.\n"
        )
        data = gp.parse_frontmatter(text)
        self.assertEqual(data["project"], "Example")
        self.assertEqual(data["status"], "active")
        self.assertEqual(data["stack"], ["Python", "FastAPI"])
        self.assertEqual(data["last_updated"], "2026-08-23")

    def test_returns_none_without_frontmatter(self):
        self.assertIsNone(gp.parse_frontmatter("No frontmatter here.\n"))

    def test_ignores_indented_nested_list_lines(self):
        text = (
            "---\n"
            "project: Example\n"
            "status: active\n"
            "subprojects:\n"
            "  - name: \"api\"\n"
            "    path: \"api\"\n"
            "    tracked: true\n"
            "    git: true\n"
            "    status: archived\n"
            "last_updated: 2026-08-23\n"
            "---\n"
            "Body.\n"
        )
        data = gp.parse_frontmatter(text)
        self.assertEqual(data["status"], "active")
        self.assertEqual(data["last_updated"], "2026-08-23")
        self.assertNotIn("tracked", data)
        self.assertNotIn("- name", data)


class CollectProjectsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def _write_status(self, rel_dir, content):
        d = self.root / rel_dir / "docs" / "project-tracker"
        d.mkdir(parents=True, exist_ok=True)
        (d / "STATUS.md").write_text(content, encoding="utf-8")

    def _collect(self):
        return gp.collect_projects(self.root, gp.load_global_trackignore(), [str(self.root)])

    def test_collects_valid_project(self):
        self._write_status("ProjA", "---\nproject: ProjA\nstatus: active\nlast_updated: 2026-08-23\n---\nOk.\n")
        projects, warnings = self._collect()
        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0]["project"], "ProjA")
        self.assertEqual(warnings, [])

    def test_project_carries_its_category(self):
        self._write_status("WithCat", "---\nproject: WithCat\nstatus: active\nlast_updated: 2026-08-23\ncategory: \"Perso\"\n---\nOk.\n")
        self._write_status("NoCat", "---\nproject: NoCat\nstatus: active\nlast_updated: 2026-08-23\n---\nOk.\n")
        projects, _ = self._collect()
        by_name = {p["project"]: p for p in projects}
        self.assertEqual(by_name["WithCat"]["category"], "Perso")
        self.assertEqual(by_name["NoCat"]["category"], "")

    def test_project_path_is_home_relative_or_absolute(self):
        self._write_status("ProjA", "---\nproject: ProjA\nstatus: active\nlast_updated: 2026-08-23\n---\nOk.\n")
        projects, warnings = self._collect()
        self.assertTrue(projects[0]["_path"].endswith("ProjA"))

    def test_project_carries_its_scope(self):
        self._write_status("ProjA", "---\nproject: ProjA\nstatus: active\nlast_updated: 2026-08-23\n---\nOk.\n")
        projects, warnings = self._collect()
        self.assertEqual(projects[0]["scope"], str(self.root))

    def test_skips_malformed_frontmatter_with_warning(self):
        self._write_status("ProjBad", "No frontmatter.\n")
        self._write_status("ProjGood", "---\nproject: Good\nstatus: active\nlast_updated: 2026-08-23\n---\nOk.\n")
        projects, warnings = self._collect()
        self.assertEqual([p["project"] for p in projects], ["Good"])
        self.assertEqual(len(warnings), 1)
        self.assertIn("ProjBad", warnings[0])

    def test_skips_missing_required_fields_with_warning(self):
        self._write_status("ProjIncomplete", "---\nproject: Incomplete\n---\nOk.\n")
        projects, warnings = self._collect()
        self.assertEqual(projects, [])
        self.assertEqual(len(warnings), 1)

    def test_respects_global_trackignore(self):
        self._write_status("Kept", "---\nproject: Kept\nstatus: active\nlast_updated: 2026-08-23\n---\nOk.\n")
        self._write_status("Skipped", "---\nproject: Skipped\nstatus: active\nlast_updated: 2026-08-23\n---\nOk.\n")
        entries = [str(self.root / "Skipped")]
        projects, _ = gp.collect_projects(self.root, entries, [str(self.root)])
        self.assertEqual([p["project"] for p in projects], ["Kept"])

    def test_scope_root_entry_matches_exactly_only(self):
        self._write_status("Inside", "---\nproject: Inside\nstatus: active\nlast_updated: 2026-08-23\n---\nOk.\n")
        entries = [str(self.root)]  # entry == scope root
        projects, _ = gp.collect_projects(self.root, entries, [str(self.root)])
        self.assertEqual([p["project"] for p in projects], ["Inside"])

    def test_dedupes_nested_status_under_same_project(self):
        self._write_status("ProjA", "---\nproject: ProjA\nstatus: active\nlast_updated: 2026-08-23\n---\nOk.\n")
        self._write_status("ProjA/backend", "---\nproject: ProjA-backend\nstatus: active\nlast_updated: 2026-08-23\n---\nOk.\n")
        projects, warnings = self._collect()
        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0]["project"], "ProjA")
        self.assertEqual(warnings, [])

    def test_flat_status_at_project_root_is_not_discovered(self):
        d = self.root / "ProjFlat"
        d.mkdir()
        (d / "STATUS.md").write_text(
            "---\nproject: ProjFlat\nstatus: active\nlast_updated: 2026-08-23\n---\nOk.\n",
            encoding="utf-8",
        )
        projects, warnings = self._collect()
        self.assertEqual(projects, [])
        self.assertEqual(warnings, [])

    def test_prunes_git_and_node_modules_directories(self):
        self._write_status(".git/some/nested/dir", "---\nproject: GitInternal\nstatus: active\nlast_updated: 2026-08-23\n---\nOk.\n")
        self._write_status("node_modules/some-pkg", "---\nproject: NpmPkg\nstatus: active\nlast_updated: 2026-08-23\n---\nOk.\n")
        self._write_status("ProjGood", "---\nproject: Good\nstatus: active\nlast_updated: 2026-08-23\n---\nOk.\n")
        projects, warnings = self._collect()
        self.assertEqual([p["project"] for p in projects], ["Good"])
        self.assertEqual(warnings, [])

    def test_project_status_unaffected_by_nested_subprojects_list(self):
        self._write_status(
            "ProjWithSubs",
            "---\nproject: ProjWithSubs\nstatus: active\nlast_updated: 2026-08-23\n"
            "subprojects:\n  - name: \"api\"\n    path: \"api\"\n    tracked: true\n"
            "    git: true\n    status: archived\n---\nOk.\n",
        )
        projects, warnings = self._collect()
        self.assertEqual(projects[0]["status"], "active")
        self.assertEqual(warnings, [])

    def test_project_carries_its_absolute_dir(self):
        self._write_status("ProjA", "---\nproject: ProjA\nstatus: active\nlast_updated: 2026-08-23\n---\nOk.\n")
        projects, warnings = self._collect()
        self.assertEqual(warnings, [])
        self.assertEqual(projects[0]["_dir"], str(self.root / "ProjA"))


class AggregateStackTests(unittest.TestCase):
    def test_dedupes_exact_duplicates_and_sorts_case_insensitively(self):
        projects = [
            {"stack": ["Python", "FastAPI"]},
            {"stack": ["Python", "React"]},
        ]
        self.assertEqual(gp.aggregate_stack(projects), ["FastAPI", "Python", "React"])

    def test_ignores_projects_without_stack_field(self):
        projects = [{"stack": ["Go"]}, {}]
        self.assertEqual(gp.aggregate_stack(projects), ["Go"])

    def test_empty_when_no_projects(self):
        self.assertEqual(gp.aggregate_stack([]), [])


class StatusCountsTests(unittest.TestCase):
    def test_counts_by_status_in_stable_order(self):
        projects = [
            {"status": "active"}, {"status": "active"},
            {"status": "paused"}, {"status": "archived"},
        ]
        self.assertEqual(
            gp.status_counts(projects),
            [("active", 2), ("paused", 1), ("archived", 1)],
        )

    def test_unknown_status_appended_after_known_ones(self):
        projects = [{"status": "active"}, {"status": "weird"}]
        self.assertEqual(gp.status_counts(projects), [("active", 1), ("weird", 1)])


class RenderSectionsTests(unittest.TestCase):
    def test_stats_section_empty_when_no_projects(self):
        self.assertEqual(gp.render_stats_section([], gp._strings("en")), "")

    def test_stats_section_shows_real_status_label(self):
        html = gp.render_stats_section([{"status": "active"}, {"status": "active"}], gp._strings("en"))
        self.assertIn("2", html)
        self.assertIn("Active", html)

    def test_stats_section_renders_as_filter_buttons(self):
        html = gp.render_stats_section([{"status": "active"}], gp._strings("en"))
        self.assertIn('<button type="button" class="stat" data-status="active" aria-pressed="false">', html)

    def test_stack_section_empty_when_no_stack_anywhere(self):
        self.assertEqual(gp.render_stack_section([{"status": "active"}], gp._strings("en")), "")

    def test_stack_section_lists_aggregated_chips_as_filter_buttons(self):
        html = gp.render_stack_section([{"stack": ["Python", "Go"]}], gp._strings("en"))
        self.assertIn('<button type="button" class="chip" data-tech="go" aria-pressed="false">Go</button>', html)
        self.assertIn(
            '<button type="button" class="chip" data-tech="python" aria-pressed="false">Python</button>', html
        )


class LocalisationTests(unittest.TestCase):
    def test_freshness_labels_localise(self):
        s = gp._strings("fr")
        self.assertEqual(gp.relative_freshness("2026-08-30", date(2026, 8, 30), s)[0], "aujourd'hui")
        self.assertEqual(gp.relative_freshness("2026-08-29", date(2026, 8, 30), s)[0], "hier")
        self.assertEqual(gp.relative_freshness("2026-08-25", date(2026, 8, 30), s)[0], "il y a 5 jours")
        label, stale = gp.relative_freshness("2026-06-01", date(2026, 8, 30), s)
        self.assertTrue(stale)
        self.assertIn("mois", label)

    def test_card_status_label_localises(self):
        p = {"project": "x", "_path": "~/x", "status": "active", "last_updated": "2026-08-30", "stack": []}
        html_fr = gp.render_card(p, gp._strings("fr"))
        self.assertIn("Actif", html_fr)
        self.assertNotIn(">Active<", html_fr)

    def test_card_meta_labels_localise(self):
        p = {"project": "x", "_path": "~/x", "status": "active", "last_updated": "2026-08-30", "stack": []}
        html_fr = gp.render_card(p, gp._strings("fr"))
        self.assertIn("Prochain jalon", html_fr)
        self.assertIn("Mis à jour", html_fr)

    def test_stats_section_labels_localise(self):
        projects = [{"status": "active"}, {"status": "paused"}]
        html_fr = gp.render_stats_section(projects, gp._strings("fr"))
        self.assertIn("Actif", html_fr)
        self.assertIn("En pause", html_fr)

    def test_stack_section_labels_localise(self):
        html_fr = gp.render_stack_section([{"stack": ["Python"]}], gp._strings("fr"))
        self.assertIn("Stack &amp; outils", html_fr)
        self.assertIn("Filtrer par technologie", html_fr)
        self.assertIn("Clique sur une technologie", html_fr)

    def test_stack_section_title_ampersand_escaped_in_en(self):
        html_en = gp.render_stack_section([{"stack": ["Python"]}], gp._strings("en"))
        self.assertIn("Stack &amp; tools", html_en)
        self.assertNotIn("Stack & tools", html_en)

    def test_strings_tables_have_matching_keys(self):
        for lang in gp.STRINGS:
            self.assertEqual(set(gp.STRINGS[lang]), set(gp.STRINGS["en"]), lang)

    def test_escaping_convention_text_vs_attribute(self):
        # A new locale's strings may carry apostrophes/quotes. Text nodes keep
        # them readable (_txt); attribute values must encode them (_attr).
        self.assertEqual(gp._txt("l'an \"x\""), "l'an \"x\"")
        self.assertEqual(gp._attr("l'an \"x\""), "l&#x27;an &quot;x&quot;")
        # End to end: a repo-name apostrophe lands in an aria-label (attribute)
        # and is encoded; the FR freshness label sits in text and stays plain.
        p = {"project": "O'Brien", "_path": "~/o", "status": "active",
             "last_updated": "2026-08-30", "stack": [], "repo": "https://x/o"}
        html_fr = gp.render_card(p, gp._strings("fr"), today=date(2026, 8, 30))
        self.assertIn('aria-label="Ouvrir le dépôt O&#x27;Brien"', html_fr)
        self.assertIn(">(aujourd'hui)<", html_fr)


class RenderCardTests(unittest.TestCase):
    def test_renders_link_for_http_repo(self):
        p = {"project": "P", "status": "active", "last_updated": "2026-08-23", "_path": "p", "repo": "https://example.com/repo"}
        html = gp.render_card(p, gp._strings("en"))
        self.assertIn('<a href="https://example.com/repo"', html)

    def test_suppresses_non_http_repo_scheme(self):
        p = {"project": "P", "status": "active", "last_updated": "2026-08-23", "_path": "p", "repo": "javascript:alert(1)"}
        html = gp.render_card(p, gp._strings("en"))
        self.assertNotIn("<a href=", html)
        self.assertNotIn("javascript:", html)

    def test_absent_repo_renders_no_link(self):
        p = {"project": "P", "status": "active", "last_updated": "2026-08-23", "_path": "p"}
        html = gp.render_card(p, gp._strings("en"))
        self.assertNotIn("<a href=", html)

    def test_data_stack_attribute_is_lowercased_for_matching(self):
        p = {
            "project": "P", "status": "active", "last_updated": "2026-08-23", "_path": "p",
            "stack": ["Python", "FastAPI"],
        }
        html = gp.render_card(p, gp._strings("en"))
        self.assertIn('data-stack="python,fastapi"', html)

    def test_data_stack_attribute_present_without_repo_too(self):
        p = {"project": "P", "status": "active", "last_updated": "2026-08-23", "_path": "p", "stack": ["Go"]}
        html = gp.render_card(p, gp._strings("en"))
        self.assertIn('<article class="card" data-stack="go" data-status="active">', html)

    def test_data_status_attribute_lowercased(self):
        p = {"project": "P", "status": "Paused", "last_updated": "2026-08-23", "_path": "p"}
        html = gp.render_card(p, gp._strings("en"))
        self.assertIn('data-status="paused"', html)

    def test_freshness_shown_for_recent_date(self):
        p = {"project": "P", "status": "active", "last_updated": "2026-08-20", "_path": "p"}
        html = gp.render_card(p, gp._strings("en"), today=date(2026, 8, 23))
        self.assertIn("3 days ago", html)
        self.assertNotIn("freshness-stale", html)

    def test_freshness_flags_stale_projects(self):
        p = {"project": "P", "status": "active", "last_updated": "2026-06-01", "_path": "p"}
        html = gp.render_card(p, gp._strings("en"), today=date(2026, 8, 23))
        self.assertIn("freshness-stale", html)

    def test_freshness_absent_for_unparseable_date(self):
        p = {"project": "P", "status": "active", "last_updated": "n/a", "_path": "p"}
        html = gp.render_card(p, gp._strings("en"), today=date(2026, 8, 23))
        self.assertNotIn("freshness", html)


class _AnchorNestingChecker(HTMLParser):
    """Tracks open tags on a stack to detect an <a> start tag encountered
    while another <a> is still open. A plain substring check (assertIn on
    the href) cannot see this: HTML5 forbids nested anchors, and a real
    browser auto-closes the outer <a> the instant it hits the nested one
    -- which silently breaks whole-card click-to-repo and strips the
    click target off everything after the nested link. Only parsing the
    tag structure catches that."""
    def __init__(self):
        super().__init__()
        self.stack = []
        self.saw_nested_anchor = False

    def handle_starttag(self, tag, attrs):
        if tag == "a" and "a" in self.stack:
            self.saw_nested_anchor = True
        self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in self.stack:
            while self.stack and self.stack.pop() != tag:
                pass


class TestCardLinksToSubpage(unittest.TestCase):
    def test_render_card_links_to_subpage(self):
        s = gp._strings("en")
        p = {"project": "demo", "_path": "~/demo", "status": "active", "last_updated": "2026-09-01"}
        html = gp.render_card(p, s)
        self.assertIn('href="portfolio/demo.html"', html)

    def test_render_card_with_repo_does_not_nest_anchors(self):
        # Regression: when a repo is set, open_tag/close_tag make the whole
        # card one <a href="{repo}">...</a> -- the sub-page link's own <a>
        # must be a structural sibling of that anchor, never nested inside
        # it (see _AnchorNestingChecker's docstring for why).
        s = gp._strings("en")
        p = {
            "project": "demo", "_path": "~/demo", "status": "active",
            "last_updated": "2026-09-01", "repo": "https://example.com/demo",
        }
        html = gp.render_card(p, s)
        self.assertIn('href="portfolio/demo.html"', html)
        checker = _AnchorNestingChecker()
        checker.feed(html)
        self.assertFalse(checker.saw_nested_anchor, "an <a> must never be nested inside another <a>")


class RelativeFreshnessTests(unittest.TestCase):
    def test_today_and_yesterday_have_dedicated_labels(self):
        self.assertEqual(gp.relative_freshness("2026-08-23", date(2026, 8, 23), gp._strings("en")), ("today", False))
        self.assertEqual(gp.relative_freshness("2026-08-22", date(2026, 8, 23), gp._strings("en")), ("yesterday", False))

    def test_days_label_under_stale_threshold(self):
        label, is_stale = gp.relative_freshness("2026-08-13", date(2026, 8, 23), gp._strings("en"))
        self.assertEqual(label, "10 days ago")
        self.assertFalse(is_stale)

    def test_stale_after_30_days(self):
        label, is_stale = gp.relative_freshness("2026-07-01", date(2026, 8, 23), gp._strings("en"))
        self.assertTrue(is_stale)
        self.assertIn("month", label)

    def test_unparseable_date_returns_none(self):
        self.assertEqual(gp.relative_freshness("not a date", date(2026, 8, 23), gp._strings("en")), (None, False))

    def test_future_date_returns_none(self):
        self.assertEqual(gp.relative_freshness("2026-09-01", date(2026, 8, 23), gp._strings("en")), (None, False))


class TestExtractChangelogLatestVersion(unittest.TestCase):
    CHANGELOG = """## [Unreleased]

### Added
- something not yet released

## [0.2.0] — 2026-09-10

### Added
- feature two

## [0.1.0] — 2026-08-01

### Added
- feature one
"""

    def test_skips_unreleased_returns_first_dated(self):
        version, date_str, body = gp.extract_changelog_latest_version(self.CHANGELOG)
        self.assertEqual(version, "0.2.0")
        self.assertEqual(date_str, "2026-09-10")
        self.assertIn("feature two", body)
        self.assertNotIn("feature one", body)

    def test_no_dated_version_yet(self):
        self.assertIsNone(gp.extract_changelog_latest_version("## [Unreleased]\n\n- x\n"))

    def test_empty_changelog(self):
        self.assertIsNone(gp.extract_changelog_latest_version(""))


class SortByRecencyTests(unittest.TestCase):
    def test_most_recent_first(self):
        projects = [
            {"project": "Old", "last_updated": "2026-01-01"},
            {"project": "New", "last_updated": "2026-08-20"},
            {"project": "Mid", "last_updated": "2026-05-15"},
        ]
        result = gp.sort_by_recency(projects)
        self.assertEqual([p["project"] for p in result], ["New", "Mid", "Old"])

    def test_unparseable_dates_pushed_to_end_but_stable(self):
        projects = [
            {"project": "NoDate1", "last_updated": "n/a"},
            {"project": "Real", "last_updated": "2026-01-01"},
            {"project": "NoDate2", "last_updated": ""},
        ]
        result = gp.sort_by_recency(projects)
        self.assertEqual([p["project"] for p in result], ["Real", "NoDate1", "NoDate2"])


class BuildPageTests(unittest.TestCase):
    def test_build_page_contains_projects_and_generated_at(self):
        projects = [{"project": "Z", "status": "active", "last_updated": "2026-08-23", "_path": "~/x/Z"}]
        html = gp.build_page(projects, generated_at="2026-08-30 12:00")
        self.assertIn("Z", html)
        self.assertIn("2026-08-30 12:00", html)
        self.assertIn('<html lang="en">', html)

    def test_build_page_empty_state_when_no_projects(self):
        html = gp.build_page([], generated_at="2026-08-30 12:00")
        self.assertIn("No tracked projects yet.", html)

    def test_build_page_uses_given_title(self):
        html = gp.build_page(
            [{"project": "Z", "status": "active", "last_updated": "2026-08-23", "_path": "~/x/Z"}],
            generated_at="2026-08-30 12:00", title="Stuff <x> & things",
        )
        self.assertIn("Stuff &lt;x&gt; &amp; things", html)

    def test_build_page_default_title_and_no_section_title(self):
        html = gp.build_page(
            [{"project": "Z", "status": "active", "last_updated": "2026-08-23", "_path": "~/x/Z"}],
            generated_at="2026-08-30 12:00",
        )
        self.assertIn('<p class="tagline">My projects</p>', html)
        self.assertNotIn(">My projects</h2>", html)

    def test_build_page_html_lang_follows_language(self):
        html = gp.build_page([], generated_at="2026-08-30 10:00", lang="fr")
        self.assertIn('<html lang="fr">', html)

    def test_build_page_localizes_chrome(self):
        html = gp.build_page([], generated_at="2026-08-30 10:00", lang="fr")
        self.assertIn("Aucun projet suivi pour l'instant.", html)
        self.assertIn("Rechercher un projet", html)
        self.assertIn("Réinitialiser les filtres", html)
        self.assertIn("Régénéré automatiquement par project-tracker.", html)

    def test_build_page_localized_default_title(self):
        html = gp.build_page([], generated_at="x", title=None, lang="fr")
        self.assertIn("Mes projets", html)

    def test_build_page_localized_meta_line_and_uncategorized(self):
        p = {"project": "x", "_path": "~/x", "status": "active", "last_updated": "2026-08-30", "stack": [], "category": ""}
        html = gp.build_page([p], generated_at="2026-08-30 10:00", lang="fr")
        self.assertIn("1 suivis · 2026-08-30 10:00", html)
        self.assertIn("Sans catégorie", html)


class GroupByCategoryTests(unittest.TestCase):
    def _p(self, name, category=None, last_updated="2026-08-23"):
        d = {"project": name, "status": "active", "last_updated": last_updated, "_path": "~/x/" + name}
        if category is not None:
            d["category"] = category
        return d

    def test_groups_by_category(self):
        html = gp.build_page([self._p("A1", "Alpha"), self._p("B1", "Beta")], generated_at="2026-08-30 12:00")
        self.assertIn('<h3 class="category-title">Alpha</h3>', html)
        self.assertIn('<h3 class="category-title">Beta</h3>', html)

    def test_uncategorized_section_first(self):
        html = gp.build_page([self._p("A1", "Alpha"), self._p("U1")], generated_at="2026-08-30 12:00")
        self.assertLess(html.index(">Uncategorized</h3>"), html.index(">Alpha</h3>"))

    def test_categories_ordered_by_activity(self):
        projects = [self._p("F1", "Fresh", "2026-08-29"), self._p("S1", "Stale", "2026-01-01")]
        html = gp.build_page(projects, generated_at="2026-08-30 12:00")
        self.assertLess(html.index(">Fresh</h3>"), html.index(">Stale</h3>"))

    def test_non_sentinel_treated_as_uncategorized(self):
        html = gp.build_page([self._p("N1", "non")], generated_at="2026-08-30 12:00")
        self.assertIn(">Uncategorized</h3>", html)
        self.assertNotIn(">non</h3>", html)

    def test_empty_state_still_rendered(self):
        html = gp.build_page([], generated_at="2026-08-30 12:00")
        self.assertIn("No tracked projects yet.", html)
        self.assertIn('class="grid"', html)

    def test_category_label_is_stripped(self):
        html = gp.build_page(
            [self._p("A1", " Perso "), self._p("A2", "Perso")], generated_at="2026-08-30 12:00"
        )
        self.assertEqual(html.count('class="category-title"'), 1)
        self.assertIn('<h3 class="category-title">Perso</h3>', html)


class TestSubprojectsSection(unittest.TestCase):
    def test_latest_subproject_changelog_date_reads_first_dated_entry(self):
        with tempfile.TemporaryDirectory() as tmp:
            changelog = Path(tmp) / "CHANGELOG.md"
            changelog.write_text("## [1.0.0] — 2026-05-01\n\n- x\n", encoding="utf-8")
            self.assertEqual(gp.latest_subproject_changelog_date(changelog), "2026-05-01")

    def test_latest_subproject_changelog_date_missing_file(self):
        self.assertIsNone(gp.latest_subproject_changelog_date(Path("/nonexistent/CHANGELOG.md")))

    def test_render_subprojects_section_only_active(self):
        s = gp._strings("en")
        subprojects = [
            {"name": "api", "path": "api", "tracked": True, "git": True, "status": "active"},
            {"name": "old", "path": "old", "tracked": True, "git": True, "status": "archived"},
        ]
        with tempfile.TemporaryDirectory() as tmp:
            project_dir = Path(tmp)
            (project_dir / "api").mkdir()
            (project_dir / "api" / "CHANGELOG.md").write_text("## [1.0.0] — 2026-05-01\n\n- x\n", encoding="utf-8")
            html = gp.render_subprojects_section(subprojects, project_dir, s)
        self.assertIn("api", html)
        self.assertIn("2026-05-01", html)
        self.assertNotIn("old", html)

    def test_render_subprojects_section_empty_when_none_active(self):
        s = gp._strings("en")
        subprojects = [{"name": "old", "path": "old", "tracked": True, "git": True, "status": "archived"}]
        self.assertEqual(gp.render_subprojects_section(subprojects, Path("/tmp"), s), "")

    def test_render_subprojects_section_listed_not_tracked(self):
        s = gp._strings("en")
        subprojects = [{"name": "notes", "path": "notes", "tracked": False, "git": False, "status": "active"}]
        html = gp.render_subprojects_section(subprojects, Path("/tmp"), s)
        self.assertIn(s["subpage_subproject_listed"], html)


class MainTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.cfg = self.home / ".claude" / "project-tracker"
        self.cfg.mkdir(parents=True)
        self._env = unittest.mock.patch.dict("os.environ", {"HOME": str(self.home)})
        self._env.start()
        self.addCleanup(self._env.stop)
        self.scopeA = self.home / "scopeA"
        self.scopeB = self.home / "scopeB"

    def _status(self, scope, rel, name, category=None):
        d = scope / rel / "docs" / "project-tracker"
        d.mkdir(parents=True, exist_ok=True)
        cat_line = f'category: "{category}"\n' if category is not None else ""
        (d / "STATUS.md").write_text(
            f"---\nproject: {name}\nstatus: active\nlast_updated: 2026-08-23\n{cat_line}---\nOk.\n",
            encoding="utf-8",
        )

    def test_no_portfolio_config_is_noop(self):
        (self.cfg / "scopes.txt").write_text(f"{self.scopeA}\n", encoding="utf-8")
        self._status(self.scopeA, "P1", "P1")
        gp.main([])  # must not raise, must not write
        self.assertEqual(list(self.home.rglob("PORTFOLIO.html")), [])

    def test_comments_only_portfolio_config_is_noop(self):
        (self.cfg / "scopes.txt").write_text(f"{self.scopeA}\n", encoding="utf-8")
        (self.cfg / "portfolio.txt").write_text("# not set\n", encoding="utf-8")
        self._status(self.scopeA, "P1", "P1")
        gp.main([])
        self.assertEqual(list(self.home.rglob("PORTFOLIO.html")), [])

    def test_aggregates_all_scopes_to_configured_folder(self):
        out_dir = self.home / "out"
        (self.cfg / "scopes.txt").write_text(f"{self.scopeA}\n{self.scopeB}\n", encoding="utf-8")
        (self.cfg / "portfolio.txt").write_text(f"{out_dir}\n", encoding="utf-8")
        self._status(self.scopeA, "Alpha", "Alpha", category="Work")
        self._status(self.scopeB, "Beta", "Beta")
        gp.main([])
        html = (out_dir / "PORTFOLIO.html").read_text(encoding="utf-8")
        self.assertIn("Alpha", html)
        self.assertIn("Beta", html)
        self.assertIn('<h3 class="category-title">Work</h3>', html)

    def test_explicit_out_mode(self):
        out_dir = self.home / "explicit"
        self._status(self.scopeA, "Gamma", "Gamma")
        gp.main(["--out", str(out_dir), str(self.scopeA)])
        html = (out_dir / "PORTFOLIO.html").read_text(encoding="utf-8")
        self.assertIn("Gamma", html)

    def test_title_from_portfolio_txt(self):
        out_dir = self.home / "out"
        (self.cfg / "scopes.txt").write_text(f"{self.scopeA}\n", encoding="utf-8")
        (self.cfg / "portfolio.txt").write_text(f"{out_dir}\ntitle: My stuff\n", encoding="utf-8")
        self._status(self.scopeA, "P1", "P1")
        gp.main([])
        html = (out_dir / "PORTFOLIO.html").read_text(encoding="utf-8")
        self.assertIn('<p class="tagline">My stuff</p>', html)

    def test_language_from_portfolio_txt(self):
        # `language:` line written FIRST, before the path — also exercises
        # C1 (load_portfolio_target must not treat it as the output path).
        out_dir = self.home / "out"
        (self.cfg / "scopes.txt").write_text(f"{self.scopeA}\n", encoding="utf-8")
        (self.cfg / "portfolio.txt").write_text(f"language: fr\n{out_dir}\n", encoding="utf-8")
        self._status(self.scopeA, "P1", "P1")
        self.assertEqual(gp.load_portfolio_target(), out_dir / "PORTFOLIO.html")
        gp.main([])
        html = (out_dir / "PORTFOLIO.html").read_text(encoding="utf-8")
        self.assertIn('<html lang="fr">', html)

    def test_changed_flag_only_writes_that_projects_subpage(self):
        out_dir = self.home / "out"
        (self.cfg / "scopes.txt").write_text(f"{self.scopeA}\n", encoding="utf-8")
        (self.cfg / "portfolio.txt").write_text(f"{out_dir}\n", encoding="utf-8")
        self._status(self.scopeA, "Alpha", "Alpha")
        self._status(self.scopeA, "Beta", "Beta")
        gp.main(["--changed", str(self.scopeA / "Alpha")])
        self.assertTrue((out_dir / "portfolio" / "Alpha.html").is_file())
        self.assertFalse((out_dir / "portfolio" / "Beta.html").is_file())


class TestRenderMarkdownFragment(unittest.TestCase):
    def test_paragraph_is_wrapped(self):
        self.assertEqual(gp.render_markdown_fragment("hello world"), "<p>hello world</p>")

    def test_heading(self):
        self.assertEqual(gp.render_markdown_fragment("## Title"), "<h2>Title</h2>")

    def test_unordered_list(self):
        html = gp.render_markdown_fragment("- one\n- two")
        self.assertEqual(html, "<ul><li>one</li><li>two</li></ul>")

    def test_ordered_list(self):
        html = gp.render_markdown_fragment("1. first\n2. second")
        self.assertEqual(html, "<ol><li>first</li><li>second</li></ol>")

    def test_bold_and_italic(self):
        html = gp.render_markdown_fragment("**bold** and *italic* and _also italic_")
        self.assertEqual(html, "<p><strong>bold</strong> and <em>italic</em> and <em>also italic</em></p>")

    def test_inline_code_not_interpreted(self):
        html = gp.render_markdown_fragment("use `a*b*c` literally")
        self.assertEqual(html, "<p>use <code>a*b*c</code> literally</p>")

    def test_link(self):
        html = gp.render_markdown_fragment("see [the docs](https://example.com/x?a=1&b=2)")
        self.assertEqual(
            html,
            '<p>see <a href="https://example.com/x?a=1&amp;b=2">the docs</a></p>',
        )

    def test_html_in_source_is_escaped(self):
        html = gp.render_markdown_fragment("a <script> & \"quote\"")
        self.assertEqual(html, "<p>a &lt;script&gt; &amp; \"quote\"</p>")

    def test_blank_lines_separate_paragraphs(self):
        html = gp.render_markdown_fragment("first\n\nsecond")
        self.assertEqual(html, "<p>first</p>\n<p>second</p>")

    def test_empty_input(self):
        self.assertEqual(gp.render_markdown_fragment(""), "")


class TestExtractStatusRoadmapSections(unittest.TestCase):
    STATUS_BODY = """
## Where it stands

Project is in good shape.

### What works

- thing one

## Next 3 actions

1. Do the first thing
2. Do the second thing
"""

    def test_extract_status_overview_stops_before_h3(self):
        self.assertEqual(
            gp.extract_status_overview(self.STATUS_BODY, "en"),
            "Project is in good shape.",
        )

    def test_extract_status_next_actions(self):
        self.assertEqual(
            gp.extract_status_next_actions(self.STATUS_BODY, "en"),
            "1. Do the first thing\n2. Do the second thing",
        )

    def test_extract_status_overview_missing_heading(self):
        self.assertIsNone(gp.extract_status_overview("no headings here", "en"))

    def test_extract_status_overview_french(self):
        body = "## État actuel\n\nÇa avance bien.\n\n## 3 prochaines actions\n\n1. Faire ceci\n"
        self.assertEqual(gp.extract_status_overview(body, "fr"), "Ça avance bien.")

    ROADMAP_IN_PROGRESS = "## Done\n\nstuff\n\n## Phase 3 — in progress\n\nBuilding the thing.\n\n## After Phase 3\n\nlater\n"
    ROADMAP_NO_PHASE = "## Current focus\n\nPick the next feature.\n\n## Unprioritised ideas\n\n- x\n"

    def test_extract_roadmap_current_prefers_in_progress_phase(self):
        self.assertEqual(
            gp.extract_roadmap_current(self.ROADMAP_IN_PROGRESS, "en"),
            "Building the thing.",
        )

    def test_extract_roadmap_current_falls_back_to_current_focus(self):
        self.assertEqual(
            gp.extract_roadmap_current(self.ROADMAP_NO_PHASE, "en"),
            "Pick the next feature.",
        )

    def test_extract_roadmap_current_missing_both(self):
        self.assertIsNone(gp.extract_roadmap_current("## Done\n\nstuff\n", "en"))

    def test_extract_status_next_actions_includes_h3_subsections(self):
        """Verify that ### headings inside "Next 3 actions" are NOT treated as
        boundaries (unlike "Where it stands" which stops before them)."""
        body = "## Next 3 actions\n\n1. First action\n\n### Details\n\nMore info here.\n\n## Later section\n\nignored"
        result = gp.extract_status_next_actions(body, "en")
        # Should include the ### subsection and its content
        self.assertIn("### Details", result)
        self.assertIn("More info here.", result)

    def test_extract_roadmap_current_includes_h3_subsections(self):
        """Verify that ### headings inside "Phase N — in progress" or "Current focus"
        sections are NOT treated as boundaries."""
        body = "## Phase 3 — in progress\n\nBuilding the feature.\n\n### Implementation notes\n\nUse async pattern.\n\n## After Phase 3\n\nignored"
        result = gp.extract_roadmap_current(body, "en")
        # Should include the ### subsection and its content
        self.assertIn("### Implementation notes", result)
        self.assertIn("Use async pattern.", result)


class TestExtractJournalRecentEntries(unittest.TestCase):
    JOURNAL = """## 2026-09-01 — First entry

Did the first thing.

## 2026-09-02 — Second entry

Did the second thing.
Still going.

## 2026-09-03 — Third entry

Did the third thing.
"""

    def test_returns_most_recent_first(self):
        entries = gp.extract_journal_recent_entries(self.JOURNAL, count=3)
        self.assertEqual([e[0] for e in entries], ["2026-09-03", "2026-09-02", "2026-09-01"])
        self.assertEqual([e[1] for e in entries], ["Third entry", "Second entry", "First entry"])

    def test_respects_count(self):
        entries = gp.extract_journal_recent_entries(self.JOURNAL, count=2)
        self.assertEqual([e[0] for e in entries], ["2026-09-03", "2026-09-02"])

    def test_body_captured(self):
        entries = gp.extract_journal_recent_entries(self.JOURNAL, count=1)
        self.assertEqual(entries[0][2], "Did the third thing.")

    def test_multiline_body(self):
        entries = gp.extract_journal_recent_entries(self.JOURNAL, count=3)
        second = [e for e in entries if e[0] == "2026-09-02"][0]
        self.assertEqual(second[2], "Did the second thing.\nStill going.")

    def test_empty_journal(self):
        self.assertEqual(gp.extract_journal_recent_entries("", count=3), [])


class TestParseSubprojects(unittest.TestCase):
    STATUS_TEXT = """---
project: parent
status: active
last_updated: 2026-09-01
subprojects:
  - name: "api"
    path: "api"
    tracked: true
    git: true
    status: active
  - name: "legacy-v1"
    path: "archive/v1"
    tracked: true
    git: true
    status: archived
  - name: "notes"
    path: "notes"
    tracked: false
    git: false
    status: active
---

# STATUS
"""

    def test_parses_all_entries(self):
        entries = gp.parse_subprojects(self.STATUS_TEXT)
        self.assertEqual(len(entries), 3)
        self.assertEqual(entries[0], {
            "name": "api", "path": "api", "tracked": True, "git": True, "status": "active",
        })
        self.assertEqual(entries[1]["status"], "archived")
        self.assertEqual(entries[2]["tracked"], False)

    def test_no_subprojects_key(self):
        text = "---\nproject: p\nstatus: active\nlast_updated: 2026-01-01\n---\n"
        self.assertEqual(gp.parse_subprojects(text), [])

    def test_no_frontmatter_at_all(self):
        self.assertEqual(gp.parse_subprojects("just some text"), [])


class TestBuildSubpage(unittest.TestCase):
    def _make_project_files(self, root):
        docs = root / "docs" / "project-tracker"
        docs.mkdir(parents=True)
        (docs / "STATUS.md").write_text(
            "---\nproject: demo\nstatus: active\nlast_updated: 2026-09-01\n---\n\n"
            "## Where it stands\n\nGoing well.\n\n### What works\n\n- x\n\n"
            "## Next 3 actions\n\n1. Ship it\n",
            encoding="utf-8",
        )
        (docs / "ROADMAP.md").write_text("## Current focus\n\nFinish the thing.\n", encoding="utf-8")
        (docs / "JOURNAL.md").write_text("## 2026-09-01 — Kickoff\n\nStarted.\n", encoding="utf-8")
        (docs / "CHANGELOG.md").write_text("## [0.1.0] — 2026-09-01\n\n### Added\n- first release\n", encoding="utf-8")

    def test_build_subpage_includes_all_sections(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "demo"
            root.mkdir()
            self._make_project_files(root)
            data = {"project": "demo", "repo": "https://github.com/x/demo"}
            html = gp.build_subpage(root, data, "en")
        self.assertIn("demo", html)
        self.assertIn("Going well.", html)
        self.assertIn("Ship it", html)
        self.assertIn("Finish the thing.", html)
        self.assertIn("Kickoff", html)
        self.assertIn("first release", html)
        self.assertIn("https://github.com/x/demo", html)
        self.assertNotIn("- x", html)  # the "### What works" bullet must not leak in

    def test_build_subpage_omits_missing_sections(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "bare"
            root.mkdir()
            (root / "docs" / "project-tracker").mkdir(parents=True)
            (root / "docs" / "project-tracker" / "STATUS.md").write_text(
                "---\nproject: bare\nstatus: active\nlast_updated: 2026-09-01\n---\n\n"
                "## Where it stands\n\nJust started.\n\n## Next 3 actions\n\n1. Do a thing\n",
                encoding="utf-8",
            )
            html = gp.build_subpage(root, {"project": "bare"}, "en")
        self.assertNotIn(gp._strings("en")["subpage_view_repo"], html)
        self.assertNotIn(gp._strings("en")["subpage_current_phase"], html)
        self.assertNotIn(gp._strings("en")["subpage_recent_activity"], html)

    def test_build_subpage_french(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "demo"
            root.mkdir()
            docs = root / "docs" / "project-tracker"
            docs.mkdir(parents=True)
            (docs / "STATUS.md").write_text(
                "---\nproject: demo\nstatus: active\nlast_updated: 2026-09-01\n---\n\n"
                "## État actuel\n\nÇa avance.\n\n## 3 prochaines actions\n\n1. Continuer\n",
                encoding="utf-8",
            )
            html = gp.build_subpage(root, {"project": "demo"}, "fr")
        self.assertIn("Ça avance.", html)
        self.assertIn("Retour au portfolio", html)


class TestWriteSubpagesAndCleanup(unittest.TestCase):
    def _project(self, tmp, slug, lang=None):
        root = Path(tmp) / slug
        docs = root / "docs" / "project-tracker"
        docs.mkdir(parents=True)
        (docs / "STATUS.md").write_text(
            f"---\nproject: {slug}\nstatus: active\nlast_updated: 2026-09-01\n---\n\n"
            "## Where it stands\n\nFine.\n\n## Next 3 actions\n\n1. x\n",
            encoding="utf-8",
        )
        data = {"project": slug, "_dir": str(root)}
        if lang:
            data["language"] = lang
        return data

    def test_write_subpages_writes_one_file_per_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            out_dir.mkdir()
            target = out_dir / "PORTFOLIO.html"
            projects = [self._project(tmp, "alpha"), self._project(tmp, "beta")]
            gp.write_subpages(target, projects, changed_dir=None)
            self.assertTrue((out_dir / "portfolio" / "alpha.html").is_file())
            self.assertTrue((out_dir / "portfolio" / "beta.html").is_file())

    def test_write_subpages_targeted_only_writes_changed_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            out_dir.mkdir()
            target = out_dir / "PORTFOLIO.html"
            alpha = self._project(tmp, "alpha")
            beta = self._project(tmp, "beta")
            gp.write_subpages(target, [alpha, beta], changed_dir=alpha["_dir"])
            self.assertTrue((out_dir / "portfolio" / "alpha.html").is_file())
            self.assertFalse((out_dir / "portfolio" / "beta.html").is_file())

    def test_clean_orphan_subpages_removes_unmatched_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            sub_dir = out_dir / "portfolio"
            sub_dir.mkdir(parents=True)
            (sub_dir / "alpha.html").write_text("x", encoding="utf-8")
            (sub_dir / "gone.html").write_text("x", encoding="utf-8")
            target = out_dir / "PORTFOLIO.html"
            gp.clean_orphan_subpages(target, [{"project": "alpha"}])
            self.assertTrue((sub_dir / "alpha.html").is_file())
            self.assertFalse((sub_dir / "gone.html").is_file())

    def test_clean_orphan_subpages_noop_when_dir_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "PORTFOLIO.html"
            gp.clean_orphan_subpages(target, [])  # must not raise


if __name__ == "__main__":
    unittest.main()
