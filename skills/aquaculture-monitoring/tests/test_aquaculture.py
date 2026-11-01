import datetime as dt
import importlib.util
import math
import pathlib
import unittest

HERE = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('aquaculture', HERE / 'scripts' / 'aquaculture.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
CFG = module.load_skill(HERE / 'skill.yaml')
NOW = dt.datetime(2026, 11, 1, 1, 0, 0, tzinfo=dt.timezone.utc)


def reading(**kwargs):
    data = {'pond_id': 'A', 'observed_at': NOW.isoformat(), 'do_mg_l': 7.0,
            'ph': 7.2, 'temperature_c': 26.0, 'aerator_on': False, 'feeding_active': False}
    data.update(kwargs)
    return data


class SkillTests(unittest.TestCase):
    def test_schema_and_safety_flags(self):
        self.assertTrue(module.validate_skill(CFG))
        self.assertFalse(CFG['memory_learning']['autonomous_threshold_relaxation'])

    def test_healthy(self):
        x = module.evaluate(CFG, reading(), NOW)
        self.assertEqual((x['level'], x['aerator_recommendation'], x['feeding_recommendation']), ('normal', 'hold_off', 'normal'))

    def test_warning_oxygen(self):
        x = module.evaluate(CFG, reading(do_mg_l=4.9), NOW)
        self.assertEqual((x['level'], x['aerator_recommendation'], x['feeding_recommendation']), ('warning', 'recommend_on', 'pause'))

    def test_critical_oxygen(self):
        self.assertEqual(module.evaluate(CFG, reading(do_mg_l=2.9), NOW)['level'], 'critical')

    def test_pH_critical(self):
        x = module.evaluate(CFG, reading(ph=9.1), NOW)
        self.assertEqual((x['level'], x['feeding_recommendation']), ('critical', 'pause'))

    def test_temperature_warning_and_critical(self):
        self.assertEqual(module.evaluate(CFG, reading(temperature_c=31), NOW)['level'], 'warning')
        self.assertEqual(module.evaluate(CFG, reading(temperature_c=36), NOW)['level'], 'critical')

    def test_stale_fails_safe(self):
        ts = (NOW - dt.timedelta(minutes=11)).isoformat()
        x = module.evaluate(CFG, reading(observed_at=ts, aerator_on=True), NOW)
        self.assertEqual((x['level'], x['aerator_recommendation'], x['feeding_recommendation']), ('sensor_fault', 'recommend_on', 'pause'))

    def test_nonfinite_and_boolean_rejected(self):
        for bad in (float('nan'), math.inf, True, None):
            self.assertEqual(module.evaluate(CFG, reading(do_mg_l=bad), NOW)['level'], 'sensor_fault')

    def test_future_skew_and_timezone(self):
        self.assertEqual(module.evaluate(CFG, reading(observed_at=(NOW + dt.timedelta(minutes=3)).isoformat()), NOW)['level'], 'sensor_fault')
        self.assertEqual(module.evaluate(CFG, reading(observed_at='2026-11-01T01:00:00'), NOW)['level'], 'sensor_fault')

    def test_aerator_hysteresis(self):
        state = {'seconds_since_aerator_change': 300}
        self.assertEqual(module.evaluate(CFG, reading(aerator_on=True), NOW, state)['aerator_recommendation'], 'hold_on')
        state['seconds_since_aerator_change'] = 901
        self.assertEqual(module.evaluate(CFG, reading(aerator_on=True), NOW, state)['aerator_recommendation'], 'eligible_to_stop_after_operator_review')

    def test_operator_override_prevents_off(self):
        state = {'operator_override_active': True, 'seconds_since_aerator_change': 3600}
        self.assertEqual(module.evaluate(CFG, reading(aerator_on=True), NOW, state)['aerator_recommendation'], 'hold_current')

    def test_never_actuates(self):
        self.assertFalse(module.evaluate(CFG, reading(do_mg_l=1), NOW)['hardware_command_sent'])

    def test_daily_report(self):
        data = [reading(), reading(do_mg_l=2.3)]
        result = module.daily_report(CFG, data, NOW)
        self.assertIn('Critical readings: 1', result)
        self.assertIn('Dissolved oxygen', result)

    def test_memory_bounded(self):
        cfg = dict(CFG)
        cfg['memory_learning'] = dict(CFG['memory_learning'], maximum_samples_per_sensor=2)
        records = [reading(observed_at=(NOW - dt.timedelta(hours=x)).isoformat()) for x in range(5)]
        self.assertEqual(len(module.trim_memory(cfg, records, NOW)), 2)

    def test_trend_detection(self):
        older = (NOW - dt.timedelta(hours=2)).isoformat()
        records = [reading(observed_at=older, do_mg_l=7.0, ph=7.2, temperature_c=24.0),
                   reading(do_mg_l=4.9, ph=7.3, temperature_c=28.0)]
        found = module.trend_observations(CFG, records, NOW)
        self.assertIn('dissolved_oxygen_declining', found)
        self.assertIn('temperature_rising', found)

    def test_trend_requires_history(self):
        self.assertEqual(module.trend_observations(CFG, [reading()], NOW), [])

    def test_yaml_on_value_is_string(self):
        self.assertEqual(CFG['aerator_control']['control_guardrails']['fail_safe_when_unknown'], 'on')

    def test_minimum_off_dwell_and_critical_override(self):
        state = {'seconds_since_aerator_change': 60}
        warning = module.evaluate(CFG, reading(do_mg_l=4.0), NOW, state)
        self.assertEqual(warning['aerator_recommendation'], 'recommend_on_after_minimum_off')
        critical = module.evaluate(CFG, reading(do_mg_l=2.0), NOW, state)
        self.assertEqual(critical['aerator_recommendation'], 'recommend_on')

    def test_memory_cap_is_per_pond(self):
        cfg = dict(CFG)
        cfg['memory_learning'] = dict(CFG['memory_learning'], maximum_samples_per_sensor=2)
        records = [reading(pond_id=pond, observed_at=(NOW - dt.timedelta(hours=i)).isoformat())
                   for pond in ('A', 'B') for i in range(5)]
        trimmed = module.trim_memory(cfg, records, NOW)
        self.assertEqual(len(trimmed), 4)
        self.assertEqual(sum(r['pond_id'] == 'A' for r in trimmed), 2)
        self.assertEqual(sum(r['pond_id'] == 'B' for r in trimmed), 2)

    def test_mixed_pond_trends_rejected(self):
        older = (NOW - dt.timedelta(hours=2)).isoformat()
        records = [reading(pond_id='A', observed_at=older, do_mg_l=7.0),
                   reading(pond_id='B', do_mg_l=2.0)]
        self.assertEqual(module.trend_observations(CFG, records, NOW), [])

    def test_exact_boundary_values(self):
        self.assertEqual(module.evaluate(CFG, reading(do_mg_l=3.0), NOW)['level'], 'warning')
        self.assertEqual(module.evaluate(CFG, reading(do_mg_l=5.0), NOW)['level'], 'normal')
        self.assertEqual(module.evaluate(CFG, reading(ph=9.0), NOW)['level'], 'warning')

    def test_warnings_not_hardcoded_as_actual_relay_success(self):
        result = module.evaluate(CFG, reading(do_mg_l=1.5), NOW)
        self.assertNotIn('activated', str(result).lower())


if __name__ == '__main__':
    unittest.main()
