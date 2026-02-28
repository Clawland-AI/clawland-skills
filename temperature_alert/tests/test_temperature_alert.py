#!/usr/bin/env python3
"""Tests for temperature_alert skill."""

import unittest
import tempfile
import os
import json
from unittest.mock import Mock, patch, MagicMock

from temperature_alert import (
    FileSensor, HTTPSensor, SensorConfig, AlertConfig,
    TemperatureAlert, TelegramNotifier, DiscordNotifier, WebhookNotifier
)


class TestFileSensor(unittest.TestCase):
    """Test file sensor functionality."""
    
    def test_read_dallas_format(self):
        """Test reading Dallas 1-wire format."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("aa 01 4b 46 7f ff 0c 10 12 : crc=12 YES\n")
            f.write("aa 01 4b 46 7f ff 0c 10 12 t=23500\n")
            temp_file = f.name
        
        try:
            sensor = FileSensor(temp_file)
            temp = sensor.read_temperature()
            self.assertAlmostEqual(temp, 23.5, places=1)
        finally:
            os.unlink(temp_file)
    
    def test_read_plain_value(self):
        """Test reading plain temperature value."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("25.5")
            temp_file = f.name
        
        try:
            sensor = FileSensor(temp_file)
            temp = sensor.read_temperature()
            self.assertEqual(temp, 25.5)
        finally:
            os.unlink(temp_file)
    
    def test_read_nonexistent_file(self):
        """Test reading non-existent file."""
        sensor = FileSensor('/nonexistent/file')
        temp = sensor.read_temperature()
        self.assertIsNone(temp)


class TestHTTPSensor(unittest.TestCase):
    """Test HTTP sensor functionality."""
    
    @patch('requests.get')
    def test_read_temperature_json(self, mock_get):
        """Test reading temperature from HTTP JSON response."""
        mock_response = Mock()
        mock_response.json.return_value = {'temperature': 25.5}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        sensor = HTTPSensor('http://sensor.local/temp')
        temp = sensor.read_temperature()
        
        self.assertEqual(temp, 25.5)
    
    @patch('requests.get')
    def test_read_temperature_different_keys(self, mock_get):
        """Test reading temperature with different JSON keys."""
        mock_response = Mock()
        mock_response.json.return_value = {'temp': 22.0}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        sensor = HTTPSensor('http://sensor.local/temp')
        temp = sensor.read_temperature()
        
        self.assertEqual(temp, 22.0)


class TestAlertConfig(unittest.TestCase):
    """Test alert configuration."""
    
    def test_default_values(self):
        """Test default configuration values."""
        config = AlertConfig(threshold=30.0)
        
        self.assertEqual(config.threshold, 30.0)
        self.assertEqual(config.hysteresis, 1.0)
        self.assertEqual(config.check_interval, 60)
        self.assertEqual(config.rate_of_change_threshold, 5.0)
    
    def test_custom_values(self):
        """Test custom configuration values."""
        config = AlertConfig(
            threshold=25.0,
            hysteresis=2.0,
            check_interval=30,
            rate_of_change_threshold=10.0
        )
        
        self.assertEqual(config.threshold, 25.0)
        self.assertEqual(config.hysteresis, 2.0)
        self.assertEqual(config.check_interval, 30)
        self.assertEqual(config.rate_of_change_threshold, 10.0)


class TestTemperatureAlert(unittest.TestCase):
    """Test main temperature alert class."""
    
    def test_create_file_sensor(self):
        """Test creating temperature alert with file sensor."""
        sensor_config = SensorConfig(
            sensor_type='file',
            file_path='/tmp/temp'
        )
        alert_config = AlertConfig(threshold=30.0)
        
        alert = TemperatureAlert(sensor_config, alert_config)
        
        self.assertIsInstance(alert.sensor, FileSensor)
    
    def test_create_http_sensor(self):
        """Test creating temperature alert with HTTP sensor."""
        sensor_config = SensorConfig(
            sensor_type='http',
            url='http://sensor.local/temp'
        )
        alert_config = AlertConfig(threshold=30.0)
        
        alert = TemperatureAlert(sensor_config, alert_config)
        
        self.assertIsInstance(alert.sensor, HTTPSensor)
    
    @patch('temperature_alert.requests.post')
    def test_check_alert_triggers(self, mock_post):
        """Test alert triggers when threshold exceeded."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("35.0")
            temp_file = f.name
        
        try:
            sensor_config = SensorConfig(
                sensor_type='file',
                file_path=temp_file
            )
            alert_config = AlertConfig(
                threshold=30.0,
                hysteresis=1.0,
                check_interval=3600,  # Very long to prevent repeated checks
                notification_type='webhook',
                notification_config={'url': 'http://test.com'}
            )
            
            alert = TemperatureAlert(sensor_config, alert_config)
            alert.start(duration=1)
            alert.stop()
            
            self.assertTrue(alert._alert_active)
        finally:
            os.unlink(temp_file)
    
    def test_status(self):
        """Test status reporting."""
        sensor_config = SensorConfig(sensor_type='file', file_path='/tmp/temp')
        alert_config = AlertConfig(threshold=30.0)
        
        alert = TemperatureAlert(sensor_config, alert_config)
        status = alert.status()
        
        self.assertIn('running', status)
        self.assertIn('current_temp', status)
        self.assertIn('alert_active', status)


class TestNotifiers(unittest.TestCase):
    """Test notification classes."""
    
    @patch('temperature_alert.requests.post')
    def test_telegram_notifier(self, mock_post):
        """Test Telegram notification."""
        notifier = TelegramNotifier({
            'bot_token': 'test_token',
            'chat_id': '123456'
        })
        
        notifier.send('Test message', 35.0, True)
        
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertIn('sendMessage', call_args[0][0])
    
    @patch('temperature_alert.requests.post')
    def test_discord_notifier(self, mock_post):
        """Test Discord notification."""
        notifier = DiscordNotifier({
            'webhook_url': 'https://discord.com/api/webhooks/test'
        })
        
        notifier.send('Test message', 35.0, True)
        
        mock_post.assert_called_once()
    
    @patch('temperature_alert.requests.post')
    def test_webhook_notifier(self, mock_post):
        """Test generic webhook notification."""
        notifier = WebhookNotifier({
            'url': 'https://test.com/webhook'
        })
        
        notifier.send('Test message', 35.0, True)
        
        mock_post.assert_called_once()


if __name__ == '__main__':
    unittest.main()
