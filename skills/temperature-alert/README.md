# Temperature Alert Skill

A Claw agent skill that monitors temperature sensors and sends multi-channel alerts when thresholds are exceeded.

## Features

- **Configurable Thresholds** - Set custom high and low temperature limits
- **Multi-Channel Notifications** - Telegram, Discord, and generic webhooks
- **Multiple Triggers** - Cron-based polling, event-driven, or manual
- **Works with all Claw agents** - picclaw, nanoclaw, microclaw, moltclaw

## Installation

```bash
# Clone this repository
git clone https://github.com/Clawland-AI/clawland-skills.git
cd clawland-skills

# Copy skill to your agent's skills directory
cp -r skills/temperature-alert ~/path/to/your/agent/skills/
```

## Configuration

### Required Setup

1. **Temperature Sensor** - Ensure your agent has access to a temperature sensor
2. **Notification Channels** - Configure at least one:
   - Telegram: Get chat ID from @userinfobot
   - Discord: Create webhook in server settings
   - Generic Webhook: Any HTTP endpoint

### Configuration File

Create `config.yaml` in the skill directory:

```yaml
# Temperature thresholds (in Celsius)
high_threshold: 35.0
low_threshold: 5.0

# Check interval in seconds
check_interval: 300

# Enabled notification channels
channels:
  - telegram
  - discord
  - webhook

# Channel-specific configuration
telegram_chat_id: "123456789"
discord_webhook: "https://discord.com/api/webhooks/..."
webhook_url: "https://your-endpoint.com/alerts"
```

## Usage

### Automatic Monitoring

The skill runs on a cron schedule (default: every 5 minutes). When temperature exceeds or drops below thresholds, alerts are sent to configured channels.

### Manual Commands

```
# Check current temperature
> What's the current temperature?

# Set high temperature threshold
> Set high alert to 40 degrees

# Set low temperature threshold
> Set low alert to 0 degrees

# Enable Discord notifications
> Enable Discord alerts

# Disable alerts
> Mute temperature alerts
```

## Alert Examples

### High Temperature Alert (Telegram/Discord)
```
⚠️ HIGH TEMPERATURE ALERT

Temperature: 38.5°C
Threshold: 35.0°C
Time: 2026-02-24 09:00:00
```

### Low Temperature Alert (Telegram/Discord)
```
❄️ LOW TEMPERATURE ALERT

Temperature: 2.1°C
Threshold: 5.0°C
Time: 2026-02-24 09:00:00
```

## Integration

### With picclaw

```python
from picclaw import Agent

agent = Agent()
agent.load_skill("temperature-alert", config={
    "high_threshold": 30.0,
    "channels": ["telegram"],
    "telegram_chat_id": "YOUR_CHAT_ID"
})
```

### With nanoclaw

```javascript
const { NanoClaw } = require('nanoclaw');

const agent = new NanoClaw();
await agent.loadSkill('temperature-alert', {
  highThreshold: 30,
  lowThreshold: 5,
  channels: ['discord'],
  discordWebhook: 'YOUR_WEBHOOK_URL'
});
```

### With microclaw

```bash
microclaw skill load temperature-alert --config config.yaml
```

## Development

### Adding New Notification Channels

Edit `skill.yaml` and add a new tool:

```yaml
- name: send_slack_alert
  description: "Send alert via Slack"
  parameters:
    message:
      type: string
      required: true
    webhook_url:
      type: string
      required: true
```

### Testing

```bash
# Test temperature reading
python -c "from skills.temperature-alert import sensor; print(sensor.read())"

# Test alert sending (dry run)
python -c "from skills.temperature-alert import alerts; alerts.test()"
```

## Files

```
temperature-alert/
├── skill.yaml      # Skill manifest
├── README.md       # This file
├── config.example  # Example configuration
└── __init__.py     # Optional Python module
```

## License

MIT License - See [LICENSE](../../LICENSE) for details.

## Contributing

Contributions welcome! Please read the [Contributing Guide](https://github.com/Clawland-AI/.github/blob/main/CONTRIBUTING.md).

## Support

- Issues: https://github.com/Clawland-AI/clawland-skills/issues
- Discussions: https://github.com/Clawland-AI/clawland-skills/discussions
