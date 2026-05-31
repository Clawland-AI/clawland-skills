# Aquaculture Monitoring Skill

This PicClaw skill monitors water quality, automates aeration, protects feeding windows, and produces daily operating reports.

## What It Monitors

| Signal | Warning | Critical | Action |
| --- | --- | --- | --- |
| Dissolved oxygen | below 5.5 mg/L | below 4.5 mg/L | Run aerator and notify operator. |
| pH | outside 6.8-8.4 | outside 6.5-8.8 | Pause feeding and notify operator. |
| Water temperature | outside 18-30 C | outside 15-33 C | Notify operator and increase oxygen watch. |
| Turbidity | above 55 NTU | above 80 NTU | Pause feeding and create quality event. |

## Sensor Mapping

The manifest uses logical sensor names so deployments can map them to local drivers:

- `modbus.do_probe` for dissolved oxygen.
- `analog.ph_probe` for pH.
- `ds18b20.water_probe` for water temperature.
- `analog.turbidity` for turbidity.
- `gpio.feeder_status` for feeder state.

## Control Logic

- Critical oxygen readings force the aerator relay on.
- Low oxygen during warm water conditions starts aeration before the critical band.
- Feeding is paused when oxygen, pH, or turbidity is outside safe ranges.
- A daily report summarizes water-quality state, threshold breaches, actuator activity, and operator actions.

## Memory Trend Learning

The skill stores 90 days of water-quality and actuator history under `aquaculture.monitoring`. Trend learning is configured to:

- Predict overnight oxygen drops.
- Identify recurring pH drift after feeding.
- Compare aerator runtime against recovery rate.

## Validation

From the repository root:

```sh
node scripts/validate-aquaculture-skill.mjs
```

The validator checks that the skill manifest includes the required sensors, thresholds, rules, Memory settings, reports, and sample readings.
