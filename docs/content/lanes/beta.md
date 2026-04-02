### What it does

1. Configures App Store Connect API key
2. Installs dependencies (Xcode version, CocoaPods if needed)
3. Generates GraphQL operations if configured
4. Increments build number based on latest TestFlight build (or uses custom `build_number`)
5. Sets version from `VERSION_NUMBER` env var (default `1.0.0`), or uses custom `version_number`
6. Creates a temporary CI keychain
7. Syncs appstore provisioning profiles for the beta bundle identifier (`.beta` suffix)
8. Builds the app using the **Beta** configuration
9. Uploads the `.ipa` to TestFlight with `CHANGELOG` as the changelog

### Notes

- Beta builds always use Futured's own App Store Connect account (configured via `TEAM_ID` and `ASC_TEAM_ID`)
- The build number auto-increment fetches the latest build from TestFlight and adds 1
- If a custom `build_number` is lower than the latest TestFlight build, a warning is shown but the build proceeds
- Version number suffixes (e.g., `1.0.0-beta`) are stripped to the base version
