# Temperature Alert Skill

A plug-and-play Clawland skill for monitoring temperature sensors and sending alerts when thresholds are exceeded.

## Compatibility

| Agent    | Supported |
|----------|-----------|
| PicClaw  | ✅        |
| NanoClaw | ✅        |
| MicroClaw| ✅        |

## Installation

```bash
# PicClaw
picclaw skill install temperature-alert

# NanoClaw
nanoclaw skill install temperature-alert

# Remote install via MoltClaw
moltclaw fleet skill install --node edge-01 temperature-alert
```

## Configuration

Set the following environment variables for notification channels:

```bash
export TELEGRAM_BOT_TOKEN="your-bot-token"
export TELEGRAM_CHAT_ID="your-chat-id"
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."
export CUSTOM_WEBHOOK_URL="https://your-service.com/webhook"
```

### Thresholds

| Parameter           | Default | Description                            |
|---------------------|---------|----------------------------------------|
| `high.warning`      | 35.0°C  | Warning threshold for high temperature |
| `high.critical`     | 45.0°C  | Critical threshold for high temperature|
| `low.warning`       | 5.0°C   | Warning threshold for low temperature  |
| `low.critical`      | 0.0°C   | Critical threshold for low temperature |
| `rate_of_change`    | 5.0°C/m | Max rate of change before alert        |

## Features

- **Multi-sensor support**: Monitor multiple temperature sensors simultaneously
- **Configurable thresholds**: Set warning and critical thresholds for high and low temperatures
- **Rate of change detection**: Alert on rapid temperature changes
- **Multi-channel notifications**: Send alerts via Telegram, Discord, email, or custom webhooks
- **Automatic actions**: Trigger cooling/heating systems when thresholds are exceeded
- **Sensor health monitoring**: Detect when sensors go offline or come back online
- **Metrics collection**: Export temperature data in Prometheus, JSON, or CSV format

## How It Works

1. The skill reads sensor data on a configurable schedule (default: every 5 minutes)
2. Each reading is compared against warning and critical thresholds
3. Rate of change is calculated from recent readings
4. Appropriate notifications are sent based on severity
5. Actuators (cooling/heating) are triggered automatically on critical thresholds
6. All data is logged and exported for dashboard integration

## License

MIT
