import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";

const root = process.cwd();
const skillDir = join(root, "skills", "aquaculture-monitoring");
const manifestPath = join(skillDir, "skill.yaml");
const readmePath = join(skillDir, "README.md");
const samplePath = join(skillDir, "examples", "sample-readings.jsonl");
const reportPath = join(skillDir, "reports", "daily-pond-health.md");

const requiredFiles = [manifestPath, readmePath, samplePath, reportPath];
const missingFiles = requiredFiles.filter((path) => !existsSync(path));

if (missingFiles.length) {
  console.error("Missing required files:");
  for (const path of missingFiles) console.error(`- ${path}`);
  process.exit(1);
}

const manifest = readFileSync(manifestPath, "utf8");
const readme = readFileSync(readmePath, "utf8");
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
  "name: aquaculture-monitoring",
  "picclaw",
  "nanoclaw",
  "microclaw",
  "dissolved_oxygen",
  "ph:",
  "water_temperature",
  "aerator",
  "feeding_guard",
  "trend_learning",
  "daily-pond-health",
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

const sampleProblems = samples.flatMap((sample, index) => {
  const missing = ["timestamp", "pond_id", "dissolved_oxygen", "ph", "water_temperature"]
    .filter((key) => !(key in sample));
  return missing.map((key) => `sample ${index + 1} missing ${key}`);
});

if (sampleProblems.length) {
  console.error("Sample data problems:");
  for (const problem of sampleProblems) console.error(`- ${problem}`);
  process.exit(1);
}

if (!readme.includes("Validation Checklist")) {
  console.error("README must include a validation checklist.");
  process.exit(1);
}

console.log(`aquaculture-monitoring validation passed: ${samples.length} sample readings checked`);
