# Temperature Alert Skill - API Reference

Complete API reference for the Temperature Alert skill.

## Configuration Schema

### Core Configuration

```yaml
config:
  high_threshold: float       # High temperature alert threshold (°C)
  low_threshold: float        # Low temperature alert threshold (°C)
  rate_threshold: float       # Maximum temperature change rate (°C/min)
  cooldown_minutes: integer   # Minutes between repeated alerts
  sensor_id: string          # Unique sensor identifier
  sensor_type: string        # Sensor type/driver name
```

#### Configuration Options Detail

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `high_threshold` | float | 35.0 | -50 to 100 | High temperature alert threshold in Celsius |
| `low_threshold` | float | 5.0 | -50 to 100 | Low temperature alert threshold in Celsius |
| `rate_threshold` | float | 5.0 | 0.1 to 50 | Maximum temperature change per minute |
| `cooldown_minutes` | integer | 15 | 1 to 1440 | Alert cooldown period |
| `sensor_id` | string | "temp_01" | 1-50 chars | Unique sensor identifier |
| `sensor_type` | string | "DS18B20" | enum | Sensor driver type |

#### Supported Sensor Types

| Type | Description | Interface | Notes |
|------|-------------|-----------|--------|
| `DS18B20` | 1-Wire digital temperature sensor | GPIO | Most reliable, unique ID per sensor |
| `DHT22` | Digital humidity & temperature | GPIO | Also provides humidity |
| `BME280` | Environmental sensor (temp/humidity/pressure) | I2C/SPI | Multi-function sensor |
| `LM35` | Analog temperature sensor | ADC | Linear 10mV/°C output |
| `TMP36` | Analog temperature sensor | ADC | Linear temperature sensor |
| `SHT30` | Digital humidity & temperature | I2C | High accuracy |

### Notification Configuration

```yaml
notifications:
  telegram:
    enabled: boolean
    bot_token: string (secret)
    chat_id: string
  
  discord:
    enabled: boolean
    webhook_url: string (secret)
  
  email:
    enabled: boolean
    smtp_server: string
    smtp_port: integer
    username: string
    password: string (secret)
    from_email: string
    to_email: string
  
  webhook:
    enabled: boolean
    url: string
    method: string
    headers: object
```

## Event Types

### Temperature Events

#### `temperature.reading`
Emitted on every temperature reading.

```json
{
  "event_type": "temperature.reading",
  "timestamp": "2026-02-16T14:30:15Z",
  "sensor_id": "temp_01",
  "temperature": 23.5,
  "unit": "celsius",
  "status": "ok"
}
```

#### `temperature.high`
Emitted when temperature exceeds high threshold.

```json
{
  "event_type": "temperature.high",
  "timestamp": "2026-02-16T14:30:15Z",
  "sensor_id": "temp_01", 
  "temperature": 36.2,
  "threshold": 35.0,
  "severity": "warning",
  "message": "High temperature alert: 36.2°C > 35.0°C"
}
```

#### `temperature.low` 
Emitted when temperature drops below low threshold.

```json
{
  "event_type": "temperature.low",
  "timestamp": "2026-02-16T14:30:15Z",
  "sensor_id": "temp_01",
  "temperature": 3.8,
  "threshold": 5.0, 
  "severity": "warning",
  "message": "Low temperature alert: 3.8°C < 5.0°C"
}
```

#### `temperature.rapid_change`
Emitted when rate of change exceeds threshold.

```json
{
  "event_type": "temperature.rapid_change",
  "timestamp": "2026-02-16T14:30:15Z", 
  "sensor_id": "temp_01",
  "temperature": 28.5,
  "previous_temperature": 21.2,
  "rate": 7.3,
  "rate_threshold": 5.0,
  "duration_minutes": 1,
  "message": "Rapid temperature change: 7.3°C/min"
}
```

#### `temperature.sensor_error`
Emitted when sensor reading fails.

```json
{
  "event_type": "temperature.sensor_error",
  "timestamp": "2026-02-16T14:30:15Z",
  "sensor_id": "temp_01", 
  "error": "Device not found",
  "error_code": "DEVICE_NOT_FOUND",
  "severity": "error"
}
```

## Actions

### Trigger Actions

#### `read_sensor`
Read current temperature from sensor.

**Parameters:**
- `sensor_id` (optional): Override default sensor ID

**Returns:**
```json
{
  "temperature": 23.5,
  "timestamp": "2026-02-16T14:30:15Z",
  "sensor_id": "temp_01",
  "status": "ok"
}
```

**Errors:**
- `SENSOR_NOT_FOUND`: Sensor device not detected
- `READ_ERROR`: Failed to read from sensor
- `INVALID_DATA`: Sensor returned invalid data

#### `check_thresholds`
Check current temperature against configured thresholds.

**Parameters:**
- `temperature` (optional): Temperature value to check (uses current reading if not provided)

**Returns:**
```json
{
  "temperature": 23.5,
  "high_threshold": 35.0,
  "low_threshold": 5.0,
  "threshold_status": "normal",
  "alerts_triggered": []
}
```

**Threshold Status Values:**
- `normal`: Temperature within acceptable range
- `high`: Temperature exceeds high threshold
- `low`: Temperature below low threshold
- `rapid_change`: Rate of change exceeded

#### `send_notification`
Send notification through configured channels.

**Parameters:**
- `title`: Notification title
- `message`: Notification message  
- `priority`: Priority level (`low`, `medium`, `high`, `critical`)
- `channels` (optional): Array of specific channels to use

**Returns:**
```json
{
  "notifications_sent": 2,
  "successful_channels": ["email", "telegram"],
  "failed_channels": [],
  "delivery_id": "alert_20260216_143015"
}
```

### Management Actions  

#### `get_status`
Get current skill status and sensor information.

**Returns:**
```json
{
  "skill_status": "active",
  "sensor_status": "ok",
  "last_reading": {
    "temperature": 23.5,
    "timestamp": "2026-02-16T14:30:15Z"
  },
  "alert_stats": {
    "total_alerts": 12,
    "alerts_today": 3,
    "last_alert_time": "2026-02-16T12:15:30Z"
  }
}
```

#### `get_history`
Retrieve temperature history.

**Parameters:**
- `limit` (optional): Number of readings to return (default: 100)
- `start_time` (optional): Start timestamp for range query
- `end_time` (optional): End timestamp for range query

**Returns:**
```json
{
  "readings": [
    {
      "temperature": 23.5,
      "timestamp": "2026-02-16T14:30:15Z",
      "sensor_id": "temp_01"
    }
  ],
  "count": 100,
  "has_more": false
}
```

#### `reset_alerts`
Reset alert cooldown and counters.

**Returns:**
```json
{
  "status": "success",
  "message": "Alert cooldowns and counters reset"
}
```

## State Variables

The skill maintains internal state for monitoring and alerting.

### Current State

| Variable | Type | Description |
|----------|------|-------------|
| `last_temperature` | float | Last recorded temperature |
| `last_reading_time` | timestamp | Time of last sensor reading |
| `last_alert_time` | timestamp | Time of last alert sent |
| `alert_count` | integer | Total alerts sent in session |
| `sensor_status` | string | Current sensor health status |

### Historical State

| Variable | Type | Description |
|----------|------|-------------|
| `temperature_history` | array | Recent temperature readings |
| `alert_history` | array | Recent alerts sent |
| `error_history` | array | Recent sensor errors |

### Status Values

#### Sensor Status
- `ok`: Sensor operating normally
- `error`: Sensor read error
- `offline`: Sensor not detected
- `unknown`: Status not determined

#### Skill Status  
- `active`: Monitoring and alerting active
- `inactive`: Monitoring disabled
- `error`: Skill configuration error
- `starting`: Skill initializing

## Webhook Payloads

When webhook notifications are enabled, payloads are sent in this format:

### Standard Alert Payload

```json
{
  "skill_name": "temperature-alert",
  "skill_version": "1.0.0",
  "event_type": "temperature.high",
  "timestamp": "2026-02-16T14:30:15Z",
  "sensor_id": "temp_01",
  "data": {
    "temperature": 36.2,
    "threshold": 35.0,
    "severity": "warning",
    "message": "High temperature alert: 36.2°C > 35.0°C"
  },
  "metadata": {
    "device_id": "picclaw_001", 
    "location": "greenhouse",
    "alert_id": "alert_20260216_143015"
  }
}
```

### Sensor Error Payload

```json
{
  "skill_name": "temperature-alert",
  "skill_version": "1.0.0", 
  "event_type": "temperature.sensor_error",
  "timestamp": "2026-02-16T14:30:15Z",
  "sensor_id": "temp_01",
  "data": {
    "error": "Device not found",
    "error_code": "DEVICE_NOT_FOUND",
    "severity": "error"
  },
  "metadata": {
    "device_id": "picclaw_001",
    "retry_count": 3
  }
}
```

## HTTP API Endpoints

When running with HTTP API enabled:

### `GET /temperature`
Get current temperature reading.

**Response:**
```json
{
  "temperature": 23.5,
  "timestamp": "2026-02-16T14:30:15Z",
  "sensor_id": "temp_01",
  "unit": "celsius"
}
```

### `GET /status`
Get skill status and configuration.

**Response:**
```json
{
  "skill_status": "active",
  "sensor_status": "ok", 
  "configuration": {
    "high_threshold": 35.0,
    "low_threshold": 5.0,
    "sensor_id": "temp_01"
  }
}
```

### `POST /test-alert`
Trigger test alert.

**Request Body:**
```json
{
  "type": "high_temperature",
  "temperature": 40.0
}
```

**Response:**
```json
{
  "status": "success",
  "notifications_sent": 2,
  "message": "Test alert sent successfully"
}
```

### `GET /history`
Get temperature history.

**Query Parameters:**
- `limit`: Number of readings (default: 100)
- `start`: Start timestamp
- `end`: End timestamp

**Response:**
```json
{
  "readings": [...],
  "count": 100,
  "has_more": false
}
```

## Error Codes

### Sensor Errors

| Code | Description | Resolution |
|------|-------------|------------|
| `DEVICE_NOT_FOUND` | Sensor device not detected | Check wiring, enable 1-Wire |
| `READ_ERROR` | Failed to read from sensor | Check connections, power |
| `INVALID_DATA` | Sensor returned invalid data | Check sensor health, replace if needed |
| `TIMEOUT` | Sensor read timeout | Check for interference, shorter cables |
| `CRC_ERROR` | Data corruption detected | Check connections, add shielding |

### Configuration Errors  

| Code | Description | Resolution |
|------|-------------|------------|
| `INVALID_CONFIG` | Configuration validation failed | Check YAML syntax, required fields |
| `MISSING_REQUIRED` | Required configuration missing | Add required configuration parameters |
| `INVALID_RANGE` | Value outside acceptable range | Adjust values to valid ranges |
| `UNKNOWN_SENSOR_TYPE` | Unsupported sensor type | Use supported sensor or custom driver |

### Notification Errors

| Code | Description | Resolution |
|------|-------------|------------|
| `SMTP_AUTH_ERROR` | Email authentication failed | Check credentials, app passwords |
| `WEBHOOK_TIMEOUT` | Webhook request timed out | Check URL, network connectivity |
| `TELEGRAM_INVALID_TOKEN` | Invalid Telegram bot token | Verify token with BotFather |
| `DISCORD_WEBHOOK_ERROR` | Discord webhook failed | Check webhook URL, permissions |
| `RATE_LIMIT_EXCEEDED` | Too many notifications sent | Increase cooldown, reduce frequency |

## Integration Examples

### Home Assistant Integration

```yaml
# configuration.yaml
sensor:
  - platform: rest
    resource: http://picclaw.local:8080/api/temperature-alert/temperature
    name: "Greenhouse Temperature"
    unit_of_measurement: "°C"
    device_class: temperature

automation:
  - alias: "Temperature Alert Received"
    trigger:
      platform: webhook
      webhook_id: temperature_alert
    action:
      service: notify.mobile_app
      data:
        message: "{{ trigger.json.data.message }}"
```

### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "Temperature Monitoring",
    "panels": [
      {
        "title": "Current Temperature",
        "type": "stat",
        "targets": [
          {
            "url": "http://picclaw.local:8080/api/temperature-alert/temperature",
            "refId": "A"
          }
        ]
      }
    ]
  }
}
```

### Custom Application

```python
import requests
import json

# Get current temperature
response = requests.get('http://picclaw.local:8080/api/temperature-alert/temperature')
temp_data = response.json()
print(f"Current temperature: {temp_data['temperature']}°C")

# Get temperature history
history = requests.get('http://picclaw.local:8080/api/temperature-alert/history?limit=24')
readings = history.json()['readings']

# Calculate average temperature over last 24 readings
avg_temp = sum(r['temperature'] for r in readings) / len(readings)
print(f"Average temperature: {avg_temp:.1f}°C")

# Webhook endpoint to receive alerts
from flask import Flask, request

app = Flask(__name__)

@app.route('/temperature-alerts', methods=['POST'])
def handle_temperature_alert():
    alert_data = request.json
    
    if alert_data['event_type'] == 'temperature.high':
        # Handle high temperature alert
        send_urgent_notification(alert_data)
    elif alert_data['event_type'] == 'temperature.sensor_error':
        # Handle sensor error
        log_sensor_error(alert_data)
    
    return {'status': 'received'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

## Versioning

The Temperature Alert skill follows semantic versioning (semver):

- **Major version**: Breaking configuration changes
- **Minor version**: New features, backward compatible
- **Patch version**: Bug fixes, no configuration changes

### Version 1.0.0 (Current)
- Initial release
- Basic temperature monitoring
- Multi-channel notifications
- Rate limiting and cooldown

### Planned Features

#### Version 1.1.0
- Multiple sensor support
- Custom alert templates
- Historical trend analysis
- Mobile app integration

#### Version 1.2.0  
- Machine learning anomaly detection
- Predictive alerts
- Advanced dashboard
- Cloud sync capabilities

## Performance Characteristics

### Resource Usage

| Metric | Typical Value | Maximum |
|--------|---------------|---------|
| CPU Usage | <0.5% | 2% |
| Memory Usage | <5MB | 15MB |
| Disk Usage | <1MB | 10MB |
| Network Usage | <1KB/min | 10KB/alert |

### Limits

| Parameter | Limit | Notes |
|-----------|-------|--------|
| Max Sensors | 10 | Per skill instance |
| Max History | 10,000 readings | Automatic cleanup |
| Max Alert Rate | 60/hour | Rate limiting |
| Max Webhook Timeout | 30 seconds | Configurable |

This API reference provides complete details for integrating with and extending the Temperature Alert skill.