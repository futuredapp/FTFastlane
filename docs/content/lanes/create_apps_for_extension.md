### What it creates

For each extension in `APP_EXTENSIONS`, it creates identifiers following the same pattern as `create_apps`:

| Configuration | Bundle ID |
|---------------|-----------|
| Debug | `APP_IDENTIFIER.{extension}` |
| Beta | `APP_IDENTIFIER.beta.{extension}` |
| Release | `APP_IDENTIFIER_CUSTOMER.{extension}` or `APP_IDENTIFIER.{extension}` |

### Example

Set `APP_EXTENSIONS` in your project's Fastfile:

```ruby
ENV["APP_EXTENSIONS"] = "widget,notification-service"
```

Then run:

```bash
bundle exec fastlane create_apps_for_extension
```

This creates identifiers for both `widget` and `notification-service` extensions across Debug, Beta, and Release configurations.
