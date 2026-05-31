import { existsSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const skillDir = join(root, "skills", "cold-chain-compliance");
const skillPath = join(skillDir, "skill.yaml");
const readmePath = join(skillDir, "README.md");
const samplePath = join(skillDir, "samples", "sample-readings.json");

const requiredFiles = [skillPath, readmePath, samplePath];
const missingFiles = requiredFiles.filter((file) => !existsSync(file));
if (missingFiles.length > 0) {
  throw new Error(`Missing required files:\n${missingFiles.join("\n")}`);
}

const yaml = readFileSync(skillPath, "utf8");
const requiredSnippets = [
  "name: cold-chain-compliance",
  "frameworks:",
  "- GSP",
  "- HACCP",
  "audit_trail:",
  "previous_hash",
  "entry_hash",
  "daily_summary:",
  "excursion_report:",
  "trend_learning:",
  "samples/sample-readings.json",
];

const missingSnippets = requiredSnippets.filter((snippet) => !yaml.includes(snippet));
if (missingSnippets.length > 0) {
  throw new Error(`Skill manifest is missing expected content:\n${missingSnippets.join("\n")}`);
}

const samples = JSON.parse(readFileSync(samplePath, "utf8"));
const expectedStates = new Set(samples.map((item) => item.expected_state));
for (const state of ["normal", "warning", "critical"]) {
  if (!expectedStates.has(state)) {
    throw new Error(`Sample readings do not include expected_state=${state}`);
  }
}

for (const sample of samples) {
  for (const field of ["id", "profile", "shipment_id", "lot_id", "timestamp", "temperature_c", "expected_state"]) {
    if (!(field in sample)) {
      throw new Error(`Sample ${sample.id ?? "<unknown>"} is missing ${field}`);
    }
  }
}

console.log(`Validated cold-chain-compliance skill (${samples.length} sample readings).`);
