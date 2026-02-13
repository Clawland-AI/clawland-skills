# Clawland Skills

**Community skill marketplace — plug-and-play AI capabilities for all Claw family agents.**

> Part of the [Clawland](https://github.com/Clawland-AI) ecosystem.

---

## Overview

Clawland Skills is a curated collection of **plug-and-play capabilities** that any Claw agent can load on demand. Skills encapsulate domain knowledge, tool configurations, and behavioral patterns into reusable packages.

## What is a Skill?

A skill is a YAML configuration + optional supporting files that teach a Claw agent how to handle a specific domain:

```yaml
# skills/temperature-monitor/skill.yaml
name: temperature-monitor
version: 1.0.0
description: Monitor temperature sensors and alert on anomalies
agent: picclaw  # or nanoclaw, microclaw, moltclaw, any

triggers:
  - cron: "*/5 * * * *"        # Every 5 minutes
  - event: "sensor.temperature" # On sensor reading

tools:
  - read_sensor
  - send_alert
  - log_data

thresholds:
  warning: 35.0
  critical: 45.0
  rate_of_change: 5.0  # degrees per minute

actions:
  on_warning: "Send Telegram alert to operator"
  on_critical: "Send alert + activate cooling relay + escalate to cloud"
```

## Skill Categories

| Category | Examples |
|----------|----------|
| **Monitoring** | temperature-monitor, humidity-watch, power-usage |
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
picclaw skill install temperature-monitor

# On NanoClaw
nanoclaw skill install camera-patrol

# From MoltClaw (remote install to edge node)
moltclaw fleet skill install --node edge-01 temperature-monitor
```

## Creating a Skill

1. Fork this repository
2. Create a directory under `skills/your-skill-name/`
3. Add `skill.yaml` with the skill definition
4. Add any supporting files (drivers, scripts, templates)
5. Submit a Pull Request

See the [Skill Development Guide](docs/SKILL-DEVELOPMENT.md) for detailed instructions.

## Status

🚧 **Pre-Alpha** — Skill format specification in design. Looking for contributors!

## Contributing

See the [Clawland Contributing Guide](https://github.com/Clawland-AI/.github/blob/main/CONTRIBUTING.md).

**Core contributors share 20% of product revenue.** Read the [Contributor Revenue Share](https://github.com/Clawland-AI/.github/blob/main/CONTRIBUTOR-REVENUE-SHARE.md) terms.

## License

MIT License — see [LICENSE](LICENSE) for details.
