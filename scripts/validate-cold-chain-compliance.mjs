import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";

const root = process.cwd();
const skillDir = join(root, "skills", "cold-chain-compliance");
const manifestPath = join(skillDir, "skill.yaml");
const readmePath = join(skillDir, "README.md");
const samplePath = join(skillDir, "examples", "sample-events.jsonl");
const reportPath = join(skillDir, "reports", "daily-cold-chain-compliance.md");

const requiredFiles = [manifestPath, readmePath, samplePath, reportPath];
const missingFiles = requiredFiles.filter((path) => !existsSync(path));

if (missingFiles.length) {
  console.error("Missing required files:");
  for (const path of missingFiles) console.error(`- ${path}`);
  process.exit(1);
}

const manifest = readFileSync(manifestPath, "utf8");
const readme = readFileSync(readmePath, "utf8");
const report = readFileSync(reportPath, "utf8");
const samples = readFileSync(samplePath, "utf8")
  .split(/\r?\n/)
  .filter(Boolean)
  .map((line, index) => {
    try {
      return JSON.parse(line);
    } catch (error) {
      throw new Error(`Invalid JSONL sample on line ${index + 1}: ${error.message}`);
    }
  });

const requiredManifestTerms = [
  "name: cold-chain-compliance",
  "picclaw",
  "nanoclaw",
  "microclaw",
  "GSP/HACCP",
  "air_temperature",
  "product_temperature",
  "relative_humidity",
  "door_state",
  "tamper_evident: true",
  "hash_algorithm: sha256",
  "temperature-excursion-critical",
  "receiving_check",
  "dispatch_check",
  "excursion_resolution",
  "daily-cold-chain-compliance",
  "export_csv",
  "export_pdf",
  "telegram",
  "discord",
  "webhook"
];

const missingTerms = requiredManifestTerms.filter((term) => !manifest.includes(term));
if (missingTerms.length) {
  console.error("Manifest is missing required terms:");
  for (const term of missingTerms) console.error(`- ${term}`);
  process.exit(1);
}

const requiredSampleKeys = [
  "timestamp",
  "site_id",
  "asset_id",
  "lane_id",
  "product_category",
  "active_profile",
  "sensor_id",
  "reading_type",
  "reading_value",
  "unit",
  "operator_id",
  "custody_event",
  "corrective_action",
  "previous_record_hash",
  "record_hash"
];

const sampleProblems = samples.flatMap((sample, index) => {
  const missing = requiredSampleKeys.filter((key) => !(key in sample));
  return missing.map((key) => `sample ${index + 1} missing ${key}`);
});

if (sampleProblems.length) {
  console.error("Sample data problems:");
  for (const problem of sampleProblems) console.error(`- ${problem}`);
  process.exit(1);
}

const recordHashes = new Set(samples.map((sample) => sample.record_hash));
const brokenLinks = samples
  .slice(1)
  .filter((sample, index) => sample.previous_record_hash !== samples[index].record_hash)
  .map((sample) => sample.timestamp);

if (recordHashes.size !== samples.length) {
  console.error("Sample data record_hash values must be unique.");
  process.exit(1);
}

if (brokenLinks.length) {
  console.error("Sample hash chain continuity problems:");
  for (const timestamp of brokenLinks) console.error(`- ${timestamp}`);
  process.exit(1);
}

if (!readme.includes("Validation Checklist")) {
  console.error("README must include a validation checklist.");
  process.exit(1);
}

for (const placeholder of ["{{report_date}}", "{{hash_chain_status}}", "{{qa_signature}}"]) {
  if (!report.includes(placeholder)) {
    console.error(`Report template missing ${placeholder}.`);
    process.exit(1);
  }
}

console.log(`cold-chain-compliance validation passed: ${samples.length} audit events checked`);
