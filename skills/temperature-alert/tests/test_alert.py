#!/usr/bin/env python3
"""
Unit tests for Temperature Alert Skill

Run with: python3 -m pytest tests/test_alert.py
"""

import pytest
import yaml
from pathlib import Path
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path to import alert module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from alert import TemperatureAlert


class TestTemperatureAlert:
    """Test suite for TemperatureAlert class"""
    
    @pytest.fixture
    def config_file(self, tmp_path):
        """Create a temporary config file for testing"""
        config = {
            'sensor': 'sht40',
            'sensor_pin': 'I2C:0x44',
            'thresholds': {
                'high_warning': 28.0,
                'high_critical': 35.0,
                'low_warning': 5.0,
                'low_critical': 0.0,
                'rate_of_change': 5.0
            },
            'notifications': {
                'telegram': {
                    'enabled': False
                },
                'discord': {
                    'enabled': False
                },
                'webhook': {
                    'enabled': False
                },
                'cooldown': 300
            }
        }
        
        config_path = tmp_path / "test_config.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(config, f)
        
        return str(config_path)
    
    def test_load_config(self, config_file):
        """Test configuration loading"""
        alert = TemperatureAlert(config_file)
        assert alert.config['sensor'] == 'sht40'
        assert alert.config['thresholds']['high_warning'] == 28.0
    
    def test_check_thresholds_normal(self, config_file):
        """Test temperature within normal range"""
        alert = TemperatureAlert(config_file)
        severity, message = alert.check_thresholds(22.0)
        assert severity == 'normal'
        assert 'normal' in message.lower()
    
    def test_check_thresholds_high_warning(self, config_file):
        """Test high warning threshold"""
        alert = TemperatureAlert(config_file)
        severity, message = alert.check_thresholds(30.0)
        assert severity == 'high_warning'
        assert 'warning' in message.lower()
    
    def test_check_thresholds_high_critical(self, config_file):
        """Test high critical threshold"""
        alert = TemperatureAlert(config_file)
        severity, message = alert.check_thresholds(40.0)
        assert severity == 'high_critical'
        assert 'critical' in message.lower()
    
    def test_check_thresholds_low_warning(self, config_file):
        """Test low warning threshold"""
        alert = TemperatureAlert(config_file)
        severity, message = alert.check_thresholds(3.0)
        assert severity == 'low_warning'
        assert 'warning' in message.lower()
    
    def test_check_thresholds_low_critical(self, config_file):
        """Test low critical threshold"""
        alert = TemperatureAlert(config_file)
        severity, message = alert.check_thresholds(-2.0)
        assert severity == 'low_critical'
        assert 'critical' in message.lower()
    
    def test_rate_of_change_detection(self, config_file):
        """Test rapid temperature change detection"""
        alert = TemperatureAlert(config_file)
        
        # Set initial temperature
        alert.last_temp = 20.0
        alert.last_temp_time = datetime.now() - timedelta(minutes=1)
        
        # Simulate rapid change (10°C in 1 minute)
        result = alert.check_rate_of_change(30.0)
        assert result is not None
        severity, message = result
        assert severity == 'rapid_change'
        assert 'rapid' in message.lower()
    
    def test_rate_of_change_normal(self, config_file):
        """Test normal temperature change rate"""
        alert = TemperatureAlert(config_file)
        
        # Set initial temperature
        alert.last_temp = 20.0
        alert.last_temp_time = datetime.now() - timedelta(minutes=5)
        
        # Simulate slow change (3°C in 5 minutes = 0.6°C/min)
        result = alert.check_rate_of_change(23.0)
        assert result is None
    
    def test_cooldown_mechanism(self, config_file):
        """Test alert cooldown to prevent spam"""
        alert = TemperatureAlert(config_file)
        
        # First alert should be allowed
        assert alert.should_send_alert('high_warning') is True
        
        # Record alert
        alert.last_alert_time['high_warning'] = datetime.now()
        
        # Immediate second alert should be blocked
        assert alert.should_send_alert('high_warning') is False
        
        # Alert after cooldown period should be allowed
        alert.last_alert_time['high_warning'] = datetime.now() - timedelta(seconds=301)
        assert alert.should_send_alert('high_warning') is True
    
    def test_sensor_types(self, config_file):
        """Test different sensor type support"""
        alert = TemperatureAlert(config_file)
        
        # Test that sensor reading methods exist (mock implementations)
        assert callable(getattr(alert, '_read_sht40', None))
        assert callable(getattr(alert, '_read_dht22', None))
        assert callable(getattr(alert, '_read_bme280', None))
        assert callable(getattr(alert, '_read_dallas', None))
    
    def test_notification_config(self, config_file):
        """Test notification configuration parsing"""
        alert = TemperatureAlert(config_file)
        
        telegram_config = alert.config['notifications']['telegram']
        assert 'enabled' in telegram_config
        assert telegram_config['enabled'] is False
        
        discord_config = alert.config['notifications']['discord']
        assert 'enabled' in discord_config
        
        webhook_config = alert.config['notifications']['webhook']
        assert 'enabled' in webhook_config


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_missing_config_file(self):
        """Test handling of missing configuration file"""
        with pytest.raises(FileNotFoundError):
            TemperatureAlert('nonexistent_config.yaml')
    
    def test_invalid_yaml(self, tmp_path):
        """Test handling of invalid YAML syntax"""
        bad_config = tmp_path / "bad_config.yaml"
        with open(bad_config, 'w') as f:
            f.write("{ invalid: yaml: syntax")
        
        with pytest.raises(yaml.YAMLError):
            TemperatureAlert(str(bad_config))
    
    def test_boundary_temperatures(self, tmp_path):
        """Test temperature readings at exact threshold boundaries"""
        config = {
            'sensor': 'sht40',
            'thresholds': {
                'high_warning': 30.0,
                'high_critical': 40.0,
                'low_warning': 10.0,
                'low_critical': 0.0
            },
            'notifications': {'cooldown': 300}
        }
        
        config_path = tmp_path / "boundary_config.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(config, f)
        
        alert = TemperatureAlert(str(config_path))
        
        # Test exact threshold values
        severity, _ = alert.check_thresholds(30.0)
        assert severity == 'high_warning'
        
        severity, _ = alert.check_thresholds(40.0)
        assert severity == 'high_critical'
        
        severity, _ = alert.check_thresholds(10.0)
        assert severity == 'low_warning'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
