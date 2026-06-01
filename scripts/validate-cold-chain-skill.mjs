import { existsSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const skillDir = join(root, "skills", "cold-chain-compliance");
const skillPath = join(skillDir, "skill.yaml");
const readmePath = join(skillDir, "README.md");
const samplePath = join(skillDir, "samples", "sample-readings.json");
const auditPath = join(skillDir, "samples", "audit-log.jsonl");
const dailyReportPath = join(skillDir, "reports", "daily-summary-template.md");
const excursionReportPath = join(skillDir, "reports", "excursion-report-template.md");

const requiredFiles = [skillPath, readmePath, samplePath, auditPath, dailyReportPath, excursionReportPath];
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
  "sample_chain: samples/audit-log.jsonl",
  "previous_hash",
  "entry_hash",
  "daily_summary:",
  "template_path: reports/daily-summary-template.md",
  "excursion_report:",
  "template_path: reports/excursion-report-template.md",
  "trend_learning:",
  "samples/sample-readings.json",
  "sample_audit_chain: samples/audit-log.jsonl",
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

const auditEvents = readFileSync(auditPath, "utf8")
  .trim()
  .split(/\r?\n/)
  .map((line) => JSON.parse(line));

if (auditEvents.length < 3) {
  throw new Error("Audit log sample must include at least three linked events");
}

let previousHash = "GENESIS";
for (const event of auditEvents) {
  for (const field of ["entry_id", "previous_hash", "entry_hash", "timestamp", "shipment_id", "lot_id", "severity"]) {
    if (!(field in event)) {
      throw new Error(`Audit event ${event.entry_id ?? "<unknown>"} is missing ${field}`);
    }
  }
  if (event.previous_hash !== previousHash) {
    throw new Error(`Audit event ${event.entry_id} breaks previous_hash linkage`);
  }
  if (!/^sha256:[0-9a-f]{64}$/.test(event.entry_hash)) {
    throw new Error(`Audit event ${event.entry_id} has an invalid entry_hash`);
  }
  previousHash = event.entry_hash;
}

const reportRequirements = new Map([
  [dailyReportPath, ["{{date}}", "{{shipment_id}}", "{{total_excursion_minutes}}", "{{qa_release_required}}"]],
  [excursionReportPath, ["{{event_id}}", "{{duration_minutes}}", "{{previous_hash}}", "{{entry_hash}}"]],
]);

for (const [path, placeholders] of reportRequirements) {
  const report = readFileSync(path, "utf8");
  for (const placeholder of placeholders) {
    if (!report.includes(placeholder)) {
      throw new Error(`${path} is missing ${placeholder}`);
    }
  }
}

console.log(
  `Validated cold-chain-compliance skill (${samples.length} sample readings, ${auditEvents.length} audit events).`,
);
