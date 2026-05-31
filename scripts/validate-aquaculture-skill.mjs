import fs from "node:fs";

const manifestPath = "skills/aquaculture-monitoring/skill.yaml";
const readmePath = "skills/aquaculture-monitoring/README.md";
const samplePath = "skills/aquaculture-monitoring/samples/sample-readings.json";

for (const path of [manifestPath, readmePath, samplePath]) {
  if (!fs.existsSync(path)) {
    throw new Error(`Missing required file: ${path}`);
  }
}

const manifest = fs.readFileSync(manifestPath, "utf8");
const readme = fs.readFileSync(readmePath, "utf8");
const samples = JSON.parse(fs.readFileSync(samplePath, "utf8"));

const requiredManifestTerms = [
  "name: aquaculture-monitoring",
  "agent: picclaw",
  "dissolved_oxygen_mg_l",
  "warning_below_mg_l: 5.5",
  "critical_below_mg_l: 4.5",
  "ph:",
  "water_temperature",
  "aerator_relay",
  "feeder_relay",
  "feeding-guardrail",
  "daily-report",
  "trend_learning:",
  "daily-water-quality",
];

for (const term of requiredManifestTerms) {
  if (!manifest.includes(term)) {
    throw new Error(`Manifest missing required term: ${term}`);
  }
}

for (const term of ["Sensor Mapping", "Control Logic", "Memory Trend Learning", "Validation"]) {
  if (!readme.includes(term)) {
    throw new Error(`README missing section: ${term}`);
  }
}

if (!Array.isArray(samples) || samples.length < 3) {
  throw new Error("Sample readings must include at least three entries");
}

for (const sample of samples) {
  for (const key of ["timestamp", "node_id", "dissolved_oxygen_mg_l", "ph", "water_temperature_c", "turbidity_ntu"]) {
    if (!(key in sample)) {
      throw new Error(`Sample reading missing key: ${key}`);
    }
  }
}

console.log("Aquaculture monitoring skill validated");
