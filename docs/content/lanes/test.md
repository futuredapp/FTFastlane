### What it does

1. Installs dependencies (`dependencies` private lane):
    - Selects Xcode version if `XCODE_VERSION` is set
    - Runs `pod install` if a `Podfile` exists
2. Generates GraphQL operations if `APOLLO_CODEGEN_CONFIG_PATH` is set
3. Runs all unit and UI tests via `run_tests` (scan)

### Customizing test settings

Override default test settings by setting `ADDITIONAL_TESTS_SETTINGS` in your project's Fastfile:

```ruby
ENV["ADDITIONAL_TESTS_SETTINGS"] = {
  destination: "platform=iOS Simulator,name=iPhone 15"
}.to_json
```

See [Helpers](../configuration/helpers.md#tests_settings) for default test configuration.
