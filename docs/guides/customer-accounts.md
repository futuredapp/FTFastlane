# Customer Accounts

Some projects are published under a client's Apple Developer account rather than your organization's own account. This guide covers the setup and workflow for customer-account projects.

## When to use customer accounts

Use a customer account when:

- The client owns the Apple Developer account and App Store Connect listing
- The app must be published under the client's team
- The client provides their own signing certificates

## Configuration

Set these additional environment variables in the consumer project's Fastfile:

```ruby
ENV["APP_IDENTIFIER"] = "app.example.myapp"           # Your internal identifier
ENV["APP_IDENTIFIER_CUSTOMER"] = "com.client.theapp"   # Client's bundle identifier
ENV["APP_SCHEME"] = "MyApp"
ENV["APP_NAME"] = "My App"
ENV["TEAM_ID_CUSTOMER"] = "ABCDEF1234"                 # Client's Apple Developer Team ID
ENV["ASC_TEAM_ID_CUSTOMER"] = "9876543"                # Client's App Store Connect Team ID
ENV["CUSTOMERS_BRANCH"] = "client-name"                # Branch in certificates repo

import_from_git(url: "git@github.com:your-org/fastlane.git")
```

## How it works

### Certificate management

Customer certificates are stored on a separate branch in the shared certificates repository:

- **Own-account apps:** Use `MATCH_GIT_BRANCH` (e.g., `master`)
- **Customer-account apps:** Use `CUSTOMERS_BRANCH` (e.g., `client-name`)

### Lane behavior

The `release` lane automatically detects the account type:

| Setting | Own Account | Customer Account |
|---------|-------------|------------------|
| Bundle ID | `APP_IDENTIFIER` | `APP_IDENTIFIER_CUSTOMER` |
| Team ID | `TEAM_ID` | `TEAM_ID_CUSTOMER` |
| ASC Team ID | `ASC_TEAM_ID` | `ASC_TEAM_ID_CUSTOMER` |
| Certificate branch | `MATCH_GIT_BRANCH` | `CUSTOMERS_BRANCH` |

The `beta` lane always uses the organization's own account (since beta builds are internal).

### App identifiers

| Configuration | Identifier |
|---------------|------------|
| Debug | `APP_IDENTIFIER` |
| Beta | `APP_IDENTIFIER.beta` |
| Release | `APP_IDENTIFIER_CUSTOMER` |

## Initial setup

### 1. Create the customer branch in certificates repo

First time only — create the branch for the customer's certificates:

```bash
bundle exec fastlane update_provisioning include_release:true create_branch:true
```

The `create_branch:true` option tells match to create the branch if it doesn't exist.

### 2. Create app identifiers

```bash
bundle exec fastlane create_apps
```

This creates:

- Debug identifier under your team (`APP_IDENTIFIER`)
- Beta identifier + ITC app under your team (`APP_IDENTIFIER.beta`)
- Release identifier + ITC app under the customer's team (`APP_IDENTIFIER_CUSTOMER`)

### 3. Set up provisioning profiles

```bash
bundle exec fastlane update_provisioning include_release:true
```

## Further reading

- [Futured Engineering Handbook — Customer Account CI Setup](https://futuredapp.github.io/Engineering-Handbook/teams/ios/ios_customer_account/)
