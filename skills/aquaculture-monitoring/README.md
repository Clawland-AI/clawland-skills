# Aquaculture Monitoring Skill

`aquaculture-monitoring` is a PicClaw skill for pond and tank operations. It evaluates dissolved oxygen, pH, and water temperature, drives aerator relays, suspends feeding during unsafe water-quality windows, and produces a daily operating report.

## What It Covers

- Dissolved oxygen warning and critical bands.
- pH warning and critical bands.
- Water temperature warning and critical bands.
- Optional ammonia, nitrite, turbidity, salinity, and water-level checks.
- Aerator control with normal, boost, and emergency modes.
- Feeding guardrails when oxygen, temperature, ammonia, or nitrite values are unsafe.
- Daily markdown and JSON reports.
- Memory-based trend learning for overnight oxygen troughs, pH drift, heat-related oxygen drops, feeding correlation, and aerator recovery time.

## Expected Sensor Reading

PicClaw should publish readings with these required fields:

```json
{
  "pond_id": "pond-west-01",
  "timestamp": "2026-05-31T06:00:00Z",
  "dissolved_oxygen_mg_l": 4.6,
  "ph": 7.4,
  "water_temperature_c": 28.2
}
```

Optional fields include `ammonia_mg_l`, `nitrite_mg_l`, `turbidity_ntu`, `salinity_ppt`, `water_level_cm`, `feeding_event`, `aerator_state`, `sensor_battery_percent`, and `sensor_age_seconds`.

## Aerator Behavior

| Mode | Trigger | Primary aerator | Backup aerator |
| --- | --- | --- | --- |
| `normal` | Dissolved oxygen at or above 5.0 mg/L and water temperature at or below 30 C | Scheduled operation | Off |
| `boost` | Dissolved oxygen below 4.0 mg/L or water temperature above 32 C | On for at least 30 minutes | Off |
| `emergency` | Dissolved oxygen below 3.0 mg/L or stale sensor data | On for at least 60 minutes | On |

The skill avoids stopping aeration immediately after feeding, applies a relay cooldown, and requires manual acknowledgement before shutting down after emergency mode.

## Daily Report

The daily report runs at 06:00 local time by default and includes:

- Minimum, maximum, and average dissolved oxygen.
- Minimum, maximum, and average pH.
- Minimum, maximum, and average water temperature.
- Aerator runtime.
- Feeding suspensions.
- Warning and critical events.
- Sensor-health status.
- Recommended actions.

The report template lives in `templates/daily-report.md`.

## Validation

Run the dependency-free validator from the repository root:

```bash
python skills/aquaculture-monitoring/tools/validate_aquaculture_skill.py
```

The validator checks that the YAML parses, required top-level sections are present, core thresholds exist, aerator modes are defined, Memory learning is enabled, the report template exists, and the sample reading contains the required sensor fields.

## Bounty Mapping

The Clawland bounty board asks for:

- DO/pH/temp thresholds.
- Aerator control logic.
- Daily report generation.
- Memory-based trend learning.

Each item is represented in `skill.yaml` and covered by the validator.
