# Skill Development Guide

This repository currently treats a Skill as:

- a directory under `skills/<skill-name>/`
- a `skill.yaml` manifest that machines can parse
- optional supporting files such as `README.md`, templates, scripts, or sample payloads

## Minimum Layout

```text
skills/
  your-skill-name/
    skill.yaml
    README.md
```

## Required Manifest Fields

```yaml
name: your-skill-name
version: 1.0.0
description: Short summary of what the skill does
category: monitoring
supported_agents:
  - picclaw
  - nanoclaw
  - microclaw
triggers:
  - cron: "*/5 * * * *"
tools:
  - read_sensor
actions:
  on_warning:
    - send_telegram
```

## Recommended Sections

- `metadata`
  - owner, tags, license
- `inputs`
  - event source names, polling intervals, expected payload fields
- `thresholds`
  - defaults that operators can tune without changing logic
- `notifications`
  - channel toggles and environment variable names
- `message_templates`
  - human-readable alert text

## Authoring Rules

- keep manifests declarative and portable across PicClaw, NanoClaw, and MicroClaw
- prefer environment variables for secrets
- use README examples that show real threshold values and install commands
- keep one skill per directory and one problem per skill

## Review Checklist

- does `skill.yaml` parse as valid YAML?
- are supported agents explicit?
- are thresholds and notification channels configurable?
- does the README explain what the skill does and how to install it?
- does the skill avoid hard-coded secrets or device-specific assumptions?

## Starting Point

Use [`skills/temperature-alert/`](../skills/temperature-alert/) as the reference
implementation for new monitoring skills.
