# Temperature Alert Skill

Temperature Alert monitors temperature readings and emits alerts when configured high, low, or rapid-change thresholds are crossed. It is intentionally dependency-free so it can run on PicClaw, NanoClaw, MicroClaw, or MoltClaw environments.

## Features

- High and low warning thresholds.
- High and low critical thresholds.
- Rate-of-change detection using a small local state file.
- Multi-channel notification support:
  - generic webhook
  - Discord webhook
  - Telegram bot
  - local log/stdout fallback
- JSON event input for easy integration with edge agents.

## Skill Manifest

The skill definition lives in `skill.yaml`.

```yaml
triggers:
  - event: sensor.temperature
  - cron: "*/5 * * * *"

thresholds:
  high_warning_c: 35.0
  high_critical_c: 45.0
  low_warning_c: 5.0
  low_critical_c: 0.0
  rate_of_change_c_per_min: 5.0
```

## Event Format

```json
{
  "sensor_id": "greenhouse-01",
  "temperature_c": 38.2,
  "timestamp": "2026-06-15T12:00:00Z"
}
```

`timestamp` is optional. If it is omitted, the runtime uses the current UTC time.

## Runtime Usage

```bash
python3 scripts/temperature_alert.py \
  --event examples/sensor-event.json \
  --config config.example.yaml \
  --state .temperature-alert-state.json
```

The runtime prints a JSON decision with:

- `level`: `normal`, `warning`, or `critical`
- `reasons`: threshold or rate-change reasons
- `message`: human-readable alert text
- `delivered`: delivery status per channel

## Configuration

Copy `config.example.yaml` and set only the channels you need.

```yaml
thresholds:
  high_warning_c: 35.0
  high_critical_c: 45.0
  low_warning_c: 5.0
  low_critical_c: 0.0
  rate_of_change_c_per_min: 5.0

notifications:
  webhook_url: ""
  discord_webhook_url: ""
  telegram_bot_token: ""
  telegram_chat_id: ""
```

Empty notification values are ignored, and alerts still appear in stdout.

## Agent Integration

- **PicClaw / MicroClaw** can emit `sensor.temperature` events from GPIO/I2C/SPI sensor readers.
- **NanoClaw** can run the Python runtime directly when aggregating regional sensor events.
- **MoltClaw** can install the skill fleet-wide and route notifications through cloud webhook targets.

## Safety Notes

- Do not commit bot tokens, webhook URLs, or chat IDs.
- Use environment-specific config files outside version control for real deployments.
- For relay-control actions such as activating cooling hardware, add a separate guarded action with manual override and rate limiting.
