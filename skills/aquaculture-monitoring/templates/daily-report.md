# Aquaculture Daily Report

Pond: {{ pond_id }}
Date: {{ report_date }}

## Summary

- Overall status: {{ overall_status }}
- Recommended action: {{ recommended_action }}
- Sensor-health status: {{ sensor_health_status }}

## Water Quality

| Metric | Minimum | Average | Maximum | Target |
| --- | ---: | ---: | ---: | --- |
| Dissolved oxygen (mg/L) | {{ do_min }} | {{ do_avg }} | {{ do_max }} | 5.0-9.0 |
| pH | {{ ph_min }} | {{ ph_avg }} | {{ ph_max }} | 6.8-8.2 |
| Water temperature (C) | {{ temp_min }} | {{ temp_avg }} | {{ temp_max }} | 22.0-30.0 |

## Events

- Warning events: {{ warning_count }}
- Critical events: {{ critical_count }}
- Feeding suspensions: {{ feeding_suspension_count }}
- Aerator runtime minutes: {{ aerator_runtime_minutes }}

## Trend Notes

- Overnight dissolved oxygen trough: {{ overnight_do_trough }}
- Heat-related oxygen drop: {{ heat_related_oxygen_drop }}
- pH drift: {{ ph_drift }}
- Aerator recovery time: {{ aerator_recovery_time }}

## Operator Checklist

- [ ] Review any critical event.
- [ ] Confirm aerator relay feedback if emergency mode occurred.
- [ ] Inspect sensors with low battery or stale readings.
- [ ] Confirm feeding can resume if it was suspended.
