### What it does

1. Configures App Store Connect API key
2. Installs dependencies (Xcode version, CocoaPods if needed)
3. Generates GraphQL operations if configured
4. Increments build number based on latest TestFlight build (or uses custom `build_number`)
5. Sets version from `VERSION_NUMBER` env var, or uses custom `version_number`
6. Creates a temporary CI keychain
7. Syncs appstore provisioning profiles:
    - **Own account:** Uses `MATCH_GIT_BRANCH` and `APP_IDENTIFIER`
    - **Customer account:** Uses `CUSTOMERS_BRANCH` and `APP_IDENTIFIER_CUSTOMER`
8. Builds the app using the Xcode scheme's default configuration
9. Uploads the `.ipa` to TestFlight (no changelog — unlike beta, release builds do not include TestFlight release notes)

### Own account vs. customer account

The release lane automatically detects the account type:

- **No `APP_IDENTIFIER_CUSTOMER` set:** Builds with your organization's team ID and uploads to your App Store Connect
- **`APP_IDENTIFIER_CUSTOMER` set:** Uses the customer's team ID, certificate branch, and App Store Connect account

See [Customer Accounts](../guides/customer-accounts.md) for detailed setup instructions.
