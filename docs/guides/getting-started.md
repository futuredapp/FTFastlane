# Getting Started

This guide walks through setting up a new iOS project to use the shared Fastlane configuration.

## Prerequisites

- [Fastlane](https://fastlane.tools) installed
- Access to your organization's certificate repository (match)
- Apple Developer account membership

## 1. Create an organization adapter (one-time)

If your organization doesn't already have an adapter repository, create one. This private repository sets organization-specific values and imports the public `ios-fastlane` Fastfile.

Create `fastlane/Fastfile` in your adapter repo:

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

An example adapter is available in `fastlane/adapter/Fastfile.example`.

## 2. Set up the consumer project

In your iOS project, create `fastlane/Fastfile`:

```ruby
ENV["APP_IDENTIFIER"] = "app.example.myapp"
ENV["APP_SCHEME"] = "MyApp"
ENV["APP_NAME"] = "My App"

import_from_git(url: "git@github.com:your-org/fastlane.git")
```

## 3. Set secrets

Configure these in your CI environment or local `.env` file:

```bash
MATCH_PASSWORD=your_match_password
```

For beta/release builds, also configure the App Store Connect API key.

## 4. Create app identifiers

Run the create apps lane to register identifiers in the Apple Developer Portal and App Store Connect:

```bash
bundle exec fastlane create_apps
```

If the app has extensions, set `APP_EXTENSIONS` in your project's Fastfile:

```ruby
ENV["APP_EXTENSIONS"] = "widget,notification-service"
```

Then run:

```bash
bundle exec fastlane create_apps_for_extension
```

## 5. Generate provisioning profiles

```bash
bundle exec fastlane update_provisioning include_release:true
```

## 6. Verify setup

Test that provisioning works correctly:

```bash
bundle exec fastlane provisioning
```

## 7. Configure CI

Set up your CI pipeline to run these lanes:

- **On pull request:** `bundle exec fastlane test`
- **On merge to develop/nightly:** `bundle exec fastlane beta`
- **On release tag:** `bundle exec fastlane release`

See the [Futured CI/CD Workflows](https://futuredapp.github.io/.github) documentation for ready-to-use GitHub Actions workflows.

## Device management

To add a new device:

1. Add the device entry to `device-list.txt` in your organization's adapter repository
2. Run `bundle exec fastlane update_provisioning` in the target project
3. Commit the updated provisioning profiles in the certificates repository

Device list format (tab-separated):

```
Device ID	Device Name	Device Platform
{UDID}	{Name}	ios
```
