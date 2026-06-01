# Daily Aquaculture Water Quality Summary

## Pond

| Field | Value |
| --- | --- |
| Date | `{{date}}` |
| Node ID | `{{node_id}}` |
| Pond ID | `{{pond_id}}` |
| Stocking group | `{{stocking_group}}` |

## Current Status

| Signal | Min | Max | Average | Latest |
| --- | ---: | ---: | ---: | ---: |
| Dissolved oxygen mg/L | `{{do_min}}` | `{{do_max}}` | `{{do_avg}}` | `{{do_latest}}` |
| pH | `{{ph_min}}` | `{{ph_max}}` | `{{ph_avg}}` | `{{ph_latest}}` |
| Water temperature C | `{{temp_min}}` | `{{temp_max}}` | `{{temp_avg}}` | `{{temp_latest}}` |
| Turbidity NTU | `{{turbidity_min}}` | `{{turbidity_max}}` | `{{turbidity_avg}}` | `{{turbidity_latest}}` |

## Threshold Breaches

| Metric | Count | Worst reading | Duration minutes |
| --- | ---: | ---: | ---: |
| Low dissolved oxygen | `{{do_breach_count}}` | `{{do_worst}}` | `{{do_breach_minutes}}` |
| pH outside safe band | `{{ph_breach_count}}` | `{{ph_worst}}` | `{{ph_breach_minutes}}` |
| High turbidity | `{{turbidity_breach_count}}` | `{{turbidity_worst}}` | `{{turbidity_breach_minutes}}` |

## Actuator Activity

| Actuator | Runtime minutes | State changes |
| --- | ---: | ---: |
| Aerator relay | `{{aerator_runtime_minutes}}` | `{{aerator_state_changes}}` |
| Feeder relay | `{{feeder_runtime_minutes}}` | `{{feeder_state_changes}}` |

## Operator Actions

`{{operator_actions}}`

## Memory Trend Summary

`{{trend_summary}}`
