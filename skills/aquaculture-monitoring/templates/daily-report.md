# Daily Aquaculture Report

Pond: `{{ pond_id }}`
Window: `{{ report_window_start }}` to `{{ report_window_end }}`

## Current Status

- Dissolved oxygen: `{{ current.dissolved_oxygen_mg_l }} mg/L`
- pH: `{{ current.ph }}`
- Water temperature: `{{ current.water_temperature_c }} C`
- Aerator state: `{{ aerator.state }}`

## 24-Hour Summary

- DO min / avg / max: `{{ daily.dissolved_oxygen.min }}` / `{{ daily.dissolved_oxygen.avg }}` / `{{ daily.dissolved_oxygen.max }} mg/L`
- pH min / avg / max: `{{ daily.ph.min }}` / `{{ daily.ph.avg }}` / `{{ daily.ph.max }}`
- Temperature min / avg / max: `{{ daily.temperature.min }}` / `{{ daily.temperature.avg }}` / `{{ daily.temperature.max }} C`
- Aerator runtime: `{{ daily.aerator_runtime_minutes }} minutes`
- Warning events: `{{ daily.warning_count }}`
- Critical events: `{{ daily.critical_count }}`

## Trend Notes

{{ trend_notes }}

## Recommended Actions

{{ recommended_actions }}
