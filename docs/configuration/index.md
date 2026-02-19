# Configuration

The Fastfile is configured entirely through environment variables and helper methods. This section covers:

- [Environment Variables](env-variables.md) — Full reference of all ENV vars
- [Helpers](helpers.md) — Configurable helper methods (`build_settings`, `code_signing_settings`, `tests_settings`)

## Configuration layers

Configuration flows through three layers:

1. **Organization adapter** — Sets organization-specific values (`USER_EMAIL`, `TEAM_ID`, `MATCH_GIT_URL`, etc.)
2. **Consumer project** — Sets project-specific values (`APP_IDENTIFIER`, `APP_SCHEME`, `APP_NAME`, etc.)
3. **CI environment** — Sets build-time values (`VERSION_NUMBER`, `PR_TITLE`, `MATCH_PASSWORD`, etc.)

All three layers set standard `ENV` variables. Later assignments override earlier ones.
