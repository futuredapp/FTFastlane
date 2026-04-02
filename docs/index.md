# Futured iOS Fastlane

Centralized [Fastlane](https://fastlane.tools) configuration for iOS projects at Futured. This repository provides reusable lanes for common CI/CD tasks including provisioning, testing, beta/release builds, and App Store Connect management.

<!-- WHATS_NEW_START -->
---

## What's New in 2.0.0

!!! danger "Breaking Changes"

    - Removed plugin `fastlane-plugin-badge`
    - Removed plugin `fastlane-plugin-brew`
    - ENV var `BADGE_DARK` is no longer used
    - ENV var `PR_TITLE` is no longer used

### New

- :material-plus:{ title="Added" } ENV var `CHANGELOG`

[:octicons-arrow-right-24: Full Changelog](changelog.md)

---
<!-- WHATS_NEW_END -->

## How it works

The Fastfile in this repository is designed to be imported by individual iOS projects using Fastlane's `import_from_git` feature. Organizations set their specific values (team IDs, email, certificate repo URL) via environment variables, then import this Fastfile to get all lanes.

```ruby
# Your organization's adapter Fastfile
ENV["USER_EMAIL"] = "ops@example.com"
ENV["TEAM_ID"] = "YOUR_TEAM_ID"
ENV["ASC_TEAM_ID"] = "YOUR_ASC_TEAM_ID"
ENV["MATCH_GIT_URL"] = "git@github.com:your-org/apple-certificates.git"
ENV["MATCH_GIT_BRANCH"] = "master"
ENV["DEVICE_LIST_GIT_URL"] = "git@github.com:your-org/fastlane.git"
ENV["DEVICE_LIST_GIT_BRANCH"] = "main"

import_from_git(url: "https://github.com/futuredapp/ios-fastlane.git")
```

Consumer projects then import from your organization's adapter:

```ruby
ENV["APP_IDENTIFIER"] = "app.futured.myapp"
ENV["APP_SCHEME"] = "MyApp"
ENV["APP_NAME"] = "My App"

import_from_git(url: "git@github.com:your-org/fastlane.git")
```

## Available lanes

| Lane | Description |
|------|-------------|
| [`provisioning`](lanes/provisioning.md) | Download development certificates and provisioning profiles |
| [`test`](lanes/test.md) | Run tests and report status to GitHub |
| [`beta`](lanes/beta.md) | Build and upload beta to TestFlight |
| [`release`](lanes/release.md) | Build and upload release to TestFlight |
| [`create_apps`](lanes/create-apps.md) | Create app identifiers and apps in App Store Connect |
| [`create_apps_for_extension`](lanes/create-apps.md#create_apps_for_extension) | Create app identifiers for extensions |
| [`generate_graphql_operations`](lanes/generate-graphql-operations.md) | Generate GraphQL models via Apollo |

## Required plugins

| Plugin | Purpose |
|--------|---------|
| `fastlane-plugin-versioning` | Sets version and build numbers |

## Quick links

- [Getting Started](guides/getting-started.md) — Set up a new project
- [Environment Variables](configuration/env-variables.md) — Full reference
- [Customer Accounts](guides/customer-accounts.md) — Working with client-owned Apple accounts
- [Futured Engineering Handbook](https://futuredapp.github.io/Engineering-Handbook/teams/ios/ios_ci_cd/#fastlane-configuring)
