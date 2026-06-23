require "spec_helper"

RSpec.describe SettingsMerger do
  let(:base) { { scheme: "App", output_directory: "./build_output/" } }

  describe ".merge" do
    context "when there are no additional settings" do
      it "returns the base unchanged for nil" do
        expect(described_class.merge(base, nil)).to eq(base)
      end

      it "returns the base unchanged for an empty string" do
        expect(described_class.merge(base, "")).to eq(base)
      end

      it "returns the base unchanged for a whitespace-only string" do
        expect(described_class.merge(base, "   ")).to eq(base)
      end
    end

    context "with valid JSON" do
      it "adds new keys" do
        result = described_class.merge(base, '{"export_method": "app-store"}')
        expect(result).to eq(base.merge(export_method: "app-store"))
      end

      it "symbolizes top-level string keys so they collide with base symbols" do
        result = described_class.merge(base, '{"scheme": "Override"}')
        expect(result[:scheme]).to eq("Override")
      end

      it "lets the additional value win on key collision" do
        result = described_class.merge(base, '{"output_directory": "./custom/"}')
        expect(result[:output_directory]).to eq("./custom/")
      end

      it "does not mutate the base hash" do
        described_class.merge(base, '{"scheme": "Override"}')
        expect(base[:scheme]).to eq("App")
      end
    end

    context "with malformed JSON" do
      it "raises so the misconfiguration is surfaced loudly" do
        expect { described_class.merge(base, "{not json}") }.to raise_error(JSON::ParserError)
      end
    end
  end
end
