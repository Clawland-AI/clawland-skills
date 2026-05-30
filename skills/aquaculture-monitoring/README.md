# Aquaculture Monitoring Skill

The `aquaculture-monitoring` skill monitors pond dissolved oxygen, pH, and water temperature for Clawland edge agents. It can start an aerator relay, send alerts, write trend data to Memory, and generate a daily pond-health report.

This package is designed for the Clawland bounty board item: **Aquaculture Monitoring Skill**.

## Supported Agents

- PicClaw for small Go-based edge deployments.
- NanoClaw for Python/Raspberry Pi gateway deployments.
- MicroClaw for microcontroller nodes that report sensor events and accept relay commands.

## What It Monitors

| Signal | Default warning | Default critical | Action |
| --- | --- | --- | --- |
| Dissolved oxygen | `< 5.0 mg/L` | `< 3.0 mg/L` | Start aerator and alert operator |
| pH | `< 6.5` or `> 8.5` | `< 6.2` or `> 9.0` | Alert operator and store event |
| Water temperature | `< 18 C` or `> 30 C` | `< 12 C` or `> 34 C` | Alert operator and annotate report |

Tune these values in `configuration.thresholds` for the species, season, and pond type. The defaults are intentionally conservative for warm-water pond monitoring.

## Notifications

The manifest supports three notification channels. Enable the channel in `configuration.notifications` and set the matching environment variable on the agent:

```bash
export TELEGRAM_BOT_TOKEN="..."
export TELEGRAM_CHAT_ID="..."
export DISCORD_WEBHOOK_URL="..."
export AQUACULTURE_WEBHOOK_URL="..."
```

The skill sends critical low-oxygen alerts to all enabled channels and includes the pond id, measured value, and control action taken.

## Aerator Control

Low oxygen uses a two-level control path:

- Warning low oxygen starts `aerator-main` for `15` minutes.
- Critical low oxygen starts `aerator-main` for `45` minutes and records a critical event.

The relay id and durations are configurable under `configuration.aerator`. Agents should enforce `cooldown_minutes` before re-triggering a normal warning cycle, while critical events may bypass cooldown to protect stock.

## Memory-Based Trend Learning

The skill writes water-quality events and aerator actions into the `aquaculture-monitoring` namespace. The daily trend pass compares:

- 30-minute rolling averages for short-term instability.
- 24-hour min/max and averages for daily report summaries.
- Seven-day history for repeated low-oxygen windows or slow aerator recovery.

Trend notes should flag recurring overnight oxygen dips, temperature-driven pH drift, failed recovery after aeration, and sensor values that look stuck or physically implausible.

## Daily Report

The daily report trigger runs at 06:00 by default. It reads the previous 24 hours from Memory, renders `templates/daily-report.md`, and sends the output to enabled channels.

The report is meant to be operational rather than decorative: it should tell the pond operator what happened, whether intervention is needed, and what to check first.

## Sample Sensor Event

Use `examples/sample-reading.json` as a minimal event payload:

```json
{
  "pond_id": "pond-01",
  "sensor_id": "water-node-01",
  "dissolved_oxygen_mg_l": 4.6,
  "ph": 7.4,
  "water_temperature_c": 28.2,
  "timestamp": "2026-05-30T06:10:00Z"
}
```

For this reading, the warning low-oxygen action starts the aerator for 15 minutes and sends a low-oxygen alert.

## Review Checklist

- `skill.yaml` parses as valid YAML.
- Thresholds, aerator relay names, and notification channels are deployment-configurable.
- Critical oxygen events never hide operator alerts behind trend-only reporting.
- Daily reports include enough Memory data to show trends, not just the latest reading.
