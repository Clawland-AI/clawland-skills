# Temperature Alert Skill

`temperature-alert` is a small reference skill for Claw agents that need to watch one or more temperature sensors and notify operators when readings drift outside a safe range.

## What it does

- Reads or receives `sensor.temperature` events.
- Applies configurable low/high warning and critical thresholds.
- Uses a small hysteresis value so alerts do not flap around the threshold.
- Detects fast temperature changes over a short trend window.
- Sends notifications through Telegram, Discord, or a webhook.
- Stores normal readings and alert events in Memory for later review.

## Default thresholds

| Level | Default | Meaning |
| --- | ---: | --- |
| Critical low | 0 °C | Immediate freeze or cold-protection escalation |
| Warning low | 5 °C | Check heating, insulation, or sensor placement |
| Warning high | 35 °C | Check cooling, airflow, or recent load changes |
| Critical high | 45 °C | Immediate operator escalation and local safety action |

Tune `thresholds.temperature` in `skill.yaml` for the environment being monitored. A greenhouse, datacenter cabinet, aquarium, and outdoor enclosure will all need different limits.

## Notification channels

The manifest enables three logical channels:

- `telegram` for direct operator alerts,
- `discord` for team/ops channels,
- `webhook` for automation systems such as dashboards, incident tools, or fleet controllers.

The skill does not store tokens or webhook secrets. Each runtime binds the logical channel names to its own local configuration.

## Agent compatibility

- **PicClaw** can run the full workflow on an edge Linux node: polling, threshold checks, Memory writes, and alert delivery.
- **NanoClaw** can aggregate readings from multiple edge nodes and reuse the same thresholds for regional alerts.
- **MicroClaw** can publish temperature readings from an MCU; if direct Telegram/Discord delivery is too heavy, it can forward events to PicoClaw or NanoClaw for notification.

## Example event

```json
{
  "event": "sensor.temperature",
  "sensor_id": "rack-a-inlet",
  "value": 38.4,
  "unit": "celsius",
  "timestamp": "2026-02-15T12:00:00Z"
}
```

With the default thresholds, this event triggers `on_warning_high` and sends a warning notification.

## Customization checklist

1. Set `warning_low`, `critical_low`, `warning_high`, and `critical_high` for the monitored system.
2. Adjust `dedupe_minutes` if operators need more or fewer repeated alerts.
3. Bind `telegram`, `discord`, and/or `webhook` in the local agent configuration.
4. Decide whether MicroClaw nodes should alert directly or forward events upstream.