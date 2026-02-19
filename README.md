# Futured iOS Fastlane

Centralized [Fastlane](https://fastlane.tools) configuration for iOS projects. Provides reusable lanes for provisioning, testing, beta/release builds, and App Store Connect management.

## Documentation

Full documentation is available at **[futuredapp.github.io/ios-fastlane](https://futuredapp.github.io/ios-fastlane)**.

## Quick start

This Fastfile is designed to be imported via `import_from_git`. Organizations create a private adapter that sets credentials, then consumer projects import from that adapter.

**Organization adapter** (private repo):

```ruby
ENV["USER_EMAIL"] = "ops@example.com"
ENV["TEAM_ID"] = "YOUR_TEAM_ID"
ENV["ASC_TEAM_ID"] = "YOUR_ASC_TEAM_ID"
ENV["MATCH_GIT_URL"] = "git@github.com:your-org/apple-certificates.git"
ENV["MATCH_GIT_BRANCH"] = "master"
ENV["DEVICE_LIST_GIT_URL"] = "git@github.com:your-org/fastlane.git"
ENV["DEVICE_LIST_GIT_BRANCH"] = "main"

import_from_git(url: "https://github.com/futuredapp/ios-fastlane.git")
```

**Consumer project**:

```ruby
ENV["APP_IDENTIFIER"] = "app.example.myapp"
ENV["APP_SCHEME"] = "MyApp"
ENV["APP_NAME"] = "My App"

import_from_git(url: "git@github.com:your-org/fastlane.git")
```

## Available lanes

| Lane | Description |
|------|-------------|
| `provisioning` | Download development certificates and provisioning profiles |
| `update_provisioning` | Register devices and update profiles |
| `update_release_provisioning` | Update release provisioning profiles |
| `test` | Run tests and report status |
| `beta` | Build and upload beta to TestFlight |
| `release` | Build and upload release to TestFlight |
| `create_apps` | Create app identifiers and App Store Connect apps |
| `create_apps_for_extension` | Create identifiers for app extensions |
| `generate_graphql_operations` | Generate GraphQL models via Apollo |

## Required plugins

- `fastlane-plugin-badge`
- `fastlane-plugin-brew`
- `fastlane-plugin-versioning`

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
