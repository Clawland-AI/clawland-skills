# Aquaculture Monitoring Skill

This skill configures a Claw agent to monitor fish-farm water quality and raise operational alerts before conditions become unsafe.

It is designed for edge devices that receive periodic readings from pond, tank, or cage sensors. The skill focuses on parameters that operators typically need to watch continuously:

- dissolved oxygen
- water temperature
- pH
- salinity
- turbidity
- ammonia
- water level
- sensor freshness

## When To Use

Use this skill for:

- pond or tank health monitoring
- shrimp, fish, or recirculating aquaculture systems
- early warning alerts for oxygen, pH, ammonia, or temperature drift
- local edge monitoring when internet connectivity is unreliable

## Expected Events

The skill expects sensor events in this general shape:

```json
{
  "pond_id": "pond-a",
  "timestamp": "2026-05-31T12:00:00Z",
  "dissolved_oxygen_mg_l": 5.8,
  "water_temperature_c": 27.5,
  "ph": 7.4,
  "salinity_ppt": 12.0,
  "turbidity_ntu": 18,
  "ammonia_mg_l": 0.05,
  "water_level_cm": 130
}
```

Individual deployments can rename fields through the `field_mapping` section in `skill.yaml`.

## Alert Logic

The skill separates warning, critical, and stale-data states.

Warning alerts are intended for operator review. Critical alerts should trigger immediate notification and optional local automation, such as starting aeration or increasing water exchange.

Stale sensor data is treated as a first-class risk. A pond that has stopped reporting can be more dangerous than a pond with a single borderline reading.

## Actions

Default actions are conservative:

- log every reading
- send operator alerts for warnings
- escalate critical alerts to both local and cloud channels
- optionally activate aeration when dissolved oxygen is critically low
- mark sensors as stale when readings are too old

Hardware-specific relay or pump actions are left disabled by default and should be wired by each deployment.

## Tuning

Thresholds in `skill.yaml` are practical defaults, not veterinary or regulatory advice. Operators should adjust them for local species, water body type, stocking density, climate, and sensor accuracy.

