# Temperature Alert Skill

A Clawland skill for monitoring temperature sensors and sending alerts when thresholds are exceeded.

## Features

- **Multi-sensor support**: Monitor multiple temperature sensors simultaneously
- **Configurable thresholds**: Set warning and critical thresholds for high and low temperatures
- **Rate of change detection**: Alert on rapid temperature changes
- **Multi-channel notifications**: Send alerts via Telegram, Discord, email, or custom webhooks
- **Automatic actions**: Trigger cooling/heating systems when thresholds are exceeded
- **Sensor health monitoring**: Detect when sensors go offline or come back online
- **Metrics collection**: Export temperature data for dashboards and analysis

## Compatible Agents

- PicClaw
- NanoClaw
- MicroClaw
- MoltClaw
- Any Claw agent

## Installation

```bash
# On PicClaw
picclaw skill install temperature-alert

# On NanoClaw
nanoclaw skill install temperature-alert

# From MoltClaw (remote install to edge node)
moltclaw fleet skill install --node edge-01 temperature-alert
```

## Configuration

Create a configuration file `config.yaml`:

```yaml
sensors:
  - id: sensor-001
    name: Server Room
    location: Building A, Floor 2
    unit: celsius

  - id: sensor-002
    name: Warehouse
    location: Building B, Ground Floor
    unit: celsius

thresholds:
  low_warning: 15.0
  low_critical: 10.0
  high_warning: 35.0
  high_critical: 40.0
  rate_of_change: 5.0  # degrees per minute

notifications:
  telegram:
    enabled: true
    bot_token: "YOUR_BOT_TOKEN"
    chat_id: "YOUR_CHAT_ID"
  
  discord:
    enabled: false
    webhook_url: "YOUR_WEBHOOK_URL"
  
  email:
    enabled: true
    recipients:
      - admin@example.com
      - ops@example.com

logging:
  enabled: true
  level: info
  retention_days: 30
```

## Usage

### Basic Usage

```bash
# Install the skill
picclaw skill install temperature-alert

# Configure the skill
picclaw skill config temperature-alert --file config.yaml

# Start monitoring
picclaw skill start temperature-alert
```

### Advanced Usage

```bash
# Check skill status
picclaw skill status temperature-alert

# View recent alerts
picclaw skill logs temperature-alert --level warning

# Stop monitoring
picclaw skill stop temperature-alert

# Update configuration
picclaw skill config temperature-alert --set thresholds.high_warning=38.0
```

## Thresholds

| Threshold | Description | Default Action |
|-----------|-------------|----------------|
| `low_warning` | Temperature below this triggers warning | Send warning notification |
| `low_critical` | Temperature below this triggers critical alert | Send critical alert + activate heating |
| `high_warning` | Temperature above this triggers warning | Send warning notification |
| `high_critical` | Temperature above this triggers critical alert | Send critical alert + activate cooling |
| `rate_of_change` | Temperature change rate (°/min) | Send warning notification |

## Notifications

### Telegram

```yaml
notifications:
  telegram:
    enabled: true
    bot_token: "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
    chat_id: "-1001234567890"
```

### Discord

```yaml
notifications:
  discord:
    enabled: true
    webhook_url: "https://discord.com/api/webhooks/123456789/ABCdefGHIjklMNOpqrsTUVwxyz"
```

### Email

```yaml
notifications:
  email:
    enabled: true
    recipients:
      - admin@example.com
      - ops@example.com
```

### Custom Webhook

```yaml
notifications:
  webhook:
    enabled: true
    url: "https://api.example.com/alerts"
    method: POST
    headers:
      Authorization: "Bearer YOUR_TOKEN"
      Content-Type: "application/json"
```

## Metrics

The skill exports the following metrics:

| Metric | Type | Description |
|--------|------|-------------|
| `temperature` | Gauge | Current temperature reading |
| `alerts_total` | Counter | Total number of alerts sent |
| `sensor_status` | Gauge | Sensor online status (1=online, 0=offline) |

### Prometheus Integration

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'temperature-alert'
    static_configs:
      - targets: ['localhost:9090']
```

## Examples

### Server Room Monitoring

```yaml
sensors:
  - id: server-room-1
    name: Server Room 1
    location: Data Center A
    unit: celsius

thresholds:
  high_warning: 28.0
  high_critical: 32.0
  low_warning: 18.0
  low_critical: 15.0

notifications:
  telegram:
    enabled: true
    bot_token: "YOUR_BOT_TOKEN"
    chat_id: "YOUR_CHAT_ID"
```

### Greenhouse Climate Control

```yaml
sensors:
  - id: greenhouse-1
    name: Greenhouse 1
    location: Farm A
    unit: celsius

thresholds:
  high_warning: 35.0
  high_critical: 40.0
  low_warning: 15.0
  low_critical: 10.0
  rate_of_change: 3.0

notifications:
  discord:
    enabled: true
    webhook_url: "YOUR_WEBHOOK_URL"
```

## Troubleshooting

### Sensor Not Detected

1. Check sensor ID in configuration
2. Verify sensor is powered on
3. Check network connectivity
4. Review logs: `picclaw skill logs temperature-alert --level error`

### Alerts Not Sending

1. Verify notification configuration
2. Check API credentials
3. Test notification: `picclaw skill test-notification temperature-alert`
4. Review logs for errors

### High CPU Usage

1. Increase check interval in `skill.yaml`
2. Reduce number of sensors
3. Disable metrics collection if not needed

## Contributing

See the [Clawland Contributing Guide](https://github.com/Clawland-AI/.github/blob/main/CONTRIBUTING.md).

## License

MIT License — see [LICENSE](../LICENSE) for details.
