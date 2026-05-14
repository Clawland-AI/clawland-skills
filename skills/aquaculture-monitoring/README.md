# Aquaculture Monitoring Skill

PicClaw YAML skill for pond water-quality monitoring. It watches dissolved oxygen (DO), pH, and temperature, controls an aerator relay, produces a daily markdown report, and uses PicClaw memory to learn recurring pond trends.

## What It Covers

- DO thresholds for warning, critical, recovery, nighttime watch, and rapid-drop detection.
- pH and water-temperature warning and critical thresholds.
- Aerator control modes: off, low pulse, high continuous, and emergency continuous.
- Daily report generation with sensor summaries, threshold breaches, aerator runtime, recovery events, and next-day recommendations.
- Memory-based trend learning for overnight DO troughs, heat-related DO drops, slow aerator recovery, and pH drift.

## Install

```bash
picclaw skill install aquaculture-monitoring
```

For local development, copy this directory to the PicClaw workspace:

```bash
mkdir -p ~/.picclaw/skills
cp -R skills/aquaculture-monitoring ~/.picclaw/skills/
```

## Expected Inputs

The skill expects water-quality readings from the configured sensor tool:

```json
{
  "pond_id": "pond-01",
  "dissolved_oxygen": 4.8,
  "ph": 7.4,
  "temperature": 29.1,
  "timestamp": "2026-05-15T18:30:00+08:00"
}
```

Relay control is expressed through the `control_relay` tool using relay `aerator_main`, channel `1`.

## Operating Behavior

PicClaw should evaluate the rules in `skill.yaml` in priority order. Critical DO always wins: the aerator is switched to emergency continuous mode, notifications are sent, and DO is rechecked every 10 minutes. Learned trends can start preventive low-mode aeration, but they must never suppress critical alerts or hard safety thresholds.

Daily reports are written to:

```text
reports/aquaculture/{{pond_id}}/{{date}}.md
```

Trend summaries are written to `memory/MEMORY.md` and recent daily notes under `memory/YYYYMM/YYYYMMDD.md`.
