# Provisioning

## provisioning

Download development certificates and provisioning profiles in read-only mode.

```bash
bundle exec fastlane provisioning
```

**Purpose:** Set up a local development machine without needing write access to the certificates repository.

### What it does

1. Syncs code signing certificates and profiles from the match repository (`ENV["MATCH_GIT_URL"]`)
2. Downloads development-type profiles for all bundle identifiers (main app + extensions)
3. Read-only mode — does not modify the certificates repository

### Environment variables used

| Variable | Purpose |
|----------|---------|
| `APP_IDENTIFIER` | Base bundle identifier |
| `APP_EXTENSIONS` | Comma-separated list of extension names (optional) |
| `MATCH_PASSWORD` | Password for decrypting match certificates |

---

## update_provisioning

Register new devices and update development + beta provisioning profiles.

```bash
bundle exec fastlane update_provisioning
bundle exec fastlane update_provisioning include_release:true
bundle exec fastlane update_provisioning include_release:true create_branch:true
```

### Options

| Option | Type | Description |
|--------|------|-------------|
| `include_release` | Boolean | Also update release certificate and provisioning profiles |
| `create_branch` | Boolean | Create the customer branch in the certificates repo if it doesn't exist |

### What it does

1. Clones the device list from `ENV["DEVICE_LIST_GIT_URL"]` (branch `ENV["DEVICE_LIST_GIT_BRANCH"]`)
2. Registers devices from `device-list.txt` to the Apple Developer Portal
3. Syncs development profiles for Debug configuration
4. Syncs appstore profiles for Beta configuration (`.beta` suffix)
5. If `include_release: true` — syncs appstore profiles for Release configuration

### Environment variables used

| Variable | Purpose |
|----------|---------|
| `APP_IDENTIFIER` | Base bundle identifier |
| `APP_EXTENSIONS` | Comma-separated extension names (optional) |
| `MATCH_PASSWORD` | Password for match certificates |
| `DEVICE_LIST_GIT_URL` | Git URL of the repository containing `device-list.txt` |
| `DEVICE_LIST_GIT_BRANCH` | Branch to check out `device-list.txt` from |

---

## update_release_provisioning

Update only release provisioning profiles.

```bash
bundle exec fastlane update_release_provisioning
bundle exec fastlane update_release_provisioning create_branch:true
```

### Options

| Option | Type | Description |
|--------|------|-------------|
| `create_branch` | Boolean | Create the customer branch in the certificates repo if it doesn't exist |

### What it does

**For own-account apps** (no `APP_IDENTIFIER_CUSTOMER`):

- Syncs appstore profiles from the main match branch for `APP_IDENTIFIER`

**For customer-account apps** (with `APP_IDENTIFIER_CUSTOMER`):

- Syncs appstore profiles from `CUSTOMERS_BRANCH` (or falls back to `MATCH_GIT_BRANCH`) for `APP_IDENTIFIER_CUSTOMER`

### Environment variables used

| Variable | Purpose |
|----------|---------|
| `APP_IDENTIFIER` | Base bundle identifier (own account) |
| `APP_IDENTIFIER_CUSTOMER` | Customer's bundle identifier (optional) |
| `TEAM_ID_CUSTOMER` | Customer's Apple Developer Team ID (optional) |
| `CUSTOMERS_BRANCH` | Git branch for customer certificates (optional) |
