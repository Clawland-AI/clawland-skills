# Aquaculture Monitoring Skill

A PicClaw declarative aquaculture skill (Clawland bounty issue #19). This is advisory only: it never directly operates a relay or actuator, and deployment to real ponds needs operator-reviewed safety checks and hardware integration.

## Inputs

A sensor event has `pond_id`, `observed_at` (UTC timestamp), `do_mg_l` (mg/L), `ph`, `temperature_c`, `aerator_on` and `feeding_active`.

## Safety thresholds

Dissolved oxygen: <3.0 critical, <5.0 warning, >6.0 recovery; pH: below 6.0 or above 9.0 critical, outside 6.5–8.5 warning; temperature: below 14 or above 35 °C critical, outside 18–30 °C warning. Values are example defaults requiring aquaculture-specific configuration.

Stale (>10 min) or invalid sensor data produces alerts and an aerator-on/feeding-pause recommendation rather than switching off equipment. Aeration uses hysteresis and minimum on/off periods, and never overrides the operator's direct command. Feeding pauses during oxygen danger and other critical water-quality conditions.

## Daily reports and memory

The YAML declares UTC 07:00 daily Markdown reports of minimum/mean/maximum values, threshold excursions, sensor quality, aerator/feed advisories and trends. Bounded 7-day trend memory tracks overnight oxygen troughs, falling oxygen, rising temperature and pH drift, without autonomously relaxing thresholds.

## Testing and limitations

This package contains a Python offline reference evaluator (`scripts/aquaculture.py`), synthetic readings in `examples/`, and automated unit tests in `tests/`.

From the repository root, install `PyYAML` and run:

```bash
python -m pip install -r skills/aquaculture-monitoring/requirements.txt
python -m unittest discover -s skills/aquaculture-monitoring/tests -v
python skills/aquaculture-monitoring/scripts/aquaculture.py --readings skills/aquaculture-monitoring/examples/sensor-readings.json --at 2026-11-01T05:00:00Z --report
```

The local test suite previously passed 22 unit tests; results are from synthetic data, not physical hardware. Clawland's skill schema is pre-alpha and maintainer review is required for runtime compatibility. No real sensors or actuator relays were tested.

## Reward

Candidate for Clawland-AI/clawland-skills#19. No entitlement to the $200 reward unless maintainers assign and accept/merge the contribution. Existing competing pull requests are acknowledged.
