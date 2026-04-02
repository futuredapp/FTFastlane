### What it does

1. Clones the device list from `ENV["DEVICE_LIST_GIT_URL"]` (branch `ENV["DEVICE_LIST_GIT_BRANCH"]`)
2. Registers devices from `device-list.txt` to the Apple Developer Portal
3. Syncs development profiles for Debug configuration
4. Syncs appstore profiles for Beta configuration (`.beta` suffix)
5. If `include_release: true` — syncs appstore profiles for Release configuration
