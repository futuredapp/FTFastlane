# Pure version-resolution logic, extracted from the `bump` lane so it can be
# unit-tested without the fastlane runtime.
module VersionResolver
  DEFAULT_VERSION = "1.0.0".freeze

  # Resolves the marketing version to set during a build.
  #
  # Precedence: explicit lane option > VERSION_NUMBER env value > DEFAULT_VERSION.
  # A nil, empty, or whitespace-only value is treated as "not provided" — this is
  # the guard against an empty VERSION_NUMBER env producing a surprise patch bump.
  # A pre-release suffix (e.g. "1.2.0-rc1") is stripped to its base ("1.2.0").
  #
  # @param option [String, nil] value passed as the lane's `version_number` option
  # @param env_value [String, nil] value of the VERSION_NUMBER env variable
  # @return [String] a concrete version string, never nil/empty
  def self.resolve(option, env_value)
    version = option.to_s.strip
    version = env_value.to_s.strip if version.empty?
    version = DEFAULT_VERSION if version.empty?
    version.split("-").first
  end
end
