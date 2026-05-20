# Temperature Alert Skill

A Clawland skill that monitors temperature sensors and sends alerts when thresholds are exceeded.

## Features

- ✅ Configurable high/low temperature thresholds
- ✅ Multi-channel notifications (Telegram, Discord, Webhook)
- ✅ Cooldown period to prevent alert spam
- ✅ Works with picclaw, nanoclaw, and microclaw
- ✅ YAML-based configuration

## Quick Start (3 steps)

```bash
# 1. Clone or copy the skill
git clone https://github.com/iyop666/clawland-skills.git
cd clawland-skills/temperature-alert

# 2. Configure thresholds in skill.yaml
# Edit thresholds.high and thresholds.low as needed

# 3. Run the alert
python3 temperature_alert.py 35.5
```

## Configuration

Edit `skill.yaml` to customize:

```yaml
config:
  thresholds:
    high: 30.0    # Alert when temperature exceeds this
    low: 10.0     # Alert when temperature drops below this
  unit: celsius   # celsius or fahrenheit
  cooldown: 300   # Seconds between alerts (prevents spam)
```

### Notification Channels

Add your credentials to `skill.yaml`:

```yaml
config:
  telegram_bot_token: "YOUR_BOT_TOKEN"
  telegram_chat_id: "YOUR_CHAT_ID"
  discord_webhook: "https://discord.com/api/webhooks/..."
  webhook_url: "https://your-api.com/webhook"
```

## Usage

```bash
# Check a single temperature
python3 temperature_alert.py 25.0  # ✅ Normal
python3 temperature_alert.py 35.0  # 🔴 HIGH ALERT
python3 temperature_alert.py 5.0   # 🔵 LOW ALERT

# Use in a monitoring loop
while true; do
    temp=$(read_sensor)  # Your sensor reading command
    python3 temperature_alert.py "$temp"
    sleep 60
done
```

## Integration with Claw Agents

### PicClaw
```yaml
skills:
  - name: temperature-alert
    config:
      thresholds:
        high: 35.0
        low: 5.0
```

### NanoClaw
```bash
claw skill add temperature-alert --config thresholds.high=35.0
```

### MicroClaw
```python
from temperature_alert import TemperatureAlert

alert = TemperatureAlert()
alert.run(sensor_reading)
```

## Requirements

- Python 3.8+
- Optional: `requests` (for notifications)
- Optional: `pyyaml` (for YAML config)

## License

MIT
