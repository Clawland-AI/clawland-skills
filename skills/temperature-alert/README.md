# Temperature Alert Skill 🌡️🐾

This skill allows your Claw agent to monitor temperature data and send alerts via multiple channels (Telegram, Discord, Webhook) when thresholds are breached.

## Features
- **Configurable Thresholds**: Set high and low limits.
- **Multi-channel**: Supports different notification platforms.
- **Universal Compatibility**: Works with `picclaw`, `nanoclaw`, and `microclaw`.

## Setup

1. Copy this folder to your agent's `skills/` directory.
2. Update `skill.yaml` with your preferred thresholds.
3. (Optional) Configure your notification credentials in your agent's `.env`.

## Manifest (skill.yaml)
```yaml
name: temperature-alert
version: 1.0.0
# ...
```

## Testing
Run the handler directly to simulate an alert:
```bash
python handler.py
```

---
*Created for the Clawland Bounty Program ⚡️*
