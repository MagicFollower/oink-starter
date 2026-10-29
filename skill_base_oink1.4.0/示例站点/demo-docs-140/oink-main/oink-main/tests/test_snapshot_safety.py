"""Regression checks for the destructive boundary of snapshot tools."""

import importlib.util
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("measure_baseline", ROOT / "bin/measure-baseline.py")
baseline = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(baseline)


class SnapshotSafety(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.site = self.root / "site"
        self.site.mkdir()
        (self.site / "hugo.yaml").write_text("title: Snapshot fixture\n")
        for args in (("init", "-q", "-b", "main"), ("add", "."),
                     ("-c", "user.name=Test", "-c", "user.email=test@example.org", "commit", "-qm", "fixture")):
            subprocess.run(["git", "-C", str(self.site), *args], check=True)
        (self.site / "uncommitted.txt").write_text("preserve this work\n")

    def test_both_clis_reject_keep_directory_that_would_delete_source(self):
        for script, extra in (("bin/sites/build-all.py", []), ("bin/measure-baseline.py", ["noise"])):
            with self.subTest(script=script):
                result = subprocess.run(
                    [sys.executable, str(ROOT / script), *extra, "--sites", str(self.site), "--keep", str(self.root)],
                    text=True, capture_output=True,
                )
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertIn("snapshot destination overlaps", result.stderr)
                self.assertTrue((self.site / ".git").is_dir())
                self.assertEqual((self.site / "uncommitted.txt").read_text(), "preserve this work\n")

    def test_nested_paths_symlink_aliases_and_other_inputs_are_rejected(self):
        alias = self.root / "alias"
        alias.symlink_to(self.site, target_is_directory=True)
        for destination in (self.site, self.site / "snap", self.root, alias):
            with self.subTest(destination=destination), self.assertRaises(ValueError):
                baseline.validate_snapshot_paths([destination], [self.site])
        with self.assertRaises(ValueError):
            baseline.validate_snapshot_paths([self.root / "safe", self.site], [self.site])

    def test_custom_theme_does_not_remove_the_running_tools_checkout(self):
        checkout = self.root / "checkout" / self.site.name
        (checkout / "bin").mkdir(parents=True)
        script = checkout / "bin/measure-baseline.py"
        shutil.copyfile(ROOT / "bin/measure-baseline.py", script)
        sentinel = checkout / "uncommitted.txt"
        sentinel.write_text("preserve the tool checkout\n")
        theme = self.root / "alternate-theme"
        (theme / "layouts/_shortcodes").mkdir(parents=True)
        (theme / "layouts/_shortcodes/example.html").write_text("example\n")
        result = subprocess.run(
            [sys.executable, str(script), "noise", "--sites", str(self.site),
             "--theme", str(theme), "--keep", str(checkout.parent)],
            text=True, capture_output=True,
        )
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("snapshot destination overlaps", result.stderr)
        self.assertTrue(script.is_file())
        self.assertEqual(sentinel.read_text(), "preserve the tool checkout\n")
        self.assertTrue((self.site / ".git").is_dir())
        self.assertTrue((self.site / "uncommitted.txt").is_file())

    def test_isolated_snapshot_still_works_and_preserves_dirty_source(self):
        destination = self.root / "snapshots/site"
        result = baseline.snapshot_site(self.site, destination)
        self.assertEqual(result["snapshot"], "head")
        self.assertTrue((destination / "hugo.yaml").is_file())
        self.assertFalse((destination / "uncommitted.txt").exists())
        self.assertTrue((self.site / "uncommitted.txt").is_file())


if __name__ == "__main__":
    unittest.main()
