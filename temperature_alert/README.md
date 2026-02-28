# Temperature Alert Skill

Monitor temperature sensors and send alerts when thresholds are exceeded. Supports multiple sensor types and notification channels.

## Features

- **Multiple Sensor Types**: File, HTTP, MQTT, GPIO
- **Smart Alerting**: Configurable threshold with hysteresis to prevent alert flapping
- **Rate of Change Detection**: Alert if temperature changes too quickly
- **Multiple Notification Channels**: Telegram, Discord, Webhook
- **Continuous Monitoring**: Background monitoring with configurable intervals

## Installation

```bash
pip install -r requirements.txt
```

### Requirements

- `requests` - For HTTP sensors and notifications
- `paho-mqtt` - For MQTT sensors (optional)

## Configuration

### skill.yaml

```yaml
configuration:
  sensor_type: file  # file, http, mqtt, or gpio
  
  sensor_config:
    file_path: /sys/bus/w1/devices/28-xxxxxx/w1_slave  # For 1-wire sensors
    # OR for HTTP
    url: http://sensor.local/temperature
    headers:
      Authorization: Bearer token
    # OR for MQTT
    broker: localhost:1883
    topic: sensors/temperature
  
  threshold: 30.0  # Alert when temperature exceeds this (°C)
  hysteresis: 1.0  # Reset alert when temp drops below threshold - hysteresis
  check_interval: 60  # Check every 60 seconds
  rate_of_change_threshold: 5.0  # Alert if temp changes >5°C/min
  
  notification:
    type: telegram  # telegram, discord, or webhook
    config:
      bot_token: YOUR_BOT_TOKEN
      chat_id: YOUR_CHAT_ID
```

## Sensor Types

### File Sensor

Read temperature from a file. Common for 1-wire temperature sensors (DS18B20).

```python
from temperature_alert import FileSensor

sensor = FileSensor('/sys/bus/w1/devices/28-000000000000/w1_slave')
temp = sensor.read_temperature()
```

### HTTP Sensor

Poll an HTTP endpoint that returns temperature data.

```python
from temperature_alert import HTTPSensor

sensor = HTTPSensor(
    url='http://sensor.local/api/temperature',
    headers={'Authorization': 'Bearer token'}
)
temp = sensor.read_temperature()
```

Expected JSON response formats:
```json
{"temperature": 25.5}
{"temp": 25.5}
{"temp_c": 25.5}
{"value": 25.5}
```

### MQTT Sensor

Subscribe to a topic for temperature updates.

```python
from temperature_alert import MQTTSensor

sensor = MQTTSensor(
    broker='localhost:1883',
    topic='sensors/temperature'
)
temp = sensor.read_temperature()
```

### GPIO Sensor

Read from GPIO-connected sensors (requires additional hardware setup).

```python
from temperature_alert import GPIOSensor

sensor = GPIOSensor(pin=4)
temp = sensor.read_temperature()
```

## Notification Channels

### Telegram

```python
from temperature_alert import TelegramNotifier

notifier = TelegramNotifier({
    'bot_token': '123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11',
    'chat_id': '123456789'
})
notifier.send('Temperature exceeded threshold!', 35.5, True)
```

### Discord Webhook

```python
from temperature_alert import DiscordNotifier

notifier = DiscordNotifier({
    'webhook_url': 'https://discord.com/api/webhooks/xxx/xxx'
})
notifier.send('Temperature exceeded threshold!', 35.5, True)
```

### Generic Webhook

```python
from temperature_alert import WebhookNotifier

notifier = WebhookNotifier({
    'url': 'https://your-server.com/webhook',
    'method': 'POST'
})
notifier.send('Temperature exceeded threshold!', 35.5, True)
```

## Usage

### Command Line

```bash
# From file
python -m temperature_alert --config config.json --duration 3600

# From arguments
python -m temperature_alert \
    --sensor-type file \
    --sensor-path /tmp/temp \
    --threshold 30 \
    --interval 30 \
    --duration 3600
```

### As a Library

```python
from temperature_alert import TemperatureAlert, SensorConfig, AlertConfig

# Configure sensor
sensor_config = SensorConfig(
    sensor_type='file',
    file_path='/sys/bus/w1/devices/28-xxxxxx/w1_slave'
)

# Configure alerts
alert_config = AlertConfig(
    threshold=30.0,
    hysteresis=1.0,
    check_interval=60,
    rate_of_change_threshold=5.0,
    notification_type='telegram',
    notification_config={
        'bot_token': 'YOUR_TOKEN',
        'chat_id': 'YOUR_CHAT_ID'
    }
)

# Start monitoring
monitor = TemperatureAlert(sensor_config, alert_config)
monitor.start(duration=3600)  # Run for 1 hour, or 0 for forever

# Check status
print(monitor.status())

# Stop
monitor.stop()
```

## Configuration File Example

```json
{
  "sensor_type": "file",
  "file_path": "/sys/bus/w1/devices/28-000000000000/w1_slave",
  "threshold": 30.0,
  "hysteresis": 1.0,
  "check_interval": 60,
  "rate_of_change_threshold": 5.0,
  "notification": {
    "type": "discord",
    "config": {
      "webhook_url": "https://discord.com/api/webhooks/xxx/xxx"
    }
  }
}
```

## Troubleshooting

### File sensor returns None

- Check file path is correct
- Ensure file is readable (`chmod 644`)
- Verify sensor is connected and working

### HTTP sensor fails

- Check URL is accessible
- Verify headers if required
- Check sensor API format

### MQTT sensor not receiving

- Verify broker is running
- Check topic name
- Ensure network connectivity

### Notifications not sending

- Verify credentials/tokens are correct
- Check network connectivity
- Review logs for error messages

## Use Cases

1. **Home Automation**: Monitor room temperature and alert when too hot/cold
2. **Server Room**: Monitor server rack temperatures
3. **Greenhouse**: Track greenhouse temperature
4. **Aquarium**: Monitor water temperature
5. **Weather Station**: Track outdoor temperature changes
6. **Industrial**: Monitor machinery temperature

## License

MIT
