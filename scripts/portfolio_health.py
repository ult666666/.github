#!/usr/bin/env python3
"""Read-only inventory of an account's public GitHub portfolio.

The report describes observable repository metadata and file presence, not the
quality, correctness, or security of the code. No GitHub writes are performed.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

API = "https://api.github.com"
GetJSON = Callable[[str], Any]
META_REPOSITORIES = {".github"}


def api_client(token: str | None = None) -> GetJSON:
    """Build a small GitHub REST client without printing credentials."""
    def get(path: str) -> Any:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "public-portfolio-health-audit/1.0",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        request = Request(API + path, headers=headers)
        try:
            with urlopen(request, timeout=25) as response:
                return json.load(response)
        except HTTPError as exc:
            raise RuntimeError(
                f"GitHub API returned HTTP {exc.code} for {path}"
            ) from None
        except (URLError, TimeoutError) as exc:
            raise RuntimeError(f"GitHub API unavailable for {path}: {type(exc).__name__}") from None
    return get


def public_repositories(owner: str, get: GetJSON) -> list[dict[str, Any]]:
    """Enumerate only public, non-fork repositories; never query private repos."""
    found: list[dict[str, Any]] = []
    for page in range(1, 11):
        path = f"/users/{quote(owner, safe='')}/repos?per_page=100&page={page}&type=owner"
        response = get(path)
        if not isinstance(response, list):
            raise ValueError(f"Expected a repository list from {path}")
        for repo in response:
            if repo.get("private") or repo.get("fork"):
                continue
            if repo.get("owner", {}).get("login", "").lower() != owner.lower():
                continue
            found.append(repo)
        if len(response) < 100:
            break
    else:
        raise RuntimeError("More than 1,000 repositories; adjust pagination before trusting the report")
    return sorted(found, key=lambda item: item["name"].lower())


def tree_paths(owner: str, repo: dict[str, Any], get: GetJSON) -> tuple[set[str], bool]:
    branch = quote(repo["default_branch"], safe="")
    path = f"/repos/{quote(owner, safe='')}/{quote(repo['name'], safe='')}/git/trees/{branch}?recursive=1"
    response = get(path)
    if not isinstance(response, dict) or not isinstance(response.get("tree"), list):
        raise ValueError(f"Missing Git tree for {owner}/{repo['name']}")
    files = {item["path"] for item in response["tree"] if item.get("type") == "blob"}
    return files, bool(response.get("truncated"))


def is_test_file(path: str) -> bool:
    lower = path.lower()
    return (
        lower.startswith(("tests/", "test/", "__tests__/"))
        or "/tests/" in lower
        or lower.endswith((".test.ts", ".test.tsx", ".spec.ts", ".spec.tsx", "_test.py"))
        or lower.rsplit("/", 1)[-1] == "test.py"
    )


def summarize_repository(
    owner: str, repo: dict[str, Any], files: set[str], truncated: bool,
    inherited: dict[str, bool],
) -> dict[str, Any]:
    name = repo["name"]
    root_files = {p.lower() for p in files if "/" not in p}
    workflow_files = sorted(
        p for p in files
        if p.startswith(".github/workflows/") and p.endswith((".yml", ".yaml"))
    )
    def known(value: bool) -> bool | None:
        return None if truncated and not value else value

    is_meta = name in META_REPOSITORIES or name.lower() == owner.lower()
    security_local = "security.md" in root_files or ".github/SECURITY.md" in files
    contributing_local = "contributing.md" in root_files or ".github/CONTRIBUTING.md" in files
    return {
        "name": name,
        "url": repo["html_url"],
        "is_meta": is_meta,
        "archived": bool(repo.get("archived")),
        "pushed_at": repo.get("pushed_at"),
        "homepage": bool(repo.get("homepage")),
        "topics": repo.get("topics") or [],
        "tree_truncated": truncated,
        "readme": known(any(p.startswith("readme.") or p == "readme" for p in root_files)),
        "license": known(any(p == "license" or p.startswith(("license.", "copying.")) for p in root_files)),
        "test_files": known(any(is_test_file(p) for p in files)),
        "workflow_files": workflow_files,
        "has_workflow": known(bool(workflow_files)),
        "dependabot": known(
            ".github/dependabot.yml" in files or ".github/dependabot.yaml" in files
        ),
        "security_policy": "local" if security_local else (
            "inherited" if inherited.get("security") else ("unknown" if truncated else "not_found")
        ),
        "contributing_guide": "local" if contributing_local else (
            "inherited" if inherited.get("contributing") else ("unknown" if truncated else "not_found")
        ),
    }


def audit(owner: str, get: GetJSON) -> dict[str, Any]:
    repositories = public_repositories(owner, get)
    trees: dict[str, tuple[set[str], bool]] = {}
    for repo in repositories:
        trees[repo["name"]] = tree_paths(owner, repo, get)

    default_files = trees.get(".github", (set(), False))[0]
    inherited = {
        "security": "SECURITY.md" in default_files or ".github/SECURITY.md" in default_files,
        "contributing": "CONTRIBUTING.md" in default_files or ".github/CONTRIBUTING.md" in default_files,
    }
    rows = [
        summarize_repository(owner, repo, *trees[repo["name"]], inherited)
        for repo in repositories
    ]
    projects = [r for r in rows if not r["is_meta"] and not r["archived"]]
    fields = ("readme", "license", "test_files", "has_workflow", "dependabot", "homepage")
    coverage = {
        field: {
            "yes": sum(r[field] is True for r in projects),
            "no": sum(r[field] is False for r in projects),
            "unknown": sum(r[field] is None for r in projects),
        }
        for field in fields
    }
    return {
        "schema_version": 1,
        "owner": owner,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": "GitHub public REST API",
        "scope": "Public, non-fork repositories; active non-meta repositories in coverage",
        "limitations": [
            "File presence is not evidence of successful execution or security.",
            "A CI workflow file does not imply passing CI; no workflow results are assessed.",
            "A test file does not establish test quality or coverage.",
            "Dependabot configuration refers to version-update YAML; security updates may be enabled in settings.",
            "Inherited security and contributing files are inferred from the owner's public .github repository.",
            "Truncated Git trees produce unknown (null), never a false missing-file finding.",
        ],
        "public_repositories": len(rows),
        "active_projects": len(projects),
        "coverage": coverage,
        "repositories": rows,
    }


def markdown(report: dict[str, Any]) -> str:
    def flag(value: bool | None) -> str:
        return "?" if value is None else ("Yes" if value else "No")

    projects = [r for r in report["repositories"] if not r["is_meta"] and not r["archived"]]
    lines = [
        "# Public GitHub portfolio health audit",
        "",
        f"**Account:** @{report['owner']}  ",
        f"**Collected:** {report['generated_at']}  ",
        f"**Scope:** {report['active_projects']} active public project repositories "
        f"({report['public_repositories']} public repositories total)",
        "",
        "This is an **inventory**, not a security rating, test result or claim of production readiness.",
        "A question mark means the API tree was incomplete and the check is unknown.",
        "",
        "| Project | README | Test files | Workflow | License | Dependabot versions | Homepage |",
        "| --- | :---: | :---: | :---: | :---: | :---: | :---: |",
    ]
    for row in projects:
        label = f"[{row['name']}]({row['url']})"
        lines.append(
            f"| {label} | {flag(row['readme'])} | {flag(row['test_files'])} "
            f"| {flag(row['has_workflow'])} | {flag(row['license'])} "
            f"| {flag(row['dependabot'])} | {flag(row['homepage'])} |"
        )
    lines.extend(["", "## Review queue", ""])
    for key, label, advice in [
        ("dependabot", "Dependency version-update automation", "Pilot ecosystem-specific, grouped update PRs and monitor CI noise."),
        ("license", "Licensing decision", "Review intent per repository; do not apply a license automatically."),
        ("has_workflow", "Continuous integration", "Check workflow coverage and execution, not just file presence."),
        ("test_files", "Test evidence", "Confirm runnable tests, negative cases and documented verification."),
        ("homepage", "Discoverability", "Add a truthful demo or case-study URL where one exists."),
    ]:
        counts = report["coverage"][key]
        lines.append(
            f"- **{label}:** {counts['no']} missing, {counts['unknown']} unknown "
            f"of {report['active_projects']} projects. {advice}"
        )
    lines.extend(["", "## Interpretation", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    lines.extend([
        "",
        "The scheduled workflow is read-only: it neither changes repositories nor opens issues.",
        "Review the artifact and create scoped PRs only after checking each project's dependencies and constraints.",
        "",
    ])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--owner", default="ult666666", help="GitHub account login")
    parser.add_argument("--output-dir", default="audit-output", type=Path)
    args = parser.parse_args(argv)
    try:
        report = audit(args.owner, api_client(os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")))
    except (RuntimeError, ValueError, KeyError) as exc:
        print(f"Portfolio audit failed: {exc}", file=sys.stderr)
        return 1
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "portfolio-health.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    rendered = markdown(report)
    (args.output_dir / "portfolio-health.md").write_text(rendered, encoding="utf-8")
    if summary := os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(summary, "a", encoding="utf-8") as file:
            file.write(rendered)
    print(
        f"Audited {report['public_repositories']} public repositories "
        f"({report['active_projects']} active projects); "
        f"reports in {args.output_dir}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
