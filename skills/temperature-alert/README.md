# Temperature Alert Skill

A comprehensive temperature monitoring skill for Claw agents that provides configurable threshold alerts with multi-channel notification support.

## Overview

The Temperature Alert skill enables any Claw agent (PicoClaw, NanoClaw, MicroClaw, etc.) to monitor temperature sensors and send intelligent alerts when thresholds are breached or rapid temperature changes occur.

## Features

- **Multi-threshold monitoring**: High and low temperature alerts
- **Rate-of-change detection**: Alert on rapid temperature fluctuations  
- **Multi-channel notifications**: Telegram, Discord, Email, and generic webhooks
- **Alert cooldown**: Prevent notification spam
- **Historical tracking**: Store temperature readings and alert history
- **Sensor flexibility**: Support for multiple sensor types (DS18B20, DHT22, BME280, etc.)
- **Universal compatibility**: Works with all Claw family agents

## Quick Start

### 1. Install the Skill

```bash
# On PicoClaw
picclaw skill install temperature-alert

# On NanoClaw  
nanoclaw skill install temperature-alert

# Remote install via MoltClaw
moltclaw fleet skill install --node edge-01 temperature-alert
```

### 2. Basic Configuration

```yaml
config:
  high_threshold: 35.0      # °C
  low_threshold: 5.0        # °C
  sensor_id: "temp_01"
  
notifications:
  email:
    enabled: true
    to_email: "alerts@example.com"
```

### 3. Activate Monitoring

The skill will automatically begin monitoring once installed and configured. Temperature readings occur every 2 minutes by default.

## Configuration Reference

### Temperature Thresholds

```yaml
config:
  high_threshold: 35.0      # High temp alert (°C)
  low_threshold: 5.0        # Low temp alert (°C)  
  rate_threshold: 5.0       # Max change rate (°C/min)
  cooldown_minutes: 15      # Alert cooldown period
```

### Sensor Settings

```yaml
config:
  sensor_id: "temp_01"      # Unique sensor identifier
  sensor_type: "DS18B20"    # Sensor type/driver
```

Supported sensor types:
- `DS18B20` - 1-Wire digital temperature sensor
- `DHT22` - Digital humidity & temperature sensor  
- `BME280` - Humidity, pressure & temperature sensor
- `LM35` - Analog temperature sensor
- `TMP36` - Analog temperature sensor
- `SHT30` - Digital humidity & temperature sensor

## Notification Channels

### Telegram

```yaml
notifications:
  telegram:
    enabled: true
    bot_token: "YOUR_BOT_TOKEN"
    chat_id: "YOUR_CHAT_ID"
```

**Setup Steps:**
1. Create a Telegram bot via @BotFather
2. Get your bot token
3. Start a chat with your bot and get the chat ID

### Discord

```yaml
notifications:
  discord:
    enabled: true
    webhook_url: "https://discord.com/api/webhooks/..."
```

**Setup Steps:**
1. Go to your Discord server settings
2. Create a webhook in the desired channel
3. Copy the webhook URL

### Email (SMTP)

```yaml
notifications:
  email:
    enabled: true
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    username: "your-email@gmail.com"
    password: "your-app-password"
    from_email: "alerts@yourcompany.com"
    to_email: "admin@yourcompany.com"
```

### Generic Webhook

```yaml
notifications:
  webhook:
    enabled: true
    url: "https://api.example.com/alerts"
    method: "POST"
    headers:
      Authorization: "Bearer YOUR_TOKEN"
      Content-Type: "application/json"
```

## Use Cases & Examples

### 1. Greenhouse Monitoring

```yaml
name: greenhouse-temp-monitor
config:
  high_threshold: 32.0
  low_threshold: 10.0
  rate_threshold: 3.0
  sensor_id: "greenhouse_main"
  sensor_type: "DHT22"
  cooldown_minutes: 10
  
notifications:
  telegram:
    enabled: true
    bot_token: "${TELEGRAM_BOT_TOKEN}"
    chat_id: "${TELEGRAM_CHAT_ID}"
  email:
    enabled: true
    to_email: "farmer@greenhouse.com"
```

**Benefits:**
- Protect crops from temperature extremes
- Get notified of HVAC system failures
- Monitor heating/cooling efficiency

### 2. Server Room Monitoring

```yaml
name: server-room-monitor
config:
  high_threshold: 28.0      # Server room getting too hot
  low_threshold: 18.0       # AC overcooling
  rate_threshold: 2.0       # Rapid changes indicate AC issues
  sensor_id: "server_rack_01"
  cooldown_minutes: 5       # Faster alerts for critical systems
  
notifications:
  discord:
    enabled: true
    webhook_url: "${DISCORD_IT_ALERTS}"
  webhook:
    enabled: true
    url: "https://monitoring.company.com/api/alerts"
    headers:
      Authorization: "Bearer ${MONITORING_API_KEY}"
```

**Benefits:**
- Prevent server overheating and shutdowns
- Early warning of HVAC failures
- Integration with existing monitoring systems

### 3. Food Storage Monitoring

```yaml
name: freezer-monitor
config:
  high_threshold: -10.0     # Freezer too warm
  low_threshold: -25.0      # Freezer too cold (energy waste)
  rate_threshold: 1.0       # Slow changes expected
  sensor_id: "walk_in_freezer"
  sensor_type: "DS18B20"
  cooldown_minutes: 30      # Longer cooldown for slow-changing system
  
notifications:
  email:
    enabled: true
    to_email: "kitchen@restaurant.com"
  telegram:
    enabled: true
    bot_token: "${TELEGRAM_BOT_TOKEN}"
    chat_id: "${KITCHEN_STAFF_CHAT}"
```

**Benefits:**
- Prevent food spoilage
- Comply with health regulations
- Reduce energy costs

### 4. Home Comfort Monitoring

```yaml
name: home-comfort
config:
  high_threshold: 26.0      # Too hot
  low_threshold: 18.0       # Too cold
  rate_threshold: 4.0       # Normal home temperature changes
  sensor_id: "living_room"
  sensor_type: "BME280"
  cooldown_minutes: 60      # Don't spam family
  
notifications:
  telegram:
    enabled: true
    bot_token: "${HOME_BOT_TOKEN}"
    chat_id: "${FAMILY_CHAT}"
```

**Benefits:**
- Optimize comfort and energy usage
- Get alerts when away from home
- Monitor HVAC system performance

## Alert Types

### High Temperature Alert
```
🔥 High Temperature Alert
Temperature 37.2°C exceeds threshold 35.0°C on sensor greenhouse_main
Time: 2026-02-16 14:30:15
```

### Low Temperature Alert
```
🧊 Low Temperature Alert  
Temperature 3.1°C below threshold 5.0°C on sensor freezer_temp
Time: 2026-02-16 14:30:15
```

### Rapid Change Alert
```
⚡ Rapid Temperature Change
Temperature changing at 7.2°C/min (threshold: 5.0°C/min)
Sensor: server_rack_01
Time: 2026-02-16 14:30:15
```

### Sensor Error Alert
```
⚠️ Sensor Error
Temperature sensor greenhouse_main error: Device not found
Time: 2026-02-16 14:30:15
```

## Hardware Requirements

### Minimum Requirements
- Raspberry Pi (any model) or similar SBC
- Temperature sensor (DS18B20, DHT22, BME280, etc.)
- GPIO pins for sensor connection
- Internet connection (for notifications)

### Recommended Hardware
- **Raspberry Pi 4B** - Best performance and reliability
- **DS18B20** - Most reliable 1-wire temperature sensor
- **4.7kΩ pull-up resistor** - Required for DS18B20
- **Breadboard or PCB** - For secure connections

### Wiring Example (DS18B20)
```
DS18B20 Pin    →    Raspberry Pi Pin
VDD (Red)      →    3.3V (Pin 1)
Data (Yellow)  →    GPIO4 (Pin 7) + 4.7kΩ to 3.3V  
GND (Black)    →    Ground (Pin 6)
```

## Installation & Setup

### 1. Hardware Setup
1. Connect your temperature sensor to the Claw device
2. Verify sensor is detected: `ls /sys/bus/w1/devices/` (for 1-Wire sensors)
3. Test sensor reading: `cat /sys/bus/w1/devices/28-*/w1_slave`

### 2. Skill Installation
```bash
picclaw skill install temperature-alert
```

### 3. Configuration
Create or edit skill configuration:
```bash
picclaw skill config temperature-alert
```

### 4. Testing
Test the skill manually:
```bash
picclaw skill test temperature-alert
```

### 5. Activation
Enable automatic monitoring:
```bash
picclaw skill enable temperature-alert
```

## Troubleshooting

### Sensor Not Detected
- Check wiring connections
- Verify 1-Wire is enabled: `sudo raspi-config` → Interface Options → 1-Wire
- Check if sensor appears: `ls /sys/bus/w1/devices/`
- Verify pull-up resistor (4.7kΩ for DS18B20)

### Notifications Not Sending
- **Telegram**: Verify bot token and chat ID
- **Discord**: Test webhook URL in browser
- **Email**: Check SMTP credentials and firewall
- **Webhook**: Verify URL and authentication

### False Alerts
- Increase `cooldown_minutes` to reduce frequency
- Adjust `rate_threshold` if getting change alerts
- Check sensor placement - avoid direct sunlight, heat sources

### No Temperature Readings
- Verify sensor power and ground connections
- Check GPIO pin assignment
- Test with known working sensor
- Check system logs: `journalctl -u picclaw`

## Advanced Configuration

### Custom Notification Templates

```yaml
actions:
  on_high_temperature:
    steps:
      - notify_all_channels:
          title: "🔥 URGENT: Temperature Alert"
          message: |
            LOCATION: {sensor_id}
            CURRENT: {temperature}°C
            THRESHOLD: {high_threshold}°C  
            TIME: {timestamp}
            
            Immediate action required!
          priority: "critical"
```

### Multiple Sensors

Deploy multiple instances with different configs:

```bash
picclaw skill install temperature-alert --instance greenhouse
picclaw skill install temperature-alert --instance freezer
picclaw skill install temperature-alert --instance server-room
```

### Integration with Home Assistant

```yaml
notifications:
  webhook:
    enabled: true
    url: "http://homeassistant.local:8123/api/webhook/temperature_alert"
    headers:
      Authorization: "Bearer YOUR_LONG_LIVED_ACCESS_TOKEN"
```

## API Reference

### State Variables
- `last_temperature`: Last recorded temperature (float)
- `last_alert_time`: Timestamp of last alert  
- `alert_count`: Number of alerts in current session
- `sensor_status`: Current sensor status (ok/error/offline)
- `temperature_history`: Array of recent readings

### Available Actions
- `on_high_temperature`: Executed when high threshold breached
- `on_low_temperature`: Executed when low threshold breached  
- `on_rapid_change`: Executed when rate threshold exceeded
- `on_sensor_error`: Executed when sensor reading fails

### Event Types
- `temperature.high`: High temperature threshold breach
- `temperature.low`: Low temperature threshold breach
- `temperature.rapid_change`: Rapid temperature change detected
- `temperature.sensor_error`: Sensor reading error
- `temperature.reading`: Normal temperature reading (every check)

## Performance

- **CPU Usage**: <1% on Raspberry Pi 4
- **Memory Usage**: <10MB
- **Network Traffic**: ~1KB per alert
- **Storage**: ~1MB per month (with history)
- **Power Consumption**: Negligible additional load

## Security

- **API Keys**: Stored encrypted in skill configuration
- **Network**: HTTPS/TLS for all external communications
- **Local Access**: Skill runs with minimal required permissions
- **Logging**: No sensitive data in log files

## Contributing

Found a bug or want to add features? Contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/Clawland-AI/clawland-skills/issues)
- **Community**: [Clawland Discord](https://discord.gg/clawland)
- **Email**: support@clawland.ai

---

**Part of the [Clawland](https://github.com/Clawland-AI) ecosystem - Industrial IoT and edge automation platform.**