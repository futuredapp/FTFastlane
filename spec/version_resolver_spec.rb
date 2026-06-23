require "spec_helper"

RSpec.describe VersionResolver do
  describe ".resolve" do
    context "when no version is provided" do
      it "defaults to 1.0.0 for a blank env (the empty-string bug)" do
        expect(described_class.resolve(nil, "")).to eq("1.0.0")
      end

      it "defaults to 1.0.0 for a nil env" do
        expect(described_class.resolve(nil, nil)).to eq("1.0.0")
      end

      it "defaults to 1.0.0 for a whitespace-only env" do
        expect(described_class.resolve(nil, "   ")).to eq("1.0.0")
      end
    end

    context "when a version is provided via env" do
      it "uses the concrete version" do
        expect(described_class.resolve(nil, "2.3.0")).to eq("2.3.0")
      end

      it "strips a pre-release suffix" do
        expect(described_class.resolve(nil, "1.2.0-rc1")).to eq("1.2.0")
      end

      it "trims surrounding whitespace" do
        expect(described_class.resolve(nil, "  2.3.0  ")).to eq("2.3.0")
      end
    end

    context "when both option and env are provided" do
      it "gives the lane option precedence over env" do
        expect(described_class.resolve("1.5.0", "9.9.9")).to eq("1.5.0")
      end

      it "falls back to env when the option is blank" do
        expect(described_class.resolve("", "2.3.0")).to eq("2.3.0")
      end
    end
  end
end
