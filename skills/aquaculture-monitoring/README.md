# Aquaculture Monitoring Skill

A PicClaw declarative aquaculture skill (Clawland bounty issue #19). This is advisory only: it never directly operates a relay or actuator, and deployment to real ponds needs operator-reviewed safety checks and hardware integration.

## Inputs

A sensor event has `pond_id`, `observed_at` (UTC timestamp), `do_mg_l` (mg/L), `ph`, `temperature_c`, `aerator_on` and `feeding_active`.

## Safety thresholds

Dissolved oxygen: &lt;3.0 critical, &lt;5.0 warning, &gt;6.0 recovery; pH: below 6.0 or above 9.0 critical, outside 6.5–8.5 warning; temperature: below 14 or above 35 °C critical, outside 18–30 °C warning. Values are example defaults requiring aquaculture-specific configuration.

Stale (&gt;10 min) or invalid sensor data produces alerts and an aerator-on/feeding-pause recommendation rather than switching off equipment. Aeration uses hysteresis and minimum on/off periods, and never overrides the operator's direct command. Feeding pauses during oxygen danger and other critical water-quality conditions.

## Daily reports and memory

The YAML declares UTC 07:00 daily Markdown reports of minimum/mean/maximum values, threshold excursions, sensor quality, aerator/feed advisories and trends. Bounded 7-day trend memory tracks overnight oxygen troughs, falling oxygen, rising temperature and pH drift, without autonomously relaxing thresholds.

## Testing and limitations

This package was independently developed with a separate Python offline evaluator and 17 local automated tests in the source submission ZIP. Those reference scripts and synthetic sample readings must be included before claiming a complete validated submission. The project's skill YAML schema is pre-alpha, and maintainers must confirm runtime compatibility. No real sensor or relay hardware was tested.

## Reward

Candidate for Clawland-AI/clawland-skills#19. No entitlement to the $200 reward unless maintainers assign and accept/merge the contribution. Existing competing pull requests are acknowledged.
