require "json"

# Pure JSON-merge logic behind `build_settings` / `code_signing_settings` /
# `tests_settings`, extracted so it can be unit-tested without the fastlane
# runtime or ENV mutation.
module SettingsMerger
  # Merges JSON-encoded additional settings on top of a base hash.
  #
  # @param base [Hash] the default settings (symbol keys)
  # @param additional [String, nil] raw JSON string (typically an ENV value);
  #   a nil, empty, or whitespace-only value leaves the base untouched
  # @return [Hash] a new hash; on key collision the additional value wins
  #
  # Top-level string keys in the JSON object are symbolized so they collide
  # correctly with the symbol keys used in the base settings. The merge is
  # shallow, matching the original Fastfile behavior.
  def self.merge(base, additional)
    return base if additional.nil? || additional.strip.empty?

    json_data = JSON.parse(additional)
    json_data = json_data.transform_keys(&:to_sym) if json_data.is_a?(Hash)
    base.merge(json_data)
  end
end
