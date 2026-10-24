# Contributing

Thanks for your interest. These are personal projects maintained by one person, so reviews are best effort, but issues and pull requests are welcome.

## Before you start

- **Small fixes** (typos, broken links, clearer docs) can go straight to a pull request.
- **Anything larger** (new features, behavior changes, refactors): open an issue first so we can agree on the approach before you spend time on it.
- **Security problems**: don't open a public issue. Follow the [security policy](SECURITY.md).

## Making a change

1. Fork the repository and create a branch from `main`.
2. Set up the project with the commands in its README, usually under **Development**.
3. Keep the change focused. One pull request should do one thing.
4. Add or update tests for any behavior you change. A bug fix should come with a test that fails without the fix.
5. Run the repository's checks (tests, lint, type checks, whatever its CI runs) and make sure they pass.
6. Update the README, docs or CHANGELOG when user-visible behavior changes.

## Pull requests

Describe what changes and why, and how you verified it. The pull request template has a short checklist. CI must be green before a merge.

## Data and secrets

The projects use synthetic, fictional or openly licensed public data. Never commit secrets, API keys, personal data or proprietary datasets, including in tests and fixtures.

## License

By contributing, you agree that your contribution is licensed under the license of the repository you contribute to.
