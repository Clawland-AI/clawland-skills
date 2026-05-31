# Cold Chain Compliance Skill

This skill configures a Claw agent to monitor refrigerated storage, frozen goods, pharmaceutical cold-chain loads, and receiving docks. It focuses on practical compliance signals that operators need to preserve an audit trail:

- temperature excursions
- humidity risk
- door-open duration
- mains power loss
- edge-device and sensor battery health
- stale sensor data
- custody handoffs and seal changes

The goal is to turn raw edge readings into operator alerts and audit-ready CSV records before cold-chain integrity is lost.

## When To Use

Use this skill for:

- refrigerated warehouses
- cold rooms and freezer containers
- refrigerated trucks
- receiving and dispatch checks
- pharmaceutical 2-8 C monitoring
- HACCP, GSP, or GDP-style audit trails

## Expected Events

The skill expects readings in this general shape:

```json
{
  "asset_id": "truck-17",
  "location_id": "dock-a",
  "timestamp": "2026-05-31T12:00:00Z",
  "product_class": "pharmaceutical_2_8c",
  "temperature_c": 4.6,
  "humidity_percent": 63.0,
  "door_open": false,
  "door_open_seconds": 0,
  "mains_power": true,
  "battery_percent": 82,
  "sensor_battery_percent": 76,
  "gps_latitude": 1.3521,
  "gps_longitude": 103.8198,
  "custody_actor": "receiving-operator",
  "custody_event": "receiving",
  "seal_id": "seal-0081"
}
```

Individual deployments can rename fields through the `field_mapping` section in `skill.yaml`.

## Temperature Profiles

The skill includes three default profiles:

| Profile | Use Case | Default Control Logic |
| --- | --- | --- |
| `refrigerated` | chilled food and ingredients | warning outside 1-7 C, critical outside 0-8 C |
| `frozen` | frozen goods | warning above -15 C, critical above -12 C |
| `pharmaceutical_2_8c` | 2-8 C medicine storage | warning outside 2.5-7.5 C, critical outside 2-8 C |

These are operating defaults, not legal or medical advice. Teams should tune thresholds to product labels, local regulation, sensor accuracy, and validation results.

## Alert Logic

The skill separates four types of risk:

- single-reading threshold breaches
- sustained excursions over a configured window
- operational hazards such as door-open duration or power loss
- audit hazards such as stale sensors or missing custody records

Warnings create local audit records and operator alerts. Critical events also escalate to a quality-team webhook for quarantine or corrective-action review.

## Audit Outputs

The skill writes two CSV streams:

- `excursions.csv` for temperature, humidity, door, power, and stale-reading events
- `custody.csv` for dispatch, handoff, receiving, and seal-change events

It also declares a daily compliance CSV and Markdown audit-report output. The Markdown report is marked as PDF-ready source so a host agent or downstream reporting pipeline can render it to PDF without changing the monitoring logic.

## Validation Checklist

Before deployment:

- confirm the selected temperature profile for each product class
- run a sensor calibration check
- test a warning excursion and a critical excursion
- test door-open duration alerts
- verify CSV records include timestamp, asset, location, rule, severity, and corrective action
- verify custody records include actor, event type, seal ID, and optional GPS fields

## Safety Notes

This skill does not directly actuate cooling equipment or quarantine inventory. It records evidence, alerts operators, and escalates to quality-control workflows so humans can make regulated release or disposal decisions.
