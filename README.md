# Clawland Skills

**Community skill marketplace — plug-and-play AI capabilities for all Claw family agents.**

> Part of the [Clawland](https://github.com/Clawland-AI) ecosystem.

---

## Overview

Clawland Skills is a curated collection of **plug-and-play capabilities** that any Claw agent can load on demand. Skills encapsulate domain knowledge, tool configurations, and behavioral patterns into reusable packages.

## What is a Skill?

A skill is a directory with a machine-readable YAML manifest plus optional
supporting files that teach a Claw agent how to handle a specific domain:

```yaml
# skills/temperature-alert/skill.yaml
name: temperature-alert
version: 1.0.0
description: Monitor temperature sensors and alert on anomalies
supported_agents:
  - picclaw
  - nanoclaw
  - microclaw

triggers:
  - cron: "*/5 * * * *"
  - event: "sensor.temperature"

tools:
  - read_sensor
  - log_data
  - send_telegram
  - send_discord_webhook
  - post_webhook

thresholds:
  low_warning: 5.0
  low_critical: 0.0
  high_warning: 35.0
  high_critical: 45.0
  rate_of_change: 5.0

notifications:
  telegram:
    enabled: false
  discord:
    enabled: false
  webhook:
    enabled: false
```

## Skill Categories

| Category | Examples |
|----------|----------|
| **Monitoring** | temperature-alert, humidity-watch, power-usage |
| **Security** | motion-detect, door-sensor, camera-patrol |
| **Agriculture** | soil-moisture, greenhouse-climate, irrigation-control |
| **Industrial** | vibration-analysis, predictive-maintenance, energy-audit |
| **Home** | elder-care, pet-monitor, plant-watering |
| **DevOps** | server-health, log-watcher, deploy-notifier |
| **Communication** | telegram-bot, discord-relay, email-digest |
| **Data** | csv-logger, influxdb-writer, grafana-dashboard |

## Installing a Skill

```bash
# On PicClaw
picclaw skills install temperature-alert

# On NanoClaw
nanoclaw skills install temperature-alert

# On MicroClaw
microclaw skills install temperature-alert

# From MoltClaw (remote install to edge node)
moltclaw fleet skill install --node edge-01 temperature-alert
```

## Creating a Skill

1. Fork this repository
2. Create a directory under `skills/your-skill-name/`
3. Add `skill.yaml` with the skill definition
4. Add a local `README.md` explaining configuration and install steps
5. Add any supporting files (drivers, scripts, templates)
6. Submit a Pull Request

See the [Skill Development Guide](docs/SKILL-DEVELOPMENT.md) for detailed instructions.

## Available Skills

| Skill | Purpose | Agents |
|-------|---------|--------|
| `temperature-alert` | High/low threshold and rapid-change temperature alerting with Telegram, Discord, and webhook fan-out | PicClaw, NanoClaw, MicroClaw |

## Status

🚧 **Pre-Alpha** — Skill format specification in design. Looking for contributors!

## Contributing

See the [Clawland Contributing Guide](https://github.com/Clawland-AI/.github/blob/main/CONTRIBUTING.md).

**Core contributors share 20% of product revenue.** Read the [Contributor Revenue Share](https://github.com/Clawland-AI/.github/blob/main/CONTRIBUTOR-REVENUE-SHARE.md) terms.

## License

MIT License — see [LICENSE](LICENSE) for details.
