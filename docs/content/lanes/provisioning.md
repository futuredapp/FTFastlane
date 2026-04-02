**Purpose:** Set up a local development machine without needing write access to the certificates repository.

### What it does

1. Syncs code signing certificates and profiles from the match repository (`ENV["MATCH_GIT_URL"]`)
2. Downloads development-type profiles for all bundle identifiers (main app + extensions)
3. Read-only mode — does not modify the certificates repository
