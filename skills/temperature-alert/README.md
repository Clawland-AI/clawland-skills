# Temperature Alert Skill

A plug-and-play Clawland skill that monitors temperature sensors and sends alerts when thresholds are breached. Supports **Telegram**, **Discord**, and **generic webhook** notifications.

## Overview

| Property | Value |
|----------|-------|
| **Name** | temperature-alert |
| **Version** | 1.0.0 |
| **Category** | Monitoring |
| **Agents** | picclaw, nanoclaw, microclaw |
| **License** | MIT |

## Features

- Configurable high/low temperature thresholds (warning and critical levels)
- Rate-of-change detection for rapid temperature shifts
- Multi-channel notifications: Telegram, Discord, webhook
- Adjustable polling interval and cooldown period
- Automatic retry for failed notifications
- Local event logging

## Quick Start

### Install

```bash
# On PicClaw
picclaw skill install temperature-alert

# On NanoClaw
nanoclaw skill install temperature-alert

# On MicroClaw
microclaw skill install temperature-alert
```

### Configure

Set your notification channels via environment variables:

```bash
# Telegram (optional)
export TELEGRAM_BOT_TOKEN="your-bot-token"
export TELEGRAM_CHAT_ID="your-chat-id"

# Discord (optional)
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/YOUR/WEBHOOK"

# Generic webhook (optional)
export ALERT_WEBHOOK_URL="https://your-server.com/alerts"
```

Then enable channels in your skill config:

```yaml
notifications:
  telegram:
    enabled: true
  discord:
    enabled: true
  webhook:
    enabled: true
```

### Customize Thresholds

Edit the thresholds in `skill.yaml` or override at install time:

```yaml
thresholds:
  high:
    warning: 30.0   # Celsius
    critical: 40.0
  low:
    warning: 10.0
    critical: 0.0
  unit: celsius  # or fahrenheit
```

## Threshold Reference

| Level | High Warning | High Critical | Low Warning | Low Critical |
|-------|-------------|---------------|-------------|--------------|
| Default (C) | 35.0 | 45.0 | 5.0 | -5.0 |
| Home comfort | 28.0 | 35.0 | 15.0 | 10.0 |
| Server room | 30.0 | 35.0 | — | — |
| Freezer | -10.0 | -5.0 | — | — |

## Notification Format

All channels receive a structured JSON payload:

```json
{
  "skill": "temperature-alert",
  "level": "critical",
  "sensor_id": "default",
  "temperature": 46.2,
  "threshold": 45.0,
  "unit": "celsius",
  "timestamp": "2026-05-21T10:30:00Z",
  "message": "CRITICAL: Temperature 46.2C exceeds threshold 45.0C"
}
```

## Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `sensor_id` | `default` | Sensor identifier |
| `polling_interval` | `300` | Seconds between sensor checks |
| `cooldown_period` | `600` | Minimum seconds between same-level alerts |
| `retry_count` | `3` | Notification retry attempts |
| `retry_delay` | `10` | Seconds between retries |

## Troubleshooting

- **No alerts firing**: Verify sensor is returning valid readings and thresholds are appropriate.
- **Notifications failing**: Check webhook URLs and bot tokens. Enable debug logging with `CLAW_LOG_LEVEL=debug`.
- **Too many alerts**: Increase `cooldown_period` to avoid alert fatigue.

## Contributing

Bug reports and feature requests welcome. See the [Clawland Contributing Guide](https://github.com/Clawland-AI/.github/blob/main/CONTRIBUTING.md).
