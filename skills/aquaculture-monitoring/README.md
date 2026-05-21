# Aquaculture Monitoring Skill

PicClaw skill for pond water-quality monitoring. It watches dissolved oxygen, pH, temperature, ammonia, nitrite, turbidity, salinity, and water level; controls an aerator relay; generates a daily markdown report; and uses memory to learn recurring pond trends.

This skill targets the Clawland bounty requirement: a complete `aquaculture-monitoring` YAML skill for PicClaw with DO/pH/temp thresholds, aerator control logic, daily report generation, and Memory-based trend learning.

## Files

- `skill.yaml` - skill manifest, triggers, thresholds, aerator control rules, alerting, reports, and memory learning.
- `templates/daily-report.md` - markdown report template for daily pond summaries.
- `examples/sample-pond-readings.json` - sample sensor and feeding events for local checks or demos.

## Install

```bash
picclaw skill install aquaculture-monitoring
```

For local development:

```bash
mkdir -p ~/.picclaw/skills
cp -R skills/aquaculture-monitoring ~/.picclaw/skills/
```

## Expected Input

The main event is `sensor.water_quality`. A complete reading should include at least:

```json
{
  "pond_id": "pond-01",
  "timestamp": "2026-05-21T18:30:00+08:00",
  "dissolved_oxygen_mg_l": 4.8,
  "ph": 7.4,
  "water_temperature_c": 29.1
}
```

Optional readings improve diagnosis:

- `ammonia_mg_l`
- `nitrite_mg_l`
- `turbidity_ntu`
- `salinity_ppt`
- `water_level_cm`

Feeding events use `feeding.completed` and are stored so memory can learn whether feeding is followed by oxygen drops.

## Operating Behavior

The skill evaluates aerator rules in priority order. Stale or invalid sensor readings never switch the aerator off. Critical dissolved oxygen always wins: PicClaw closes the aerator relay, sends a critical alert, schedules 10-minute rechecks, and records recovery time.

Memory can start preventive pulse aeration during learned risk windows, but it cannot reduce hard safety thresholds or suppress critical alerts.

## Safety Notes

- The skill never performs automatic chemical dosing.
- The aerator is never disabled during low dissolved oxygen, stale oxygen readings, or manual override.
- If relay verification fails, the skill alerts the operator and keeps the safest current command.
- If aerator recovery gets slower over repeated incidents, the daily report recommends equipment inspection.

## Daily Report

Reports are generated from `templates/daily-report.md` and written to:

```text
reports/aquaculture/{{pond_id}}/{{date}}.md
```

Each report includes sensor min/max/average values, oxygen risk windows, breaches, aerator runtime, feeding correlation, learned trends, and next-day actions.

## Validation

The manifest is plain YAML and can be parsed with Ruby's standard YAML library:

```bash
ruby -e 'require "yaml"; YAML.load_file("skills/aquaculture-monitoring/skill.yaml"); puts "ok"'
```

The sample data is plain JSON:

```bash
python3 -m json.tool skills/aquaculture-monitoring/examples/sample-pond-readings.json >/dev/null
```
