# Aquaculture Monitoring Skill

This skill monitors pond or tank water quality, controls aeration, records trend memory, and generates a daily operator report for aquaculture sites.

It is designed as a reference skill for PicClaw, NanoClaw, and MicroClaw deployments.

## What It Monitors

- Dissolved oxygen in mg/L
- Water pH
- Water temperature in Celsius
- Aerator runtime
- Alert frequency and repeated trend patterns

## Default Thresholds

| Metric | Warning | Critical | Preferred band |
| --- | --- | --- | --- |
| Dissolved oxygen | <= 4.5 mg/L | <= 3.5 mg/L | >= 5.5 mg/L |
| pH | < 6.5 or > 8.8 | < 6.0 or > 9.2 | 6.8-8.4 |
| Water temperature | < 18 C or > 32 C | < 15 C or > 35 C | 20-30 C |

Tune these values for the species, stocking density, feed load, season, and pond depth.

## Control Behavior

The `aerator_main` relay turns on when dissolved oxygen reaches the warning band. It also turns on preemptively when high water temperature increases oxygen demand. The relay will not rapidly toggle because the skill defines a minimum runtime and cooldown window.

Feeding should be suspended when oxygen is low, pH is outside the safe band, or water temperature is outside the operating range. Feeding can resume only after readings remain stable for two hours.

## Memory-Based Trend Learning

The skill writes operational history to the `aquaculture.monitoring` namespace:

- Daily dissolved oxygen minimum
- Short-window oxygen slope
- Daily pH average
- Daily maximum temperature
- Daily aerator runtime
- Daily alert frequency

These memory values let the agent detect repeated night oxygen drops, slow pH drift, and heat-driven oxygen stress.

## Daily Report

At 06:00 local time, the skill renders a daily report with:

- Minimum dissolved oxygen
- Average pH
- Maximum water temperature
- Aerator runtime
- Alerts grouped by severity
- Trend-learning insights
- Recommended operator actions

The report can be emitted as Markdown and JSON, then sent through Telegram or webhook.

Template: `reports/daily-pond-health.md`

Sample readings: `examples/sample-readings.jsonl`

## Required Environment Variables

Set only the channels you plan to use.

```bash
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
DISCORD_WEBHOOK_URL=...
AQUACULTURE_WEBHOOK_URL=...
```

## Sensor Naming

The manifest accepts common aliases:

- `do`, `oxygen`, `dissolved_oxygen_mg_l`
- `pH`, `water_ph`
- `temp`, `water_temp`, `temperature_c`

## Validation Checklist

- Confirm each probe reports in the expected unit.
- Calibrate dissolved oxygen and pH probes before field use.
- Test the aerator relay manually before enabling automatic mode.
- Simulate a low-oxygen reading and confirm alert delivery.
- Verify the daily report renders after sample data is logged.

## Local Validation

From the repository root:

```bash
node scripts/validate-aquaculture-monitoring.mjs
```

This checks that the skill package has the expected files, manifest sections, channel configuration, and parseable sample readings.

## Bounty Reference

This skill was prepared for the Clawland bounty board item: **Aquaculture Monitoring Skill - $200**.

Tracking issue: https://github.com/Clawland-AI/clawland-skills/issues/19
