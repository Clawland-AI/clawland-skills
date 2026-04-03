# Temperature Alert Skill

**Universal temperature monitoring and alerting skill for all Claw agents**

---

## Overview

Temperature Alert is a plug-and-play skill that monitors temperature sensors and sends alerts when thresholds are exceeded. Works seamlessly with PicClaw, NanoClaw, and MicroClaw agents.

---

## Features

✅ **Multi-Agent Support** - Works with all Claw family agents
✅ **Configurable Thresholds** - High and low temperature limits
✅ **Multi-Channel Notifications** - Telegram, Discord, Email, Webhook
✅ **Smart Alerting** - Debouncing, cooldown, escalation
✅ **Rate-of-Change Detection** - Alert on rapid temperature changes
✅ **Historical Tracking** - Log temperature data for analysis

---

## Quick Start

### 1. Install the Skill

```bash
# On PicClaw
picclaw skill install temperature-alert

# On NanoClaw
nanoclaw skill install temperature-alert

# On MicroClaw
microclaw skill install temperature-alert
```

### 2. Configure Thresholds

Edit the configuration file:

```bash
nano /etc/clawland/skills/temperature-alert/config.yaml
```

Set your thresholds:

```yaml
thresholds:
  high_warning: 30.0    # °C - Warning level
  high_critical: 35.0   # °C - Critical level
  low_warning: 15.0     # °C - Low warning
  low_critical: 10.0    # °C - Low critical
  rate_of_change: 2.0   # °C per minute - Rapid change alert
```

### 3. Configure Notifications

```yaml
notifications:
  telegram:
    enabled: true
    bot_token: "YOUR_BOT_TOKEN"
    chat_id: "YOUR_CHAT_ID"

  discord:
    enabled: true
    webhook_url: "https://discord.com/api/webhooks/..."

  email:
    enabled: false
    smtp_server: "smtp.gmail.com"
    recipients:
      - "admin@example.com"

  webhook:
    enabled: true
    url: "https://your-server.com/alert"
```

### 4. Start Monitoring

```bash
# Test mode (dry run)
picclaw skill test temperature-alert

# Production mode
picclaw skill enable temperature-alert
```

---

## Configuration Options

### Thresholds

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `high_warning` | float | 30.0 | Warning threshold (°C) |
| `high_critical` | float | 35.0 | Critical threshold (°C) |
| `low_warning` | float | 15.0 | Low warning threshold (°C) |
| `low_critical` | float | 10.0 | Low critical threshold (°C) |
| `rate_of_change` | float | 2.0 | Rate of change limit (°C/min) |
| `hysteresis` | float | 1.0 | Threshold hysteresis (°C) |

### Notification Channels

#### Telegram

```yaml
telegram:
  enabled: true
  bot_token: "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
  chat_id: "-1001234567890"
  parse_mode: "Markdown"
```

**Setup:**
1. Create a bot via [@BotFather](https://t.me/botfather)
2. Get your chat ID from [@userinfobot](https://t.me/userinfobot)
3. Add bot to your group/channel

#### Discord

```yaml
discord:
  enabled: true
  webhook_url: "https://discord.com/api/webhooks/123456/abcdef"
  username: "Temperature Alert Bot"
  avatar_url: "https://example.com/avatar.png"
```

**Setup:**
1. Go to your Discord channel settings
2. Create a Webhook
3. Copy the webhook URL

#### Email

```yaml
email:
  enabled: true
  smtp_server: "smtp.gmail.com"
  smtp_port: 587
  smtp_user: "your-email@gmail.com"
  smtp_password: "your-app-password"
  from_address: "alerts@your-domain.com"
  recipients:
    - "admin@example.com"
    - "oncall@example.com"
```

#### Webhook

```yaml
webhook:
  enabled: true
  url: "https://your-server.com/api/alerts"
  method: "POST"
  headers:
    Authorization: "Bearer YOUR_TOKEN"
    Content-Type: "application/json"
  timeout: 10  # seconds
```

### Alert Behavior

```yaml
alert_settings:
  # Debounce - prevent alert spam
  debounce_seconds: 30

  # Cooldown - minimum time between alerts
  cooldown_seconds: 300  # 5 minutes

  # Escalation - auto-escalate if no acknowledgment
  escalation:
    enabled: true
    delay_seconds: 600  # 10 minutes
    escalate_to:
      - "+1-555-0100"  # SMS number

  # Quiet hours - reduce alerts during certain times
  quiet_hours:
    enabled: false
    start: "22:00"
    end: "06:00"
    timezone: "America/New_York"
```

### Sensor Configuration

```yaml
sensors:
  # Use specific sensor
  - id: "sensor-01"
    type: "DHT22"
    pin: 4
    name: "Server Room Temperature"
    location: "Rack A1"

  # Auto-detect all temperature sensors
  - auto_detect: true
    filter:
      type: "temperature"
```

---

## Alert Messages

### Example Telegram Alert

```
🌡️ TEMPERATURE ALERT

⚠️ WARNING: High Temperature Detected

📍 Location: Server Room - Rack A1
🌡️ Current: 32.5°C
📊 Threshold: 30.0°C
⏱️ Time: 2026-04-03 10:30:15

Trend: ↑ Rising (+2.3°C in last 10 min)

Action: Check HVAC system
```

### Example Discord Alert

```
@everyone 🚨 CRITICAL TEMPERATURE ALERT

Temperature: 36.2°C (Threshold: 35.0°C)
Location: Server Room - Rack A1
Sensor: sensor-01 (DHT22)

⚠️ IMMEDIATE ACTION REQUIRED
• Check cooling system
• Verify airflow
• Consider equipment shutdown

[Acknowledge] [View Dashboard] [Silence 1hr]
```

---

## Advanced Features

### Rate-of-Change Detection

Alerts when temperature changes too quickly, indicating potential issues:

```yaml
rate_of_change:
  enabled: true
  threshold: 2.0  # °C per minute
  window_seconds: 60  # Calculate rate over 60 seconds
```

### Predictive Alerts

Use AI to predict future temperature issues:

```yaml
prediction:
  enabled: true
  model: "linear_regression"
  predict_minutes: 30  # Predict 30 minutes ahead
  alert_if_predicted_exceeds: true
```

### Multi-Sensor Aggregation

```yaml
aggregation:
  enabled: true
  strategy: "average"  # average, max, min, median
  sensors:
    - "sensor-01"
    - "sensor-02"
    - "sensor-03"
```

---

## Integration Examples

### With PicClaw (Edge Device)

```bash
# Install on edge device
picclaw skill install temperature-alert

# Configure for local sensor
picclaw config set temperature-alert.sensor.pin 4
picclaw config set temperature-alert.thresholds.high_critical 40.0

# Enable auto-start on boot
picclaw skill enable temperature-alert --boot
```

### With NanoClaw (Raspberry Pi)

```bash
# Install on NanoClaw
nanoclaw skill install temperature-alert

# Configure multiple sensors
nanoclaw config set temperature-alert.sensors '[{"id":"s1","pin":4},{"id":"s2","pin":5}]'

# Set up notification channels
nanoclaw config set temperature-alert.notifications.telegram.bot_token "YOUR_TOKEN"
```

### With MicroClaw (ESP32)

```c
// For MicroClaw (C/Rust), minimal footprint version
// Configuration in code:

skill_config_t temp_alert = {
    .name = "temperature-alert",
    .threshold_high = 35.0,
    .threshold_low = 15.0,
    .webhook_url = "https://your-server.com/alert",
};
microclaw_skill_load(&temp_alert);
```

---

## Troubleshooting

### Common Issues

**Q: No alerts being sent**
- Check notification channel credentials
- Verify sensor is reading correctly: `picclaw sensor read`
- Check logs: `journalctl -u clawland -f`

**Q: Too many alerts**
- Increase `debounce_seconds` and `cooldown_seconds`
- Adjust `hysteresis` to prevent threshold bouncing
- Check for sensor malfunction

**Q: Alerts not reaching Telegram/Discord**
- Verify bot token and chat ID
- Test webhook URL in browser
- Check network connectivity

### Debug Mode

```bash
# Enable debug logging
picclaw config set temperature-alert.debug true
picclaw config set temperature-alert.log_level "DEBUG"

# Test notification channels
picclaw skill test temperature-alert --notifications

# Simulate temperature reading
picclaw skill test temperature-alert --simulate-temp 38.0
```

---

## API Reference

### REST API Endpoints

When running on PicClaw/NanoClaw with API server:

```bash
# Get current status
GET /api/skills/temperature-alert/status

# Get alert history
GET /api/skills/temperature-alert/history?limit=100

# Acknowledge alert
POST /api/skills/temperature-alert/acknowledge
{
  "alert_id": "alert-123",
  "acknowledged_by": "admin"
}

# Temporarily silence alerts
POST /api/skills/temperature-alert/silence
{
  "duration_minutes": 60,
  "reason": "Scheduled maintenance"
}

# Update thresholds
PUT /api/skills/temperature-alert/config
{
  "thresholds": {
    "high_critical": 38.0
  }
}
```

---

## Contributing

Contributions welcome! Please see:
- [Contributing Guide](https://github.com/Clawland-AI/.github/blob/main/CONTRIBUTING.md)
- [Skill Development Guide](docs/SKILL-DEVELOPMENT.md)

---

## License

MIT License - See [LICENSE](https://github.com/Clawland-AI/clawland-skills/blob/main/LICENSE)

---

## Support

- **Documentation**: [docs.clawland.ai](https://docs.clawland.ai)
- **Community**: [GitHub Discussions](https://github.com/Clawland-AI/clawland-skills/discussions)
- **Issues**: [GitHub Issues](https://github.com/Clawland-AI/clawland-skills/issues)
