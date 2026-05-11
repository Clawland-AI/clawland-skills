# Aquaculture Monitoring Skill

`aquaculture-monitoring` teaches Claw agents how to monitor pond water quality, control aeration, and produce a daily operations report.

## What it monitors

| Metric | Target range | Warning | Critical |
| --- | --- | --- | --- |
| Dissolved oxygen | 5.5-8.5 mg/L | `<4.5 mg/L` | `<3.0 mg/L` |
| pH | 7.0-8.5 | `<6.8` or `>8.8` | `<6.5` or `>9.2` |
| Water temperature | 20-30 °C | `<18 °C` or `>32 °C` | `<15 °C` or `>35 °C` |

Tune these values in `skill.yaml` for species, stocking density, season, and local operating practice.

## Aerator control logic

- Normal readings are logged to Memory for trend learning.
- Low dissolved oxygen warning starts the main aerator and sends a warning notification.
- Critical low dissolved oxygen starts both main and backup aerators and escalates to operators.
- pH and temperature excursions notify operators and are written to Memory for daily reporting.
- Fast changes over the configured trend window trigger an anomaly warning even before a hard threshold is crossed.

Relays default to `fail_safe_state: on` because aeration is a life-support function.

## Notification channels

The manifest includes Telegram, Discord, and webhook templates. A gateway or runtime should bind these logical channels to its local secrets/configuration; this skill does not store tokens.

## Memory-based trend learning

The skill writes readings, aerator events, critical events, and anomalies into the `aquaculture.*` Memory namespaces. The `trend_learning` block asks the agent to compare the last 24 hours against a 14-day time-of-day baseline so it can spot patterns such as:

- recurring low oxygen before sunrise,
- pH swings after feeding,
- rapid temperature ramps,
- increasing aerator runtime that may indicate fouling or overstocking.

## Daily report

At 07:00 the skill generates `reports/aquaculture/{{date}}.md` with:

1. water-quality summary,
2. threshold breaches,
3. aerator runtime,
4. trend-learning findings,
5. recommended actions.

## Compatible agents

- PicClaw: full sensor, relay, alert, Memory, and report workflow.
- NanoClaw: regional aggregation and reporting.
- MicroClaw: sensor sampling and relay control; reporting may be forwarded upstream when local storage is constrained.
