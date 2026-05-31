# Daily Cold Chain Compliance Report

Date: `{{report_date}}`

Site: `{{site_id}}`

Asset: `{{asset_id}}`

Active profile: `{{active_profile}}`

Prepared by: `{{operator_id}}`

## Executive Status

- Overall status: `{{overall_status}}`
- Product release decision: `{{release_decision}}`
- Lots under quarantine: `{{quarantined_lots}}`
- Open corrective actions: `{{open_corrective_actions}}`

## Temperature Compliance

| Metric | Minimum | Maximum | Allowed band | Excursion count | Longest excursion |
| --- | ---: | ---: | --- | ---: | --- |
| Air temperature | `{{air_temperature_min}}` | `{{air_temperature_max}}` | `{{temperature_band}}` | `{{air_temperature_excursions}}` | `{{air_temperature_longest_excursion}}` |
| Product temperature | `{{product_temperature_min}}` | `{{product_temperature_max}}` | `{{temperature_band}}` | `{{product_temperature_excursions}}` | `{{product_temperature_longest_excursion}}` |

## Humidity Compliance

| Minimum RH | Maximum RH | Allowed band | Excursion count | Corrective action required |
| ---: | ---: | --- | ---: | --- |
| `{{humidity_min}}` | `{{humidity_max}}` | `{{humidity_band}}` | `{{humidity_excursions}}` | `{{humidity_action_required}}` |

## Door and Custody Events

| Time | Event | Operator | Duration | Notes |
| --- | --- | --- | --- | --- |
| `{{custody_event_time}}` | `{{custody_event_type}}` | `{{custody_operator}}` | `{{custody_duration}}` | `{{custody_notes}}` |

## Excursions and Corrective Actions

| Time | Severity | Affected lot | Condition | Corrective action | Owner | Status |
| --- | --- | --- | --- | --- | --- | --- |
| `{{excursion_time}}` | `{{excursion_severity}}` | `{{affected_lot}}` | `{{excursion_condition}}` | `{{corrective_action}}` | `{{action_owner}}` | `{{action_status}}` |

## Sensor Health

- Stale sensors: `{{stale_sensor_count}}`
- Calibration due within 7 days: `{{calibration_due_count}}`
- Probe drift warnings: `{{probe_drift_warnings}}`

## Audit Integrity

- First record hash: `{{first_record_hash}}`
- Last record hash: `{{last_record_hash}}`
- Hash chain status: `{{hash_chain_status}}`
- Records exported to CSV: `{{csv_record_count}}`
- PDF-ready report generated: `{{pdf_ready}}`

## Trend Insights

`{{trend_learning_insights}}`

## QA Review

- Reviewer: `{{qa_reviewer}}`
- Review time: `{{qa_review_time}}`
- Decision: `{{qa_decision}}`
- Signature: `{{qa_signature}}`
