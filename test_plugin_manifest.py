#!/usr/bin/env python3
"""Validates the plugin manifests. Run from the repo root:
    python3 -m unittest test_plugin_manifest
"""
import json
import os
import unittest
from pathlib import Path

REPO = Path(__file__).parent
EXPECTED_HOOK_SCRIPTS = {
    "session_start.sh",
    "reminders_sync_trigger.sh",
    "portfolio_regen.sh",
}


def _load(rel):
    return json.loads((REPO / rel).read_text(encoding="utf-8"))


class PluginManifestTests(unittest.TestCase):
    def test_all_three_manifests_parse(self):
        _load(".claude-plugin/plugin.json")
        _load(".claude-plugin/marketplace.json")
        _load("hooks/hooks.json")

    def test_plugin_json_has_core_fields(self):
        p = _load(".claude-plugin/plugin.json")
        for k in ("name", "description", "version"):
            self.assertIn(k, p)
        self.assertEqual(p["name"], "project-tracker")

    def test_marketplace_entry_matches_plugin(self):
        m = _load(".claude-plugin/marketplace.json")
        p = _load(".claude-plugin/plugin.json")
        self.assertEqual(len(m["plugins"]), 1)
        entry = m["plugins"][0]
        self.assertEqual(entry["name"], p["name"])
        self.assertEqual(entry["version"], p["version"])
        self.assertEqual(entry["source"], ".")

    def test_hooks_json_declares_the_three_hooks(self):
        h = _load("hooks/hooks.json")["hooks"]
        cmds = [
            hk["command"]
            for event in h.values()
            for group in event
            for hk in group["hooks"]
        ]
        scripts = {c.rsplit("/", 1)[-1] for c in cmds}
        self.assertEqual(scripts, EXPECTED_HOOK_SCRIPTS)

    def test_hooks_json_commands_point_at_existing_executables(self):
        h = _load("hooks/hooks.json")["hooks"]
        for event in h.values():
            for group in event:
                for hk in group["hooks"]:
                    cmd = hk["command"].replace("${CLAUDE_PLUGIN_ROOT}/", "")
                    path = REPO / cmd
                    self.assertTrue(path.is_file(), f"missing: {cmd}")
                    self.assertTrue(os.access(path, os.X_OK), f"not executable: {cmd}")

    def test_postToolUse_hooks_match_edit_write(self):
        h = _load("hooks/hooks.json")["hooks"]
        for group in h.get("PostToolUse", []):
            self.assertEqual(group.get("matcher"), "Edit|Write")

    def test_config_command_exists(self):
        p = REPO / "commands" / "config.md"
        self.assertTrue(p.is_file())
        self.assertIn("description:", p.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
