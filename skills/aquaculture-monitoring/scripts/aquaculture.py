#!/usr/bin/env python3
"""Offline reference evaluator for the declarative Clawland aquaculture YAML skill.

This is NOT a device driver. Its output is advice for human/trusted-controller review.
"""
import argparse
import datetime as dt
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

import yaml

UTC = dt.timezone.utc


def load_skill(path):
    data = yaml.safe_load(Path(path).read_text(encoding='utf-8'))
    validate_skill(data)
    return data


def validate_skill(config):
    keys = {'name', 'version', 'agent', 'triggers', 'tools', 'thresholds',
            'aerator_control', 'feeding_guardrails', 'daily_report',
            'memory_learning', 'actions', 'sensor_health', 'sensor_mapping'}
    missing = keys - set(config)
    if missing:
        raise ValueError(f"missing required fields: {sorted(missing)}")
    if config['name'] != 'aquaculture-monitoring':
        raise ValueError('wrong skill name')
    if config['aerator_control']['mode'] != 'recommend_only':
        raise ValueError('hardware actuation is not supported by this evaluator')
    if config['aerator_control']['control_guardrails']['fail_safe_when_unknown'] != 'on':
        raise ValueError('unknown-state fail-safe must recommend on')
    t = config['thresholds']
    oxygen = t['dissolved_oxygen']
    if not (oxygen['critical_low'] < oxygen['warning_low'] < oxygen['recovery_high']):
        raise ValueError('dissolved oxygen thresholds are unordered')
    for field in ('ph', 'temperature'):
        v = t[field]
        if not (v['critical_low'] < v['warning_low'] < v['warning_high'] < v['critical_high']):
            raise ValueError(f'{field} thresholds are unordered')
    if config['memory_learning']['maximum_samples_per_sensor'] <= 0:
        raise ValueError('memory cap must be positive')
    if config['memory_learning']['autonomous_threshold_relaxation'] is not False:
        raise ValueError('autonomous threshold relaxation is unsafe')
    return True


def parse_time(value):
    if not isinstance(value, str):
        raise ValueError('observed_at must be ISO-8601 string')
    when = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
    if when.tzinfo is None:
        raise ValueError('observed_at requires timezone')
    return when.astimezone(UTC)


def evaluate(config, reading, now=None, state=None):
    """Return safety-oriented advisory without sending commands to hardware."""
    if state is None:
        state = {}
    now = now or dt.datetime.now(UTC)
    if now.tzinfo is None:
        raise ValueError('now must be timezone-aware')
    h = config['sensor_health']
    issues = []
    try:
        timestamp = parse_time(reading.get('observed_at'))
        age = (now - timestamp).total_seconds()
        if age > h['maximum_age_seconds']:
            issues.append('stale_sensor_data')
        if age < -h['reject_future_skew_seconds']:
            issues.append('future_timestamp')
    except (ValueError, TypeError):
        issues.append('invalid_timestamp')

    fields = {'dissolved_oxygen': 'do_mg_l', 'ph': 'ph', 'temperature': 'temperature_c'}
    valid = {}
    for name, key in fields.items():
        raw = reading.get(key)
        if isinstance(raw, bool) or not isinstance(raw, (int, float)) or not math.isfinite(raw):
            issues.append('invalid_' + name)
            continue
        allowed = h['valid_ranges'][name]
        if not allowed['minimum'] <= raw <= allowed['maximum']:
            issues.append('out_of_range_' + name)
            continue
        valid[name] = float(raw)

    severities = {}
    t = config['thresholds']
    if not issues:
        oxygen = valid['dissolved_oxygen']
        severities['dissolved_oxygen'] = ('critical' if oxygen < t['dissolved_oxygen']['critical_low']
                                         else 'warning' if oxygen < t['dissolved_oxygen']['warning_low'] else 'normal')
        for name in ('ph', 'temperature'):
            v, limits = valid[name], t[name]
            severities[name] = ('critical' if v < limits['critical_low'] or v > limits['critical_high']
                                else 'warning' if v < limits['warning_low'] or v > limits['warning_high'] else 'normal')
    # Unknown measurements are handled fail-safe. Never recommend shutting OFF an aerator on bad data.
    critical = 'critical' in severities.values()
    oxygen_alarm = severities.get('dissolved_oxygen') in ('critical', 'warning')
    feeding_pause = bool(issues or oxygen_alarm or critical)
    aerator_on = reading.get('aerator_on')
    override = state.get('operator_override_active', False)
    elapsed = state.get('seconds_since_aerator_change')
    if issues or (severities.get('dissolved_oxygen') == 'critical'):
        aerator_advice = 'recommend_on'
    elif oxygen_alarm:
        if (aerator_on is False and isinstance(elapsed, (int, float))
                and not isinstance(elapsed, bool) and 0 <= elapsed < config['aerator_control']['minimum_off_seconds']):
            aerator_advice = 'recommend_on_after_minimum_off'
        else:
            aerator_advice = 'recommend_on'
    elif critical or override:
        aerator_advice = 'hold_current'
    elif aerator_on is True:
        if (valid.get('dissolved_oxygen', -1) >= t['dissolved_oxygen']['recovery_high']
                and isinstance(elapsed, (int, float)) and not isinstance(elapsed, bool)
                and elapsed >= config['aerator_control']['minimum_on_seconds']):
            aerator_advice = 'eligible_to_stop_after_operator_review'
        else:
            aerator_advice = 'hold_on'
    elif aerator_on is False:
        aerator_advice = 'hold_off'
    else:
        aerator_advice = 'recommend_on'  # Unknown actuator feedback also fails safe.
    if issues:
        level = 'sensor_fault'
    elif critical:
        level = 'critical'
    elif 'warning' in severities.values():
        level = 'warning'
    else:
        level = 'normal'
    return {'pond_id': reading.get('pond_id'), 'level': level,
            'sensor_issues': sorted(set(issues)), 'severities': severities,
            'aerator_recommendation': aerator_advice,
            'feeding_recommendation': 'pause' if feeding_pause else 'normal',
            'hardware_command_sent': False}



def trend_observations(config, readings, now):
    """Derive bounded warning *hints* from observed history; never tune limits automatically."""
    policy = config['memory_learning']
    window = dt.timedelta(days=policy['rolling_window_days'])
    end = now.astimezone(UTC)
    signals = []
    cleaned = []
    for item in readings:
        try:
            timestamp = parse_time(item['observed_at'])
        except (KeyError, ValueError, TypeError):
            continue
        if not end - window <= timestamp <= end:
            continue
        # Evaluate using observation time to isolate sensor value integrity.
        if evaluate(config, item, now=timestamp)['sensor_issues']:
            continue
        cleaned.append((timestamp, item))
    cleaned.sort(key=lambda entry: entry[0])
    if len(cleaned) < 2:
        return signals
    # Never derive a trend by comparing different ponds' sensor readings.
    pond_ids = {str(sample.get('pond_id')) for _, sample in cleaned}
    if len(pond_ids) != 1:
        return signals
    first, last = cleaned[0], cleaned[-1]
    elapsed_hours = (last[0] - first[0]).total_seconds() / 3600.0
    if elapsed_hours < 1:
        return signals
    delta_do_per_hour = (last[1]['do_mg_l'] - first[1]['do_mg_l']) / elapsed_hours
    delta_temp_per_hour = (last[1]['temperature_c'] - first[1]['temperature_c']) / elapsed_hours
    delta_ph_per_day = (last[1]['ph'] - first[1]['ph']) / (elapsed_hours / 24.0)
    trend_limits = policy['trend_detection']
    if delta_do_per_hour <= trend_limits['do_declining_delta_mg_l_per_hour']:
        signals.append('dissolved_oxygen_declining')
    if delta_temp_per_hour >= trend_limits['temperature_rising_delta_c_per_hour']:
        signals.append('temperature_rising')
    if abs(delta_ph_per_day) >= trend_limits['ph_drift_delta_per_day']:
        signals.append('ph_drifting')
    if trend_limits['early_morning_do_trough']:
        # A trough requires >=3 distinct readings in the operator's UTC timezone demo.
        nighttime = [(when, sample['do_mg_l']) for when, sample in cleaned if 0 <= when.hour <= 6]
        if len(nighttime) >= 3 and min(value for _, value in nighttime) < config['thresholds']['dissolved_oxygen']['warning_low']:
            signals.append('early_morning_oxygen_trough')
    return sorted(set(signals))


def daily_report(config, readings, now):
    """Report based on recent readings only; no unverified hardware readings."""
    end = now.astimezone(UTC)
    begin = end - dt.timedelta(days=1)
    grouped = defaultdict(list)
    events = []
    for record in readings:
        try:
            when = parse_time(record['observed_at'])
        except (ValueError, KeyError, TypeError):
            continue
        if not begin <= when <= end:
            continue
        result = evaluate(config, record, now=when)
        grouped[record.get('pond_id', 'unknown')].append((record, result))
        if result['level'] != 'normal':
            events.append((record.get('pond_id', 'unknown'), result['level']))
    lines = ['# Aquaculture daily water-quality report', f'Period: {begin.isoformat()} to {end.isoformat()}',
             'All data supplied by caller; no hardware verification has been performed.']
    for pond, items in sorted(grouped.items()):
        lines.append(f'\n## {pond}')
        lines.append(f'Readings received: {len(items)}')
        for field, name, unit in (('do_mg_l', 'Dissolved oxygen', 'mg/L'), ('ph', 'pH', ''), ('temperature_c', 'Temperature', '°C')):
            nums = [rec[field] for rec, r in items if not r['sensor_issues'] and isinstance(rec.get(field), (int, float))]
            if nums:
                lines.append(f'{name}: min {min(nums):.2f}, mean {statistics.mean(nums):.2f}, max {max(nums):.2f} {unit}'.strip())
        for label in ('critical', 'warning', 'sensor_fault'):
            count = sum(r['level'] == label for _, r in items)
            lines.append(f'{label.replace("_", " ").capitalize()} readings: {count}')
        lines.append('Aerator ON recommendations: ' + str(sum(r['aerator_recommendation'] == 'recommend_on' for _, r in items)))
        lines.append('Feeding pauses recommended: ' + str(sum(r['feeding_recommendation'] == 'pause' for _, r in items)))
        trends = trend_observations(config, [item for item, _ in items], end)
        lines.append('Trend observations (advisory): ' + (', '.join(trends) if trends else 'none'))
    if not grouped:
        lines.append('\nNo readings in this period.')
    return '\n'.join(lines) + '\n'


def trim_memory(config, timestamped_samples, now):
    """Keep a bounded, chronological per-sensor history; no personal data."""
    cutoff = now - dt.timedelta(days=config['memory_learning']['retention_days'])
    cap = config['memory_learning']['maximum_samples_per_sensor']
    groups = defaultdict(list)
    for item in timestamped_samples:
        try:
            when = parse_time(item['observed_at'])
        except (ValueError, KeyError, TypeError):
            continue
        if cutoff <= when <= now:
            # A pond_id is the synthetic sensor-series key for this demo.
            groups[str(item.get('pond_id', 'unknown'))].append((when, item))
    result = []
    for group in groups.values():
        result.extend(item for _, item in sorted(group, key=lambda pair: pair[0])[-cap:])
    return [item for _, item in sorted(((parse_time(item['observed_at']), item) for item in result), key=lambda pair: pair[0])]


def main():
    cli = argparse.ArgumentParser()
    cli.add_argument('--config', default=str(Path(__file__).resolve().parents[1] / 'skill.yaml'))
    cli.add_argument('--readings', required=True)
    cli.add_argument('--at', default=None, help='Optional ISO-8601 current time for reproducible demos')
    cli.add_argument('--report', action='store_true')
    args = cli.parse_args()
    config = load_skill(args.config)
    now = parse_time(args.at) if args.at else dt.datetime.now(UTC)
    records = json.loads(Path(args.readings).read_text(encoding='utf-8'))
    if args.report:
        print(daily_report(config, records, now))
    else:
        for item in records:
            print(json.dumps(evaluate(config, item, now=now), sort_keys=True))


if __name__ == '__main__':
    main()
