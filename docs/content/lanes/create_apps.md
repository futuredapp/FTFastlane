### What it creates

| Configuration | Bundle ID | App Name | App Store Connect |
|---------------|-----------|----------|-------------------|
| Debug | `APP_IDENTIFIER` | `APP_NAME` | Identifier only (skip ITC) |
| Beta | `APP_IDENTIFIER.beta` | `APP_NAME BETA` | Identifier + ITC app |
| Release | `APP_IDENTIFIER_CUSTOMER` or `APP_IDENTIFIER` | `APP_NAME` | Identifier + ITC app |

!!! note
    The Debug app identifier is only created when `APP_IDENTIFIER_CUSTOMER` is set or `skip_release_app` is true. Otherwise, the Release identifier serves as the Debug identifier as well.
