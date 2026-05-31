# Cold Chain Compliance Skill

This skill monitors refrigerated storage and transport lanes, records tamper-evident audit events, and produces GSP/HACCP-ready cold chain compliance reports.

It is designed as a reference skill for PicClaw, NanoClaw, and MicroClaw deployments used in food, pharma, vaccine, and refrigerated logistics operations.

## What It Monitors

- Air temperature in Celsius
- Product or probe temperature in Celsius
- Relative humidity
- Door-open duration
- Shipment receiving and dispatch events
- Sensor freshness and calibration risk
- Audit log hash continuity

## Compliance Profiles

| Profile | Temperature band | Humidity band | Door-open limit |
| --- | --- | --- | --- |
| Chilled food | 0 C to 5 C | 65% to 90% | 3 minutes |
| Frozen food | -25 C to -18 C | 30% to 75% | 2 minutes |
| Pharma 2-8 C | 2 C to 8 C | 35% to 65% | 90 seconds |

Select the active profile per site, lane, shipment, or storage zone. The profile values are intentionally explicit so operators can adjust them to local SOPs and product requirements.

## Audit Trail

The skill defines a tamper-evident audit trail with SHA-256 hash chaining. Each record includes:

- Timestamp, site, asset, lane, and product category
- Active profile and sensor identifier
- Reading type, value, and unit
- Operator ID and custody event
- Corrective action and release/quarantine decision
- Previous record hash and current record hash

This does not replace legal compliance review, but it gives edge agents a clear structure for producing inspectable records.

## Core Workflows

### Receiving Check

1. Scan shipment ID.
2. Record supplier temperature.
3. Record receiver temperature.
4. Confirm packaging integrity.
5. Accept or quarantine the lot.

### Dispatch Check

1. Confirm vehicle or container is precooled.
2. Record loading start and end times.
3. Verify the active compliance profile.
4. Seal trailer or container.

### Excursion Resolution

1. Identify affected lots.
2. Record duration and temperature range.
3. Assign corrective action owner.
4. Decide release or quarantine.
5. Attach operator signoff.

## Default Rules

- Warning temperature excursions start after 10 minutes outside the active profile.
- Critical product-temperature excursions start after 20 minutes outside the active profile.
- Humidity warnings start after 20 minutes outside the active profile.
- Door-open warnings use the active profile's door limit.
- Sensor data is stale after 15 minutes without a reading.

## Memory-Based Trend Learning

The skill writes operational history to the `cold_chain.compliance` namespace:

- Temperature excursion frequency
- Daily door-open duration
- Compressor recovery time
- Humidity excursion frequency
- Sensor stale events

The agent can then detect risky loading windows, slow refrigeration recovery, and repeated probe reliability problems.

## Reports and Exports

At 07:00 local time, the daily report includes:

- Temperature and humidity excursions
- Door-open exceptions
- Sensor health events
- Corrective actions
- Quarantined lots
- Audit hash summary

The manifest supports Markdown, CSV, and PDF-ready report outputs.

Template: `reports/daily-cold-chain-compliance.md`

Sample events: `examples/sample-events.jsonl`

## Required Environment Variables

Set only the channels you plan to use.

```bash
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
DISCORD_WEBHOOK_URL=...
COLD_CHAIN_WEBHOOK_URL=...
```

## Sensor Naming

The manifest accepts common aliases:

- `temperature`, `temp_c`, `cargo_temperature`
- `probe_temperature`, `product_temp_c`, `core_temperature`
- `humidity`, `rh`
- `door`, `dock_door`, `trailer_door`

## Validation Checklist

- Confirm each probe reports in Celsius or percent as configured.
- Verify the active profile matches the product being stored or shipped.
- Simulate a temperature excursion and confirm alert delivery.
- Simulate a door-open exception during loading.
- Confirm receiving and dispatch workflows produce audit records.
- Confirm exported CSV fields match the audit-trail required fields.
- Verify hash continuity before using reports for release decisions.

## Local Validation

From the repository root:

```bash
node scripts/validate-cold-chain-compliance.mjs
```

This checks that the skill package has the expected files, manifest sections, notification channels, report references, and parseable sample events.

## Bounty Reference

This skill was prepared for the Clawland bounty board item: **Cold Chain Compliance Module - $250**.

Tracking issue: https://github.com/Clawland-AI/clawland-skills/issues/24
