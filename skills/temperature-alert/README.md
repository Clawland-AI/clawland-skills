# Temperature Alert Skill

`temperature-alert` is the first reference skill for Clawland. It watches a
temperature stream, compares readings against configurable high and low
thresholds, and fans alerts out to common operator channels.

## Supported Agents

- PicClaw
- NanoClaw
- MicroClaw

## What It Does

- polls on a 5-minute schedule and reacts to `sensor.temperature` events
- detects high, low, and rapid-change anomalies
- supports Telegram, Discord, and generic webhook notifications
- keeps local logging enabled even when outbound notifications are disabled

## Configuration

Edit [`skill.yaml`](skill.yaml) to tune the following sections:

- `thresholds`
  - `low_warning` / `low_critical`
  - `high_warning` / `high_critical`
  - `rate_of_change`
- `notifications`
  - enable only the channels you want
  - wire secrets through environment variables
- `inputs.sensor`
  - point the skill at a different event name or polling interval if needed

## Environment Variables

Optional notification secrets:

- `CLAW_TEMPERATURE_ALERT_TELEGRAM_CHAT_ID`
- `CLAW_TEMPERATURE_ALERT_DISCORD_WEBHOOK`
- `CLAW_TEMPERATURE_ALERT_WEBHOOK_URL`

## Example Behavior

- `34.0 C` with default settings: log only
- `37.0 C`: warning notification
- `47.0 C`: critical notification
- `+6.0 C/min`: rapid-change warning even if absolute temperature is still in range

## Install

```bash
picclaw skills install /path/to/clawland-skills/skills/temperature-alert
picclaw agent -m "load the temperature-alert skill and show current thresholds"
```

## Notes

This repository is still pre-alpha. The manifest is intentionally simple and
human-readable so other contributors can copy this directory as a starting
point for new skills.
