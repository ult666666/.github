# Public portfolio improvement log — 2026-10-25

This is a dated implementation record for the public GitHub portfolio. It is not a security certification, production-readiness assessment, or replacement for project-specific tests. The central [maintenance playbook](PORTFOLIO_MAINTENANCE.md) defines ongoing review cadence.

## Verified starting point

The read-only GitHub audit on 2026-10-25 found 22 public repositories, of which 20 were active project repositories. All 20 had a root README, recognizable test files, and at least one workflow file. Seventeen had license files and seventeen had repository homepage metadata. None had a Dependabot version-update configuration at the baseline snapshot. Presence of a workflow or test file is not proof that the code works.

## Completed changes

| Area | Repository | Change | Verification |
| --- | --- | --- | --- |
| Public audit | [.github](https://github.com/ult666666/.github/pull/1) | Weekly public-only inventory, JSON/Markdown artifacts, maintenance playbook and nine offline tests | [Manual run](https://github.com/ult666666/.github/actions/runs/40216839979) succeeded |
| CI maintenance | [.github](https://github.com/ult666666/.github/pull/2) | Updated pinned Actions to Node 24-compatible releases and Ubuntu 24.04 | [Manual run](https://github.com/ult666666/.github/actions/runs/40216839979) succeeded |
| Dependency hygiene | [citecheck](https://github.com/ult666666/citecheck/pull/3) | Monthly uv and GitHub Actions version updates; review-first, limited PR volume | Python 3.12/3.13 PR checks passed |
| Dependency hygiene | [contrastkit](https://github.com/ult666666/contrastkit/pull/4) | Monthly npm workspace and GitHub Actions version updates; review-first, limited PR volume | Node 20/22/24 PR checks and Dependabot configuration validation passed after Prettier fix |
| Dependency hygiene | [LineageGuard](https://github.com/ult666666/lineageguard-datahub-agent/pull/10) | Monthly npm and GitHub Actions version updates; review-first, limited PR volume | Offline, browser, CodeQL and deployment PR checks passed |
| Dependency hygiene | [ledgerline](https://github.com/ult666666/ledgerline/pull/2) | Monthly uv and GitHub Actions version updates; container upgrades intentionally separate | Python 3.12/3.13, PostgreSQL 17 and image smoke checks passed |

These dependency files configure **version-update pull requests**, not automatic upgrades or automatic merging. The update interval is monthly, the limit is two open version-update PRs per ecosystem, and routine minor/patch updates are grouped. Security updates and security alerts are distinct GitHub features.

## Security configuration pilot

On 2026-10-25, GitHub's repository settings API was used to verify and enable **Dependabot security updates** for citecheck, contrastkit and ledgerline. Each reported an enabled state afterward. Their open Dependabot alert lists returned zero items at the time of inspection; this is a dated observation, not proof of zero vulnerabilities.

GitHub CodeQL **default setup** was also enabled for these three repositories, each previously reporting not-configured. The initial analysis runs were started:

- [citecheck initial CodeQL run](https://github.com/ult666666/citecheck/actions/runs/40232481066)
- [contrastkit initial CodeQL run](https://github.com/ult666666/contrastkit/actions/runs/40232495598)
- [ledgerline initial CodeQL run](https://github.com/ult666666/ledgerline/actions/runs/40232498712)

All three initial CodeQL analysis runs completed successfully on 2026-10-25. This confirms the scanner executed, **not** that the projects have no vulnerabilities. Ledgerline had two open high-severity CodeQL findings relating to SHA-256 bearer-key fingerprints; the [security review issue](https://github.com/ult666666/ledgerline/issues/4) remains open and no alert was dismissed. Secret scanning and push protection were already enabled in these three repositories. LineageGuard already had CodeQL default setup and Dependabot security updates enabled before this pilot.

## Additional security hardening

- [Ledgerline PR #5](https://github.com/ult666666/ledgerline/pull/5) added a cryptographically random 32-byte bearer-key generator, CLI tests, and explicit documentation of the risks of weak demo keys and stable client fingerprints. Local tests: 169 passed; GitHub CI passed Python 3.12/3.13, PostgreSQL 17, image smoke and CodeQL. The two original CodeQL findings remain open for design review.
- [Luma Keys security review #1](https://github.com/ult666666/luma-keys/issues/1) tracks the observed disabled secret scanning/push protection settings and the need for a scoped review before enabling them. No setting was changed there.

## Explicit boundaries and next review

- The portfolio website has an active redesign pull request and uncommitted local work. Neither was modified by this maintenance pilot.
- No private repositories were included in the public inventory or changed.
- No licenses were assigned automatically; licensing choices require project-specific ownership and reuse decisions.
- Other public repositories have not yet received version-update configurations. Review the first monthly pilot cycle for PR noise, upgrade failures, and developer effort before expanding.
- The security settings read for Luma Keys showed secret scanning and push protection disabled. Investigate why and review the repository's current security settings before enabling; a Dependabot alert API read also failed due to token scope, so no vulnerability conclusion was drawn.
- Review the GitHub Actions run artifacts and CodeQL initial results, then prioritize failing demos, reproducibility gaps, dependency alerts, and inaccurate public claims over badges or additional projects.

## Rollback

Each Dependabot change can be reverted through a small pull request deleting that repository's .github/dependabot.yml file. GitHub security features can be reverted through the repository's Security and analysis settings, but disabling security protections is not recommended without a specific reason. Reverting these changes does not undo dependency updates that may later be merged separately.
