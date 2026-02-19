# Release

## release

Build and upload a release version to TestFlight.

```bash
bundle exec fastlane release
bundle exec fastlane release build_number:42
bundle exec fastlane release version_number:1.2.0
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
5. Sets version from `VERSION_NUMBER` env var, or uses custom `version_number`
6. Creates a temporary CI keychain
7. Syncs appstore provisioning profiles:
    - **Own account:** Uses `MATCH_GIT_BRANCH` and `APP_IDENTIFIER`
    - **Customer account:** Uses `CUSTOMERS_BRANCH` and `APP_IDENTIFIER_CUSTOMER`
8. Builds the app using the **Release** configuration
9. Uploads the `.ipa` to TestFlight

### Environment variables used

| Variable | Purpose |
|----------|---------|
| `APP_IDENTIFIER` | Base bundle identifier |
| `APP_IDENTIFIER_CUSTOMER` | Customer's bundle identifier (optional) |
| `APP_SCHEME` | Xcode scheme to build |
| `APP_NAME` | Output name for the built `.ipa` |
| `APP_EXTENSIONS` | Comma-separated extension names (optional) |
| `MATCH_PASSWORD` | Password for match certificates |
| `VERSION_NUMBER` | Marketing version |
| `CUSTOMERS_BRANCH` | Git branch for customer certificates (optional) |
| `TEAM_ID_CUSTOMER` | Customer's Apple Developer Team ID (optional) |
| `ASC_TEAM_ID_CUSTOMER` | Customer's App Store Connect Team ID (optional) |
| `ADDITIONAL_BUILD_SETTINGS` | JSON string with additional build parameters (optional) |

### Own account vs. customer account

The release lane automatically detects the account type:

- **No `APP_IDENTIFIER_CUSTOMER` set:** Builds with your organization's team ID and uploads to your App Store Connect
- **`APP_IDENTIFIER_CUSTOMER` set:** Uses the customer's team ID, certificate branch, and App Store Connect account

See [Customer Accounts](../guides/customer-accounts.md) for detailed setup instructions.
