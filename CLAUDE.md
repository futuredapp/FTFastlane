# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is the **public** Futured iOS Fastlane repository. It contains all reusable lane logic for iOS CI/CD, designed to be imported by organizations via `import_from_git`. Organization-specific values (team IDs, emails, certificate repo URLs) are provided through environment variables.

Documentation site: [futuredapp.github.io/ios-fastlane](https://futuredapp.github.io/ios-fastlane)

## Architecture

```
Consumer projects (import from org adapter)
  └── Organization adapter (private, sets ENV vars)
        └── import_from_git: this repo (public)
              └── All lanes, helpers
```

### Key design principle

This Fastfile contains **no organization-specific values**. All credentials, team IDs, and repository URLs are read from ENV variables set by the importing adapter.

## Configuration Helpers

Helper methods establish base settings merged with additional ENV variables for per-project customization:

- `build_settings` — Configures `build_ios_app`. Override with `ENV["ADDITIONAL_BUILD_SETTINGS"]` (JSON)
- `code_signing_settings` — Configures `sync_code_signing` (match). Override with `ENV["ADDITIONAL_CODE_SIGNING_SETTINGS"]` (JSON)
- `tests_settings` — Configures `run_tests` (scan). Override with `ENV["ADDITIONAL_TESTS_SETTINGS"]` (JSON)
- `merge_additional_settings(base, env_key)` — DRY helper for JSON merge pattern used by the above

## Organization-Level ENV Variables

These must be set by the adapter Fastfile before importing:

| Variable | Purpose |
|----------|---------|
| `USER_EMAIL` | Apple ID email for ASC/Developer Portal |
| `TEAM_ID` | Apple Developer Team ID |
| `ASC_TEAM_ID` | App Store Connect Team ID |
| `MATCH_GIT_URL` | Git URL of match certificates repo |
| `MATCH_GIT_BRANCH` | Default branch in certificates repo |
| `DEVICE_LIST_GIT_URL` | Git URL of repo containing device-list.txt |
| `DEVICE_LIST_GIT_BRANCH` | Branch for device-list.txt |

## Project-Level ENV Variables

Set by each consumer project:

- `APP_IDENTIFIER` — Base bundle identifier
- `APP_SCHEME` — Xcode scheme name
- `APP_NAME` — Application name
- `MATCH_PASSWORD` — Password for match certificates
- `VERSION_NUMBER` — Version number (defaults to "1.0.0" for beta)

## Lanes

| Lane | Description |
|------|-------------|
| `provisioning` | Download development certificates and profiles (read-only) |
| `update_provisioning` | Register devices and update debug/beta profiles |
| `update_release_provisioning` | Update release profiles only |
| `test` | Run tests with coverage and Danger |
| `beta` | Build and upload beta to TestFlight |
| `release` | Build and upload release to TestFlight |
| `create_apps` | Create app identifiers and ASC apps |
| `create_apps_for_extension` | Create identifiers for extensions |
| `generate_graphql_operations` | Run Apollo codegen |

## Documentation Site

Built with MkDocs Material. To develop locally:

```bash
pip install -r requirements-docs.txt
mkdocs serve
```

Deployed automatically to GitHub Pages on push to `main` via `.github/workflows/deploy-docs.yml`.

## Required Plugins

- `fastlane-plugin-brew` — Manages Homebrew dependencies
- `fastlane-plugin-versioning` — Sets version and build numbers
