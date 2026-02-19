# Test

## test

Run all tests and report status to GitHub.

```bash
bundle exec fastlane test
```

### What it does

1. Installs dependencies (`dependencies` private lane):
    - Selects Xcode version if `XCODE_VERSION` is set
    - Installs Homebrew packages from `Brewfile` or SwiftLint directly
    - Runs `pod install` if a `Podfile` exists
2. Generates GraphQL operations if `APOLLO_CODEGEN_CONFIG_PATH` is set
3. Runs all unit and UI tests via `run_tests` (scan)
4. Runs [Danger](https://danger.systems/ruby/) to report back to the pull request (CI only)

### Environment variables used

| Variable | Purpose |
|----------|---------|
| `APP_SCHEME` | Xcode scheme to test |
| `XCODE_VERSION` | Specific Xcode version to use (optional) |
| `APOLLO_CODEGEN_CONFIG_PATH` | Path to Apollo GraphQL codegen config (optional) |
| `ADDITIONAL_TESTS_SETTINGS` | JSON string with additional `run_tests` parameters (optional) |

### Customizing test settings

Override default test settings by providing a JSON string via `ADDITIONAL_TESTS_SETTINGS`:

```bash
ADDITIONAL_TESTS_SETTINGS='{"destination": "platform=iOS Simulator,name=iPhone 15"}' \
  bundle exec fastlane test
```

See [Helpers](../configuration/helpers.md#tests_settings) for default test configuration.
