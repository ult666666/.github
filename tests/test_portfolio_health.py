"""Offline tests for the public portfolio inventory and its uncertainty rules."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "portfolio_health.py"
spec = importlib.util.spec_from_file_location("portfolio_health", MODULE_PATH)
audit_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit_mod)


def repo(name, *, owner="ult666666", private=False, fork=False, archived=False, homepage=""):
    return {
        "name": name,
        "owner": {"login": owner},
        "private": private,
        "fork": fork,
        "archived": archived,
        "default_branch": "main",
        "html_url": f"https://github.com/{owner}/{name}",
        "homepage": homepage,
        "topics": [],
        "pushed_at": "2026-10-25T00:00:00Z",
    }


class FakeGitHub:
    def __init__(self, *, truncated=False):
        self.repos = [
            repo("alpha", homepage="https://example.org/alpha"),
            repo("beta"),
            repo(".github"),
            repo("secret", private=True),
            repo("fork", fork=True),
            repo("someone-elses-repo", owner="elsewhere"),
        ]
        self.trees = {
            "alpha": [
                "README.md", "LICENSE", "tests/test_core.py",
                ".github/workflows/ci.yml", ".github/dependabot.yml",
                "docs/VERIFICATION.md",
            ],
            "beta": ["README.md", "src/main.py"],
            ".github": ["README.md", "SECURITY.md", "CONTRIBUTING.md"],
        }
        self.truncated = truncated
        self.paths = []

    def __call__(self, path):
        self.paths.append(path)
        if path.startswith("/users/"):
            return self.repos
        if "/git/trees/" in path:
            name = path.split("/")[3]
            return {
                "tree": [{"type": "blob", "path": p} for p in self.trees[name]],
                "truncated": name == "beta" and self.truncated,
            }
        raise AssertionError(f"Unexpected request: {path}")


class PortfolioAuditTests(unittest.TestCase):
    def test_filters_private_forks_and_other_owners(self):
        api = FakeGitHub()
        rows = audit_mod.public_repositories("ult666666", api)
        self.assertEqual([r["name"] for r in rows], [".github", "alpha", "beta"])
        self.assertFalse(any("secret" in p for p in api.paths))

    def test_summary_only_counts_active_projects(self):
        report = audit_mod.audit("ult666666", FakeGitHub())
        self.assertEqual(report["public_repositories"], 3)
        self.assertEqual(report["active_projects"], 2)
        self.assertEqual(report["coverage"]["readme"]["yes"], 2)
        self.assertEqual(report["coverage"]["dependabot"], {"yes": 1, "no": 1, "unknown": 0})
        self.assertEqual(report["coverage"]["has_workflow"]["yes"], 1)
        self.assertEqual(report["coverage"]["test_files"]["yes"], 1)

    def test_inherited_policy_not_falsely_reported_missing(self):
        report = audit_mod.audit("ult666666", FakeGitHub())
        beta = next(r for r in report["repositories"] if r["name"] == "beta")
        self.assertEqual(beta["security_policy"], "inherited")
        self.assertEqual(beta["contributing_guide"], "inherited")

    def test_truncated_tree_uses_unknown_for_absence(self):
        report = audit_mod.audit("ult666666", FakeGitHub(truncated=True))
        beta = next(r for r in report["repositories"] if r["name"] == "beta")
        self.assertIsNone(beta["license"])
        self.assertIsNone(beta["test_files"])
        self.assertIsNone(beta["dependabot"])
        self.assertIsNone(beta["has_workflow"])
        self.assertTrue(beta["readme"])
        self.assertEqual(report["coverage"]["license"]["unknown"], 1)
        self.assertIn("?", audit_mod.markdown(report))

    def test_detects_common_test_conventions(self):
        positives = ["tests/a.py", "test/test_x.py", "src/a.test.ts", "src/a.spec.tsx", "pkg/foo_test.py"]
        negatives = ["docs/testing.md", "src/contest.py", "src/testimonials.ts"]
        for path in positives:
            with self.subTest(path=path):
                self.assertTrue(audit_mod.is_test_file(path))
        for path in negatives:
            with self.subTest(path=path):
                self.assertFalse(audit_mod.is_test_file(path))

    def test_markdown_is_scoped_and_caveated(self):
        report = audit_mod.audit("ult666666", FakeGitHub())
        rendered = audit_mod.markdown(report)
        self.assertIn("not a security rating", rendered)
        self.assertIn("[alpha](https://github.com/ult666666/alpha)", rendered)
        self.assertNotIn("| [.github]", rendered)
        self.assertIn("Dependency version-update automation", rendered)

    def test_cli_writes_machine_and_human_reports(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(audit_mod, "api_client", return_value=FakeGitHub()):
                self.assertEqual(audit_mod.main(["--output-dir", tmp]), 0)
            data = json.loads((Path(tmp) / "portfolio-health.json").read_text())
            self.assertEqual(data["active_projects"], 2)
            self.assertTrue((Path(tmp) / "portfolio-health.md").is_file())

    def test_unexpected_api_shape_fails_closed(self):
        with self.assertRaises(ValueError):
            audit_mod.public_repositories("ult666666", lambda _: {"message": "bad"})

    def test_missing_tree_fails_closed(self):
        api = FakeGitHub()
        def invalid(path):
            if "/alpha/git/trees/" in path:
                return {"tree": None}
            return api(path)
        with self.assertRaises(ValueError):
            audit_mod.audit("ult666666", invalid)


if __name__ == "__main__":
    unittest.main()
