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
        self.assertEqual(gp.render_stats_section([]), "")

    def test_stats_section_shows_real_status_label(self):
        html = gp.render_stats_section([{"status": "active"}, {"status": "active"}])
        self.assertIn("2", html)
        self.assertIn("Active", html)

    def test_stats_section_renders_as_filter_buttons(self):
        html = gp.render_stats_section([{"status": "active"}])
        self.assertIn('<button type="button" class="stat" data-status="active" aria-pressed="false">', html)

    def test_stack_section_empty_when_no_stack_anywhere(self):
        self.assertEqual(gp.render_stack_section([{"status": "active"}]), "")

    def test_stack_section_lists_aggregated_chips_as_filter_buttons(self):
        html = gp.render_stack_section([{"stack": ["Python", "Go"]}])
        self.assertIn('<button type="button" class="chip" data-tech="go" aria-pressed="false">Go</button>', html)
        self.assertIn(
            '<button type="button" class="chip" data-tech="python" aria-pressed="false">Python</button>', html
        )


class RenderCardTests(unittest.TestCase):
    def test_renders_link_for_http_repo(self):
        p = {"project": "P", "status": "active", "last_updated": "2026-08-23", "_path": "p", "repo": "https://example.com/repo"}
        html = gp.render_card(p)
        self.assertIn('<a href="https://example.com/repo"', html)

    def test_suppresses_non_http_repo_scheme(self):
        p = {"project": "P", "status": "active", "last_updated": "2026-08-23", "_path": "p", "repo": "javascript:alert(1)"}
        html = gp.render_card(p)
        self.assertNotIn("<a href=", html)
        self.assertNotIn("javascript:", html)

    def test_absent_repo_renders_no_link(self):
        p = {"project": "P", "status": "active", "last_updated": "2026-08-23", "_path": "p"}
        html = gp.render_card(p)
        self.assertNotIn("<a href=", html)

    def test_data_stack_attribute_is_lowercased_for_matching(self):
        p = {
            "project": "P", "status": "active", "last_updated": "2026-08-23", "_path": "p",
            "stack": ["Python", "FastAPI"],
        }
        html = gp.render_card(p)
        self.assertIn('data-stack="python,fastapi"', html)

    def test_data_stack_attribute_present_without_repo_too(self):
        p = {"project": "P", "status": "active", "last_updated": "2026-08-23", "_path": "p", "stack": ["Go"]}
        html = gp.render_card(p)
        self.assertIn('<article class="card" data-stack="go" data-status="active">', html)

    def test_data_status_attribute_lowercased(self):
        p = {"project": "P", "status": "Paused", "last_updated": "2026-08-23", "_path": "p"}
        html = gp.render_card(p)
        self.assertIn('data-status="paused"', html)

    def test_freshness_shown_for_recent_date(self):
        p = {"project": "P", "status": "active", "last_updated": "2026-08-20", "_path": "p"}
        html = gp.render_card(p, today=date(2026, 8, 23))
        self.assertIn("3 days ago", html)
        self.assertNotIn("freshness-stale", html)

    def test_freshness_flags_stale_projects(self):
        p = {"project": "P", "status": "active", "last_updated": "2026-06-01", "_path": "p"}
        html = gp.render_card(p, today=date(2026, 8, 23))
        self.assertIn("freshness-stale", html)

    def test_freshness_absent_for_unparseable_date(self):
        p = {"project": "P", "status": "active", "last_updated": "n/a", "_path": "p"}
        html = gp.render_card(p, today=date(2026, 8, 23))
        self.assertNotIn("freshness", html)


class RelativeFreshnessTests(unittest.TestCase):
    def test_today_and_yesterday_have_dedicated_labels(self):
        self.assertEqual(gp.relative_freshness("2026-08-23", date(2026, 8, 23)), ("today", False))
        self.assertEqual(gp.relative_freshness("2026-08-22", date(2026, 8, 23)), ("yesterday", False))

    def test_days_label_under_stale_threshold(self):
        label, is_stale = gp.relative_freshness("2026-08-13", date(2026, 8, 23))
        self.assertEqual(label, "10 days ago")
        self.assertFalse(is_stale)

    def test_stale_after_30_days(self):
        label, is_stale = gp.relative_freshness("2026-07-01", date(2026, 8, 23))
        self.assertTrue(is_stale)
        self.assertIn("month", label)

    def test_unparseable_date_returns_none(self):
        self.assertEqual(gp.relative_freshness("not a date", date(2026, 8, 23)), (None, False))

    def test_future_date_returns_none(self):
        self.assertEqual(gp.relative_freshness("2026-09-01", date(2026, 8, 23)), (None, False))


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


class MainTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    @unittest.skip("rewritten in Task 2 (config-driven main)")
    def test_main_writes_portfolio_html(self):
        d = self.root / "ProjA"
        (d / "docs" / "project-tracker").mkdir(parents=True)
        (d / "docs" / "project-tracker" / "STATUS.md").write_text(
            "---\nproject: ProjA\nstatus: active\nlast_updated: 2026-08-23\n"
            "stack: [Python]\nnext_milestone: \"Finish X\"\n---\nOk.\n",
            encoding="utf-8",
        )
        sys.argv = ["generate_portfolio.py", str(self.root)]
        gp.main()
        out = (self.root / "PORTFOLIO.html").read_text(encoding="utf-8")
        self.assertIn("ProjA", out)
        self.assertIn("Finish X", out)
        self.assertIn("Python", out)

    def test_main_exits_cleanly_on_missing_scope_root(self):
        missing = self.root / "does-not-exist"
        sys.argv = ["generate_portfolio.py", str(missing)]
        with self.assertRaises(SystemExit) as ctx:
            gp.main()
        self.assertEqual(ctx.exception.code, 1)

    def test_main_exits_cleanly_when_scope_root_is_a_file(self):
        f = self.root / "not-a-dir"
        f.write_text("x", encoding="utf-8")
        sys.argv = ["generate_portfolio.py", str(f)]
        with self.assertRaises(SystemExit) as ctx:
            gp.main()
        self.assertEqual(ctx.exception.code, 1)


if __name__ == "__main__":
    unittest.main()
