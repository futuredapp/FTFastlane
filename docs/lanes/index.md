# Lanes Overview

This section documents all public and private lanes available in the Fastfile.

## Public lanes

These lanes are intended for direct execution by developers or CI.

| Lane | Description |
|------|-------------|
| [`provisioning`](provisioning.md) | Download development certificates and provisioning profiles |
| [`update_provisioning`](provisioning.md#update_provisioning) | Register devices and update all profiles |
| [`update_release_provisioning`](provisioning.md#update_release_provisioning) | Update release provisioning profiles only |
| [`test`](test.md) | Run tests and report status to GitHub |
| [`beta`](beta.md) | Build and upload beta to TestFlight |
| [`release`](release.md) | Build and upload release to TestFlight |
| [`create_apps`](create-apps.md) | Create app identifiers and apps in App Store Connect |
| [`create_apps_for_extension`](create-apps.md#create_apps_for_extension) | Create app identifiers for extensions |
| [`generate_graphql_operations`](generate-graphql-operations.md) | Generate GraphQL models via Apollo |

## Private lanes

These lanes are used internally by public lanes and are not meant to be called directly.

| Lane | Description |
|------|-------------|
| `bump` | Fetch latest build number from TestFlight and increment version/build number |
| `create_apps_online` | Core logic for creating app identifiers and App Store Connect apps |
| `dependencies` | Install Xcode version, Homebrew packages, and CocoaPods |
| `configure_keychain` | Create a temporary CI keychain for code signing |
