# Create Apps

## create_apps

Create app identifiers in Apple Developer Portal and apps in App Store Connect. This lane is safe to run multiple times — it automatically skips apps that already exist.

```bash
bundle exec fastlane create_apps
bundle exec fastlane create_apps skip_release_app:true
bundle exec fastlane create_apps company_name:"Example Inc."
```

### Options

| Option | Type | Description |
|--------|------|-------------|
| `skip_release_app` | Boolean | Skip creating the release app identifier and App Store Connect entry |
| `company_name` | String | Required when creating the very first app on a new App Store Connect account |

### What it creates

| Configuration | Bundle ID | App Name | App Store Connect |
|---------------|-----------|----------|-------------------|
| Debug | `APP_IDENTIFIER` | `APP_NAME` | Identifier only (skip ITC) |
| Beta | `APP_IDENTIFIER.beta` | `APP_NAME BETA` | Identifier + ITC app |
| Release | `APP_IDENTIFIER_CUSTOMER` or `APP_IDENTIFIER` | `APP_NAME` | Identifier + ITC app |

!!! note
    The Debug app identifier is only created when `APP_IDENTIFIER_CUSTOMER` is set or `skip_release_app` is true. Otherwise, the Release identifier serves as the Debug identifier as well.

### Environment variables used

| Variable | Purpose |
|----------|---------|
| `APP_IDENTIFIER` | Base bundle identifier |
| `APP_IDENTIFIER_CUSTOMER` | Customer's bundle identifier (optional) |
| `APP_NAME` | Application name |
| `TEAM_ID_CUSTOMER` | Customer's Apple Developer Team ID (optional) |
| `ASC_TEAM_ID_CUSTOMER` | Customer's App Store Connect Team ID (optional) |

---

## create_apps_for_extension

Create app identifiers for all app extensions defined in `APP_EXTENSIONS`. This is a wrapper around the internal `create_apps_online` lane.

```bash
bundle exec fastlane create_apps_for_extension
bundle exec fastlane create_apps_for_extension skip_release_app:true
```

### Options

| Option | Type | Description |
|--------|------|-------------|
| `skip_release_app` | Boolean | Skip creating release identifiers for extensions |

### What it creates

For each extension in `APP_EXTENSIONS`, it creates identifiers following the same pattern as `create_apps`:

| Configuration | Bundle ID |
|---------------|-----------|
| Debug | `APP_IDENTIFIER.{extension}` |
| Beta | `APP_IDENTIFIER.beta.{extension}` |
| Release | `APP_IDENTIFIER_CUSTOMER.{extension}` or `APP_IDENTIFIER.{extension}` |

### Example

```bash
APP_EXTENSIONS="widget,notification-service" bundle exec fastlane create_apps_for_extension
```

This creates identifiers for both `widget` and `notification-service` extensions across Debug, Beta, and Release configurations.
