# Public portfolio maintenance playbook

This is a sustainable review process for [@ult666666's public repositories](https://github.com/ult666666). It is designed to make claims verifiable and maintenance predictable, without treating a GitHub activity streak or a numerical "portfolio score" as evidence of engineering quality.

## Operating principles

- **Public-only and read-only inventory.** The weekly auditor uses GitHub's public API. It does not enumerate private repositories, edit code, file issues or send notifications. Reports are retained as workflow artifacts for 30 days.
- **Evidence over badges.** A README, test file or workflow is only a signpost. A reviewer must still run the documented command, inspect representative failures and check whether CI passed.
- **Accurate scope.** Distinguish deployed demos from local prototypes, recorded/synthetic evaluations from live systems, and research architectures from execution services. Keep the date and limitations of evidence visible.
- **No automatic licensing.** Missing `LICENSE` is a prompt for an ownership and licensing decision, not permission to apply MIT or any other license.
- **No secret or personal data in demos.** Use synthetic fixtures and redact machine-specific paths, account identifiers, credentials and private repository details before publication.
- **Reviewable changes.** Make small, tested pull requests; do not auto-merge dependency upgrades or change branch rules across projects without project-specific verification.

## Weekly: inspect the read-only report (10–20 minutes)

1. Open the [Public portfolio health audit](https://github.com/ult666666/.github/actions/workflows/portfolio-health.yml) workflow. The schedule is Mondays at 14:23 UTC; use **Run workflow** for an immediate snapshot.
2. Read the workflow summary and download the JSON/Markdown artifact. Treat a `?` as incomplete API evidence, not as a missing file. If the job fails, inspect the API error before drawing conclusions.
3. Review changed findings since the last artifact. Check recent CI **runs**, dependency/security alerts, broken demo links, release download links and published site health separately; the inventory does not verify these.
4. Open a small issue or PR for a confirmed problem, linking the exact failing run, reproducible command or dated evidence. Prioritize broken user paths and vulnerabilities over cosmetic metadata.

The inventory checks README, test-file presence, workflow-file presence, license-file presence, version-update Dependabot configuration and repository homepage metadata. Inherited community-health files are recognized when the public `.github` repository provides them. It **does not** assert code quality, passing CI, dependency safety, branch protection or deployment health.

## Monthly: maintain dependencies and proof (30–60 minutes)

- Review Dependabot **security alerts** and actual workflow failures first. Decide whether each repository needs ecosystem-specific version-update automation; group safe minor/patch updates and cap PR volume.
- Run the quickstart in a clean environment for each currently showcased project. Capture the exact command, commit, date and observed result, including negative cases and known limitations.
- Recheck demo links and mobile/keyboard paths on the portfolio site. Confirm screenshots and claims still match a public commit or a dated verification record.
- Review open issues and release notes. Mark intentionally frozen projects as such rather than implying ongoing production support.

## Quarterly: curate the professional story

- Keep a focused set of pinned repositories aligned with the roles being pursued. Prefer diverse, inspectable projects with a complete problem → approach → trade-off → validation → limitation narrative.
- Audit the profile README and portfolio catalog for stale links, broken releases, inaccurate numbers and ambiguous deployment language.
- Revisit license and ownership decisions; distinguish original code, AI-assisted work, third-party dependencies and coursework.
- Check whether a visitor can understand each flagship project in under two minutes and reproduce its central result from a documented quickstart.
- Keep private engineering systems and unreleased work out of public case studies unless disclosure has been reviewed.

## Prioritization

| Priority | Evidence that triggers work | Expected outcome |
| --- | --- | --- |
| P0 | Exposed credential, reproducible security issue, broken deployed flagship demo or failing critical check | Contain, fix and verify before promotion |
| P1 | Stale dependency with a supported upgrade path; reproducible regression; missing deterministic check for a key claim | Scoped PR, tests, dated evidence |
| P2 | Ambiguous scope, missing setup steps, broken documentation links or outdated screenshots | Clear, accurate docs and demonstration |
| P3 | Cosmetic polish, extra badges, additional projects without a distinct competency | Defer until higher-value proof is complete |

## Reproduce the audit locally

From a checkout of this `.github` repository, use Python 3.11+:

`python3 -B -m unittest discover -s tests -p 'test_portfolio_health.py' -v`

`python3 -B scripts/portfolio_health.py --owner ult666666 --output-dir audit-output`

Set `GITHUB_TOKEN` in the environment for higher public-API rate limits. Never commit the token or the generated report if it contains details you have not reviewed. The report generator makes only public GET requests and writes local output files.

## Starting baseline (2026-10-25)

A read-only inventory found 22 public repositories, including 20 project repositories with CI workflow files. The public projects have READMEs and CI files, but none of the 22 public repositories had a `.github/dependabot.yml` or `.github/dependabot.yaml` **version-update configuration** at that snapshot. This does **not** mean Dependabot security alerts or security updates are disabled. These counts are dated and should be superseded by the next audit artifact, not repeated indefinitely.
