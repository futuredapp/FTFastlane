### What it does

1. Checks if `APOLLO_CODEGEN_CONFIG_PATH` is defined
2. If set, runs the Apollo iOS CLI code generation script:
   ```bash
   Scripts/apollo-ios-cli generate --path <config_path>
   ```

### Notes

- This lane is automatically called by the [`test`](test.md) and [`beta`](beta.md)/[`release`](release.md) lanes
- If `APOLLO_CODEGEN_CONFIG_PATH` is not set, the lane is a no-op
- The Apollo iOS CLI script is expected at `Scripts/apollo-ios-cli` relative to the project root
- For more information see the [Apollo iOS documentation](https://www.apollographql.com/docs/ios/code-generation/introduction)
