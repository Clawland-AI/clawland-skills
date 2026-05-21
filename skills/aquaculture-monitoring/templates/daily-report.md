# Aquaculture Daily Report

Pond: `{{pond_id}}`
Date: `{{date}}`
Timezone: `{{timezone}}`

## Executive Summary

- Overall status: `{{overall_status}}`
- Highest risk window: `{{highest_risk_window}}`
- Primary action taken: `{{primary_action}}`
- Operator follow-up: `{{operator_follow_up}}`

## Sensor Summary

| Metric | Min | Max | Average | Unit |
| --- | ---: | ---: | ---: | --- |
| Dissolved oxygen | `{{min_dissolved_oxygen_mg_l}}` | `{{max_dissolved_oxygen_mg_l}}` | `{{avg_dissolved_oxygen_mg_l}}` | mg/L |
| pH | `{{min_ph}}` | `{{max_ph}}` | `{{avg_ph}}` | pH |
| Water temperature | `{{min_water_temperature_c}}` | `{{max_water_temperature_c}}` | `{{avg_water_temperature_c}}` | degC |
| Ammonia | `{{min_ammonia_mg_l}}` | `{{max_ammonia_mg_l}}` | `{{avg_ammonia_mg_l}}` | mg/L |
| Nitrite | `{{min_nitrite_mg_l}}` | `{{max_nitrite_mg_l}}` | `{{avg_nitrite_mg_l}}` | mg/L |
| Turbidity | `{{min_turbidity_ntu}}` | `{{max_turbidity_ntu}}` | `{{avg_turbidity_ntu}}` | NTU |

## Oxygen Risk Windows

| Window | Minimum DO | Trigger | Response | Result |
| --- | ---: | --- | --- | --- |
| `{{risk_window_1}}` | `{{risk_window_1_min_do}}` | `{{risk_window_1_trigger}}` | `{{risk_window_1_response}}` | `{{risk_window_1_result}}` |
| `{{risk_window_2}}` | `{{risk_window_2_min_do}}` | `{{risk_window_2_trigger}}` | `{{risk_window_2_response}}` | `{{risk_window_2_result}}` |

## Threshold Breaches

| Time | Parameter | Value | Threshold | Severity | Action |
| --- | --- | ---: | ---: | --- | --- |
| `{{breach_time}}` | `{{breach_parameter}}` | `{{breach_value}}` | `{{breach_threshold}}` | `{{breach_severity}}` | `{{breach_action}}` |

## Aerator Runtime And Verification

- Runtime minutes: `{{aerator_runtime_minutes}}`
- Mode changes: `{{aerator_mode_changes}}`
- Last verified state: `{{last_verified_relay_state}}`
- Recovery events: `{{recovery_events}}`
- Recovery notes: `{{recovery_notes}}`

## Feeding Correlation

- Feeding events: `{{feeding_event_count}}`
- Largest post-feeding oxygen drop: `{{largest_post_feeding_oxygen_drop}}`
- Learned correlation: `{{feeding_correlation_summary}}`

## Memory Learned Trends

- Overnight oxygen trend: `{{overnight_oxygen_trend}}`
- Heat-to-oxygen trend: `{{heat_oxygen_trend}}`
- pH drift trend: `{{ph_drift_trend}}`
- Aerator recovery trend: `{{aerator_recovery_trend}}`
- Confidence: `{{trend_confidence}}`

## Next-Day Actions

1. `{{next_action_1}}`
2. `{{next_action_2}}`
3. `{{next_action_3}}`
