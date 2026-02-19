# Helper Methods

The Fastfile provides several helper methods that configure core Fastlane actions. These methods return base settings that can be merged with additional parameters.

## build_settings

Configures the `build_ios_app` action.

**Default configuration:**

```ruby
{
  scheme: ENV["APP_SCHEME"],
  output_name: ENV["APP_NAME"],
  output_directory: "./build_output/"
}
```

**Customization:** Set `ADDITIONAL_BUILD_SETTINGS` with a JSON string to merge additional parameters.

```bash
ADDITIONAL_BUILD_SETTINGS='{"derived_data_path": "./CustomDerivedData", "xcargs": "-allowProvisioningUpdates"}'
```

---

## code_signing_settings

Configures `sync_code_signing` (match).

**Default configuration:**

```ruby
{
  username: ENV["USER_EMAIL"],
  git_url: ENV["MATCH_GIT_URL"],
  shallow_clone: true,
  clone_branch_directly: true,
  keychain_password: ENV["MATCH_PASSWORD"]
}
```

**Customization:** Set `ADDITIONAL_CODE_SIGNING_SETTINGS` with a JSON string.

```bash
ADDITIONAL_CODE_SIGNING_SETTINGS='{"readonly": true}'
```

!!! note
    `clone_branch_directly` is set to `true` by default. Set it to `false` if you are creating a new branch for a client or manually creating a new branch first.

---

## tests_settings

Configures `run_tests` (scan).

**Default configuration:**

```ruby
{
  skip_build: true,
  scheme: ENV["APP_SCHEME"],
  code_coverage: true,
  result_bundle: true
}
```

**Customization:** Set `ADDITIONAL_TESTS_SETTINGS` with a JSON string.

```bash
ADDITIONAL_TESTS_SETTINGS='{"destination": "platform=iOS Simulator,name=iPhone 15"}'
```

---

## Utility helpers

### keychain_name

Returns `"MatchKeychain"` — the name of the temporary keychain created on CI for code signing.

### bundle_identifier_beta

Returns `ENV["APP_IDENTIFIER"] + ".beta"` — the beta bundle identifier.

### all_bundle_ids(identifier)

Returns a comma-separated string of bundle identifiers including extensions:

- Without extensions: returns just the `identifier`
- With `APP_EXTENSIONS="widget,notification-service"`: returns `"identifier,identifier.widget,identifier.notification-service"`

### merge_additional_settings(base, env_key)

Internal helper that merges a JSON string from an ENV variable into a base settings hash. Used by `build_settings`, `code_signing_settings`, and `tests_settings`.
