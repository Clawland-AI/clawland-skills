# Cold Chain Compliance Skill

`cold-chain-compliance` gives a PicClaw edge node a reviewable operating plan for GSP and HACCP-oriented cold storage, transport, and receiving checks. It focuses on cold-chain evidence: temperature and humidity excursions, door events, power status, chain-of-custody records, tamper-evident logs, and CSV/PDF-ready reporting.

## What It Covers

- Temperature and humidity profiles for chilled food, frozen food, and 2-8 C pharmaceutical logistics.
- Warning and critical bands with maximum excursion windows.
- Door-open, power-loss, receiving, dispatch, handoff, and delivery checkpoint events.
- Tamper-evident JSONL audit trail fields with previous-hash and entry-hash support.
- Daily summary and excursion report templates that can be rendered to CSV or PDF-ready Markdown.
- Reviewable Markdown report templates in `reports/daily-summary-template.md` and `reports/excursion-report-template.md`.
- Tamper-evident sample audit events in `samples/audit-log.jsonl`.
- Memory-based trend learning for recurring excursions, route hotspots, door-open patterns, and corrective action quality.

## Sensor Mapping

The skill expects at least one temperature input named `temperature_c`. Common aliases are accepted in the manifest:

| Canonical field | Example aliases | Unit |
| --- | --- | --- |
| `temperature_c` | `temp_c`, `cargo_temperature_c`, `probe_temperature_c` | Celsius |
| `humidity_percent` | `rh`, `relative_humidity` | Percent |
| `door_open` | `door_contact`, `cargo_door_open` | Boolean |
| `power_ok` | `mains_power`, `fridge_power_ok` | Boolean |
| `gps_location` | `location`, `lat_lon` | Text |

## Profiles

Use `default_profile: chilled_food` unless the node configuration overrides it for a route or shipment.

| Profile | Target | Critical example |
| --- | --- | --- |
| `chilled_food` | 0 C to 5 C | Below -2 C, above 8 C, or excursion over 20 minutes |
| `frozen_food` | At or below -18 C | Above -12 C or excursion over 10 minutes |
| `pharmaceuticals_2_8c` | 2 C to 8 C | Below 1 C, above 9 C, or excursion over 5 minutes |

## Audit Trail

The audit trail is designed for append-only storage at:

```text
memory/cold-chain/audit-log.jsonl
```

Each entry should include `previous_hash` and `entry_hash` so the fleet manager or QA reviewer can detect tampering. Required fields are listed in `skill.yaml` under `audit_trail.required_fields`.

The sample audit chain in `samples/audit-log.jsonl` shows the expected previous-hash linkage from a normal reading to a warning and then a critical excursion. It is sample evidence for validator/reviewer inspection, not a production secret or live shipment record.

## Reports

The skill defines two report shapes:

- `daily_summary`: one operational summary per day, including min/max/average temperature, total excursion minutes, unresolved events, and QA-release requirements.
- `excursion_report`: one report per excursion, including start/end time, duration, root cause, corrective action, disposition, and approver.

Both are marked as `csv` and `pdf-ready-markdown` outputs so a PicClaw node can write structured CSV data for audit systems while also producing a human-readable Markdown document that can be rendered to PDF.

Markdown report skeletons are included under `reports/` so reviewers can inspect the exact compliance fields that would be rendered for daily release checks and individual excursions.

## Sample Validation

The sample readings in `samples/sample-readings.json` are intentionally small and deterministic:

- `cold-ok-001` is normal chilled food storage.
- `cold-warning-001` should trigger a warning for chilled food temperature.
- `cold-critical-001` should trigger a critical excursion for chilled food.
- `pharma-critical-001` should trigger critical handling for a 2-8 C pharmaceutical excursion window.

Reviewers can validate that the manifest references the sample data and that the expected behavior list in `skill.yaml` matches these sample cases.

```bash
node scripts/validate-cold-chain-skill.mjs
```

## Operational Notes

- Treat critical excursions as quarantine events until QA release.
- Record every receiving, dispatch, and handoff checkpoint with shipment id, lot id, operator id, seal id when available, and GPS location when available.
- Use Memory trend learning to identify route hotspots and recurring equipment failures; report high-confidence recurring patterns via `report_gene`.
