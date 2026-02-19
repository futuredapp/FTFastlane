# Beta

## beta

Build and upload a beta version to TestFlight.

```bash
bundle exec fastlane beta
bundle exec fastlane beta build_number:42
bundle exec fastlane beta version_number:1.2.0
```

### Options

| Option | Type | Description |
|--------|------|-------------|
| `build_number` | Integer | Custom build number, skipping auto-increment from TestFlight |
| `version_number` | String | Custom version number, overriding `ENV["VERSION_NUMBER"]` |

### What it does

1. Configures App Store Connect API key
2. Installs dependencies (Xcode version, Homebrew, CocoaPods)
3. Generates GraphQL operations if configured
4. Increments build number based on latest TestFlight build (or uses custom `build_number`)
5. Sets version from `VERSION_NUMBER` env var (default `1.0.0`), or uses custom `version_number`
6. Adds a "BETA" badge to the app icon
7. Creates a temporary CI keychain
8. Syncs appstore provisioning profiles for the beta bundle identifier (`.beta` suffix)
9. Builds the app using the **Beta** configuration
10. Uploads the `.ipa` to TestFlight with `PR_TITLE` as the changelog

### Environment variables used

| Variable | Purpose |
|----------|---------|
| `APP_IDENTIFIER` | Base bundle identifier (`.beta` suffix added automatically) |
| `APP_SCHEME` | Xcode scheme to build |
| `APP_NAME` | Output name for the built `.ipa` |
| `APP_EXTENSIONS` | Comma-separated extension names (optional) |
| `MATCH_PASSWORD` | Password for match certificates |
| `VERSION_NUMBER` | Marketing version (default: `1.0.0`) |
| `PR_TITLE` | Pull request title used as TestFlight changelog |
| `BADGE_DARK` | Set to `"true"` for dark badge overlay (optional) |
| `ADDITIONAL_BUILD_SETTINGS` | JSON string with additional build parameters (optional) |

### Notes

- Beta builds always use Futured's own App Store Connect account (configured via `TEAM_ID` and `ASC_TEAM_ID`)
- The build number auto-increment fetches the latest build from TestFlight and adds 1
- If a custom `build_number` is lower than the latest TestFlight build, a warning is shown but the build proceeds
- Version number suffixes (e.g., `1.0.0-beta`) are stripped to the base version
