# Temperature Alert Skill - Setup Guide

This guide walks you through setting up the Temperature Alert skill from hardware to notifications.

## Prerequisites

- Claw agent device (PicoClaw, NanoClaw, MicroClaw, etc.)
- Temperature sensor (DS18B20 recommended)
- Basic electronics supplies (breadboard, wires, resistor)
- Internet connection for notifications

## Hardware Setup

### Recommended: DS18B20 1-Wire Temperature Sensor

The DS18B20 is reliable, digital, and easy to wire. Each sensor has a unique ID allowing multiple sensors on one bus.

#### Parts List
- DS18B20 temperature sensor
- 4.7kΩ pull-up resistor  
- Breadboard
- Jumper wires (3x)

#### Wiring Diagram

```
DS18B20 Pinout:
  ┌─────────┐
  │ 1  2  3 │  
  └─────────┘
   │  │  │
   │  │  └── Data (Yellow)
   │  └───── VDD (Red) 
   └──────── GND (Black)

Raspberry Pi Connection:
DS18B20 Pin 1 (GND)    → Pi Pin 6  (Ground)
DS18B20 Pin 2 (Data)   → Pi Pin 7  (GPIO4) + 4.7kΩ resistor to Pin 1 (3.3V)
DS18B20 Pin 3 (VDD)    → Pi Pin 1  (3.3V)
```

#### Physical Assembly

1. **Insert DS18B20 into breadboard**
   - Place sensor across center gap
   - Pin 1 (GND) on left, Pin 3 (VDD) on right when flat side faces you

2. **Add pull-up resistor**
   - Connect 4.7kΩ resistor between Data pin and VDD
   - This is required for 1-Wire communication

3. **Wire to Raspberry Pi**
   - Use jumper wires to connect as shown in diagram
   - Double-check connections - wrong wiring can damage components

### Alternative: DHT22 Digital Sensor

If using DHT22 (humidity + temperature):

```
DHT22 Pin 1 (VDD)    → Pi Pin 1  (3.3V)
DHT22 Pin 2 (Data)   → Pi Pin 7  (GPIO4) + 4.7kΩ resistor to Pin 1
DHT22 Pin 3 (NC)     → Not connected
DHT22 Pin 4 (GND)    → Pi Pin 6  (Ground)
```

## Software Setup

### 1. Enable 1-Wire Interface (for DS18B20)

```bash
# Open Raspberry Pi configuration
sudo raspi-config

# Navigate to: Interface Options → 1-Wire → Enable
# Reboot when prompted
sudo reboot
```

### 2. Verify Sensor Detection

```bash
# Check if 1-Wire devices are detected
ls /sys/bus/w1/devices/

# Should show something like: 28-0000072431aa  w1_bus_master1
# The 28-xxxxxx is your DS18B20 sensor

# Test temperature reading
cat /sys/bus/w1/devices/28-*/w1_slave

# Should show temperature data like:
# 72 01 4b 46 7f ff 0c 10 1c : crc=1c YES
# 72 01 4b 46 7f ff 0c 10 1c t=23125
# The t=23125 means 23.125°C
```

### 3. Install Temperature Alert Skill

```bash
# Install the skill
picclaw skill install temperature-alert

# Or if installing from local development
cd /path/to/clawland-skills
picclaw skill install ./skills/temperature-alert
```

### 4. Basic Configuration

Create initial configuration:

```bash
picclaw skill config temperature-alert --edit
```

Enter basic settings:
```yaml
config:
  high_threshold: 30.0
  low_threshold: 15.0
  sensor_id: "main_temp"
  sensor_type: "DS18B20"

notifications:
  email:
    enabled: true
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    username: "your-email@gmail.com" 
    password: "your-app-password"
    from_email: "alerts@yourdomain.com"
    to_email: "admin@yourdomain.com"
```

### 5. Test Installation

```bash
# Test sensor reading
picclaw skill test temperature-alert --action read_sensor

# Test alert system  
picclaw skill test temperature-alert --action test_alert

# View current temperature
picclaw skill status temperature-alert
```

## Notification Setup

### Email (Gmail Example)

1. **Enable 2-Factor Authentication** on your Gmail account

2. **Generate App Password**:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
   - Use this password in configuration

3. **Configure skill**:
```yaml
notifications:
  email:
    enabled: true
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    username: "your-email@gmail.com"
    password: "your-16-char-app-password"
    from_email: "alerts@yourdomain.com"
    to_email: "admin@yourdomain.com"
```

### Telegram

1. **Create Bot**:
   - Message @BotFather on Telegram
   - Send `/newbot`
   - Choose name and username
   - Save the bot token

2. **Get Chat ID**:
   - Start chat with your bot
   - Send any message
   - Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
   - Find your chat ID in the response

3. **Configure skill**:
```yaml
notifications:
  telegram:
    enabled: true
    bot_token: "1234567890:ABCdefGHijklMNopQRstUVwxyz"
    chat_id: "123456789"
```

### Discord

1. **Create Webhook**:
   - Go to your Discord server
   - Right-click channel → Edit Channel → Integrations → Webhooks
   - Create webhook, copy URL

2. **Configure skill**:
```yaml
notifications:
  discord:
    enabled: true
    webhook_url: "https://discord.com/api/webhooks/123/abc..."
```

### Generic Webhook

For integration with monitoring systems:

```yaml
notifications:
  webhook:
    enabled: true
    url: "https://api.yourmonitoringsystem.com/alerts"
    method: "POST"
    headers:
      Authorization: "Bearer your-api-token"
      Content-Type: "application/json"
```

## Testing & Validation

### 1. Manual Temperature Test

```bash
# Force a temperature reading
picclaw skill run temperature-alert --action read_temperature

# Simulate high temperature alert
picclaw skill run temperature-alert --simulate high_temp=40.0

# Simulate low temperature alert  
picclaw skill run temperature-alert --simulate low_temp=0.0
```

### 2. Notification Test

```bash
# Test all enabled notification channels
picclaw skill run temperature-alert --action test_notifications

# Test specific channel
picclaw skill run temperature-alert --action test_email
picclaw skill run temperature-alert --action test_telegram
picclaw skill run temperature-alert --action test_discord
```

### 3. Monitoring Test

```bash
# Enable skill and monitor for 10 minutes
picclaw skill enable temperature-alert
picclaw skill logs temperature-alert --follow

# Check status
picclaw skill status temperature-alert
```

## Common Configuration Examples

### Home Automation

```yaml
config:
  high_threshold: 26.0      # Comfortable home temperature
  low_threshold: 18.0       
  rate_threshold: 3.0       # Gradual changes expected
  cooldown_minutes: 30      # Don't spam family
  sensor_id: "living_room"

notifications:
  telegram:
    enabled: true
    bot_token: "${TELEGRAM_BOT_TOKEN}"
    chat_id: "${FAMILY_CHAT_ID}"
```

### Industrial Monitoring

```yaml
config:
  high_threshold: 45.0      # Equipment operating limit
  low_threshold: 10.0       # Frost protection  
  rate_threshold: 5.0       # Rapid industrial changes
  cooldown_minutes: 5       # Fast alerts for critical systems
  sensor_id: "machine_01"

notifications:
  email:
    enabled: true
    to_email: "maintenance@company.com"
  webhook:
    enabled: true
    url: "https://monitoring.company.com/api/alerts"
    headers:
      Authorization: "Bearer ${MONITORING_API_TOKEN}"
```

### Greenhouse Agriculture

```yaml
config:
  high_threshold: 32.0      # Protect crops from heat
  low_threshold: 8.0        # Frost protection
  rate_threshold: 2.0       # Greenhouse changes slowly
  cooldown_minutes: 15      # Reasonable alert frequency
  sensor_id: "greenhouse_main"

notifications:
  telegram:
    enabled: true
    bot_token: "${BOT_TOKEN}"
    chat_id: "${FARMER_CHAT}"
  email:
    enabled: true
    to_email: "farmer@greenhouse.com"
```

## Advanced Setup

### Multiple Sensors

Monitor different zones with separate instances:

```bash
# Install multiple instances
picclaw skill install temperature-alert --instance living_room
picclaw skill install temperature-alert --instance bedroom  
picclaw skill install temperature-alert --instance basement

# Configure each separately
picclaw skill config temperature-alert:living_room
picclaw skill config temperature-alert:bedroom
picclaw skill config temperature-alert:basement
```

### Custom Sensor Types

For unsupported sensors, create a custom driver:

```python
# /opt/picclaw/drivers/custom_temp_sensor.py
import time

def read_temperature(sensor_id):
    """Read temperature from custom sensor"""
    # Your custom sensor reading logic here
    temperature = read_your_sensor()
    return {
        'temperature': temperature,
        'timestamp': time.time(),
        'sensor_id': sensor_id,
        'status': 'ok'
    }
```

Then configure:
```yaml
config:
  sensor_type: "custom"
  sensor_driver: "/opt/picclaw/drivers/custom_temp_sensor.py"
```

### Environment Variables

Use environment variables for secrets:

```yaml
notifications:
  telegram:
    enabled: true  
    bot_token: "${TELEGRAM_BOT_TOKEN}"
    chat_id: "${TELEGRAM_CHAT_ID}"
  email:
    enabled: true
    password: "${EMAIL_PASSWORD}"
```

Set in system:
```bash
export TELEGRAM_BOT_TOKEN="1234567890:ABC..."
export TELEGRAM_CHAT_ID="123456789"
export EMAIL_PASSWORD="app-password-here"
```

## Next Steps

1. **Monitor for 24 hours** to verify operation
2. **Fine-tune thresholds** based on your environment
3. **Set up dashboards** if using webhook integration
4. **Add more sensors** to expand monitoring
5. **Create automation rules** based on temperature events

## Need Help?

- **Documentation**: Check other files in `/docs`
- **Logs**: `picclaw skill logs temperature-alert`
- **Status**: `picclaw skill status temperature-alert`  
- **Community**: [Clawland Discord](https://discord.gg/clawland)
- **Issues**: [GitHub Issues](https://github.com/Clawland-AI/clawland-skills/issues)