### What it does

**For own-account apps** (no `APP_IDENTIFIER_CUSTOMER`):

- Syncs appstore profiles from the main match branch for `APP_IDENTIFIER`

**For customer-account apps** (with `APP_IDENTIFIER_CUSTOMER`):

- Syncs appstore profiles from `CUSTOMERS_BRANCH` (or falls back to `MATCH_GIT_BRANCH`) for `APP_IDENTIFIER_CUSTOMER`
