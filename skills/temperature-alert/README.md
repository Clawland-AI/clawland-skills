# Temperature Alert Skill

**Monitor temperature thresholds and send multi-channel alerts for any Claw agent.**

> The first official Clawland skill — designed for PicClaw, NanoClaw, MicroClaw, and MoltClaw.

---

## Overview

The Temperature Alert skill monitors temperature sensors and sends notifications when thresholds are exceeded or rapid temperature changes are detected. It supports multiple notification channels (Telegram, Discord, webhooks) and works across all Claw agent types.

### Features

✅ **Configurable thresholds** — Set high/low warning and critical levels  
✅ **Multi-channel notifications** — Telegram, Discord, and custom webhooks  
✅ **Rate-of-change detection** — Alert on rapid temperature swings  
✅ **Cooldown protection** — Prevent alert spam  
✅ **Universal compatibility** — Works with PicClaw, NanoClaw, MicroClaw, MoltClaw  
✅ **Multiple sensor support** — SHT40, DHT22, BME280, Dallas DS18B20, etc.

---

## Installation

### 1. Install Python Dependencies

First, install the required packages:

```bash
pip3 install -r requirements.txt
```

### 2. Install Sensor-Specific Libraries (Optional)

Based on your hardware, install the appropriate sensor library:

```bash
# For SHT40 sensor
pip3 install adafruit-circuitpython-sht4x

# For DHT22 sensor
pip3 install Adafruit-DHT

# For BME280 sensor
pip3 install adafruit-circuitpython-bme280

# For Dallas DS18B20 sensor
pip3 install w1thermsensor
```

> **Note:** The core skill provides a plugin architecture. Sensor reading functions (`_read_sht40`, `_read_dht22`, etc.) are template methods that need sensor-specific library implementations. See the **Sensor Integration** section below for details.

### 3. Install on Claw Agent

#### On PicClaw (Edge Device)
```bash
picclaw skill install temperature-alert
```

#### On NanoClaw (Lightweight Edge)
```bash
nanoclaw skill install temperature-alert
```

#### On MicroClaw (Industrial)
```bash
microclaw skill install temperature-alert
```

#### Remote Install via MoltClaw (Cloud Orchestration)
```bash
moltclaw fleet skill install --node edge-01 temperature-alert
```

---

## Quick Start

### 1. Configure Your Sensor

Create a `config.yaml` file:

```yaml
sensor: "sht40"           # Sensor type: sht40, dht22, bme280, dallas
sensor_pin: "I2C:0x44"    # GPIO pin or I2C address

thresholds:
  high_warning: 28.0      # Celsius
  high_critical: 35.0
  low_warning: 5.0
  low_critical: 0.0
  rate_of_change: 5.0     # °C per minute

notifications:
  telegram:
    enabled: true
    bot_token: "YOUR_BOT_TOKEN"
    chat_id: "YOUR_CHAT_ID"
  
  discord:
    enabled: false
    webhook_url: ""
  
  webhook:
    enabled: false
    url: ""
    headers: {}
  
  cooldown: 300           # Seconds between duplicate alerts
```

### 2. Run the Skill

The skill will automatically:
- Check temperature every 5 minutes (via cron trigger)
- React to temperature sensor events in real-time
- Log all readings and alerts

Manual check:
```bash
picclaw skill run temperature-alert check-temp
```

---

## Use Cases

### 🖥️ Server Room Monitoring
**Problem:** Server room overheating can cause equipment damage  
**Solution:** Alert on high temperatures before damage occurs

```yaml
sensor: "sht40"
thresholds:
  high_warning: 28.0
  high_critical: 35.0
notifications:
  telegram:
    enabled: true
```

### 🌱 Greenhouse Freeze Protection
**Problem:** Frost can kill plants overnight  
**Solution:** Alert when temperature drops too low

```yaml
sensor: "dht22"
thresholds:
  low_warning: 8.0
  low_critical: 2.0
notifications:
  discord:
    enabled: true
```

### 🏭 Industrial Equipment Monitoring
**Problem:** Rapid temperature changes indicate equipment failure  
**Solution:** Detect anomalies in real-time

```yaml
sensor: "bme280"
thresholds:
  rate_of_change: 3.0
notifications:
  webhook:
    enabled: true
    url: "https://api.example.com/alerts"
```

---

## Configuration Reference

### Sensor Types

| Sensor | Description | Interface |
|--------|-------------|-----------|
| `sht40` | Sensirion SHT40 (±0.2°C accuracy) | I2C |
| `dht22` | DHT22/AM2302 (±0.5°C accuracy) | GPIO |
| `bme280` | Bosch BME280 (temp + humidity + pressure) | I2C/SPI |
| `dallas` | Dallas DS18B20 (waterproof probe) | 1-Wire |
| `max6675` | MAX6675 K-type thermocouple (high temp) | SPI |

### Threshold Levels

| Level | Description | Action |
|-------|-------------|--------|
| **High Critical** | Dangerous heat level | Send critical alert + escalate |
| **High Warning** | Elevated temperature | Send warning alert |
| **Normal** | Within safe range | Log only (no alert) |
| **Low Warning** | Low temperature | Send warning alert |
| **Low Critical** | Freezing risk | Send critical alert + escalate |

### Notification Channels

#### Telegram
```yaml
notifications:
  telegram:
    enabled: true
    bot_token: "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
    chat_id: "987654321"
```

**Setup:**
1. Create a bot via [@BotFather](https://t.me/botfather)
2. Get your chat ID from [@userinfobot](https://t.me/userinfobot)

#### Discord
```yaml
notifications:
  discord:
    enabled: true
    webhook_url: "https://discord.com/api/webhooks/123456789/abcdefg"
```

**Setup:**
1. Go to Server Settings → Integrations → Webhooks
2. Create a webhook and copy the URL

#### Custom Webhook
```yaml
notifications:
  webhook:
    enabled: true
    url: "https://api.example.com/alerts"
    headers:
      Authorization: "Bearer YOUR_API_TOKEN"
      Content-Type: "application/json"
```

**Payload format:**
```json
{
  "event": "temperature_alert",
  "severity": "critical",
  "temperature": 42.5,
  "threshold": 35.0,
  "sensor": "sht40",
  "timestamp": "2026-02-16T14:23:45Z",
  "agent": "picclaw-greenhouse-01"
}
```

---

## Architecture

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│  Temperature    │─────▶│  Temperature     │─────▶│  Notification   │
│  Sensor         │      │  Alert Skill     │      │  Channels       │
│  (SHT40, etc.)  │      │  (skill.yaml)    │      │  (Telegram,     │
└─────────────────┘      └──────────────────┘      │   Discord, etc.)│
                                 │                  └─────────────────┘
                                 │
                                 ▼
                         ┌──────────────────┐
                         │  Alert Logic     │
                         │  • Threshold     │
                         │  • Rate check    │
                         │  • Cooldown      │
                         └──────────────────┘
```

---

## Troubleshooting

### Sensor Not Detected
```bash
# Check I2C devices (Linux)
i2cdetect -y 1

# Check GPIO availability
gpio readall
```

### Alerts Not Sending
1. **Check bot token/webhook URL** — Verify credentials are correct
2. **Check cooldown period** — Duplicate alerts are suppressed
3. **Check network connectivity** — Ensure agent can reach notification services

### False Alerts
- **Reduce sensitivity** — Increase threshold margins
- **Increase cooldown** — Prevent alert spam during fluctuations
- **Check sensor placement** — Avoid direct sunlight, heat sources, drafts

---

## Development

### File Structure
```
skills/temperature-alert/
├── skill.yaml          # Skill manifest and configuration schema
├── README.md           # This file
├── alert.py            # Core alert logic (Python implementation)
├── config.sample.yaml  # Example configuration
└── tests/
    └── test_alert.py   # Unit tests
```

### Running Tests
```bash
cd skills/temperature-alert
python3 -m pytest tests/
```

### Contributing
See [CONTRIBUTING.md](../../CONTRIBUTING.md) for Clawland contribution guidelines.

---

## License

MIT License — see [LICENSE](../../LICENSE)

---

## Support

- **Documentation:** [clawland-ai.github.io](https://clawland-ai.github.io)
- **Issues:** [GitHub Issues](https://github.com/Clawland-AI/clawland-skills/issues)
- **Community:** [Discord](https://discord.gg/clawland) · [GitHub Discussions](https://github.com/orgs/Clawland-AI/discussions)

---

**Built by the Clawland community** 🍇  
First official skill for the Claw agent ecosystem.
