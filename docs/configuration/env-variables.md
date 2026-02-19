# Environment Variables

## Organization-level variables

These must be set by the organization's adapter Fastfile (the private repo that imports `ios-fastlane`).

| Variable | Required | Description |
|----------|----------|-------------|
| `USER_EMAIL` | Yes | Apple ID email for App Store Connect and Developer Portal operations |
| `TEAM_ID` | Yes | Apple Developer Team ID |
| `ASC_TEAM_ID` | Yes | App Store Connect Team ID |
| `MATCH_GIT_URL` | Yes | Git URL of the match certificates repository |
| `MATCH_GIT_BRANCH` | Yes | Default branch in the certificates repository (e.g., `master`) |
| `DEVICE_LIST_GIT_URL` | Yes | Git URL of the repository containing `device-list.txt` |
| `DEVICE_LIST_GIT_BRANCH` | Yes | Branch to check out `device-list.txt` from |

## Project-level variables

These are set by each consumer project's Fastfile or `.env` file.

| Variable | Required | Description |
|----------|----------|-------------|
| `APP_IDENTIFIER` | Yes | Base bundle identifier (e.g., `app.futured.myapp`) |
| `APP_SCHEME` | Yes | Xcode scheme name |
| `APP_NAME` | Yes | Application name for build outputs |
| `MATCH_PASSWORD` | Yes | Password for decrypting match certificates |

## Optional project variables

| Variable | Description |
|----------|-------------|
| `APP_IDENTIFIER_CUSTOMER` | Customer's bundle identifier (for client-owned accounts) |
| `TEAM_ID_CUSTOMER` | Customer's Apple Developer Team ID |
| `ASC_TEAM_ID_CUSTOMER` | Customer's App Store Connect Team ID |
| `CUSTOMERS_BRANCH` | Git branch in certificates repo for customer certificates |
| `APP_EXTENSIONS` | Comma-separated list of app extension names |
| `VERSION_NUMBER` | Marketing version number (defaults to `1.0.0` for beta, tag name for release) |

## CI / build-time variables

| Variable | Description |
|----------|-------------|
| `PR_TITLE` | Pull request title (used as TestFlight changelog for beta builds) |
| `BADGE_DARK` | Set to `"true"` for dark badge overlay on beta app icons |
| `XCODE_VERSION` | Specific Xcode version to select |
| `FL_BUILD_NUMBER_PROJECT` | Path to Xcode project file (if not in root or multiple exist) |
| `APOLLO_CODEGEN_CONFIG_PATH` | Path to Apollo GraphQL codegen config |

## Customization variables

These allow per-project overrides of default action parameters via JSON strings.

| Variable | Affects | Example |
|----------|---------|---------|
| `ADDITIONAL_BUILD_SETTINGS` | `build_ios_app` parameters | `'{"derived_data_path": "./CustomDerivedData"}'` |
| `ADDITIONAL_CODE_SIGNING_SETTINGS` | `sync_code_signing` parameters | `'{"readonly": true}'` |
| `ADDITIONAL_TESTS_SETTINGS` | `run_tests` parameters | `'{"destination": "platform=iOS Simulator,name=iPhone 15"}'` |

## App identifier conventions

| Configuration | Bundle ID |
|---------------|-----------|
| Debug | `APP_IDENTIFIER` |
| Beta | `APP_IDENTIFIER.beta` |
| Release | `APP_IDENTIFIER_CUSTOMER` (if customer account) or `APP_IDENTIFIER` |

App extensions follow the same pattern with the extension name appended (e.g., `APP_IDENTIFIER.beta.widget`).
