#!/usr/bin/env python3
"""
Temperature Alert Skill - Core Implementation

Monitors temperature sensors and sends multi-channel alerts based on configurable thresholds.
Compatible with PicClaw, NanoClaw, MicroClaw, and MoltClaw.

Author: Clawland Community
License: MIT
"""

import os
import time
import json
import yaml
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('temperature-alert')


class TemperatureAlert:
    """Temperature monitoring and alerting system"""
    
    def __init__(self, config_path: str = 'config.yaml'):
        """Initialize the temperature alert system
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.last_alert_time = {}  # Track last alert time per severity
        self.last_temp = None
        self.last_temp_time = None
        
        # State file for persistence across restarts
        self.state_file = Path('temperature_alert_state.json')
        self._load_state()
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Loaded configuration from {config_path}")
            return config
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {config_path}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Invalid YAML in configuration: {e}")
            raise
    
    def _load_state(self):
        """Load persistent state from file"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                self.last_temp = state.get('last_temp')
                self.last_temp_time = state.get('last_temp_time')
                if self.last_temp_time:
                    self.last_temp_time = datetime.fromisoformat(self.last_temp_time)
                # Restore cooldown state
                last_alert_data = state.get('last_alert_time', {})
                self.last_alert_time = {k: datetime.fromisoformat(v) for k, v in last_alert_data.items()}
                logger.info("Loaded previous state")
            except Exception as e:
                logger.warning(f"Could not load state: {e}")
    
    def _save_state(self):
        """Save persistent state to file"""
        try:
            state = {
                'last_temp': self.last_temp,
                'last_temp_time': self.last_temp_time.isoformat() if self.last_temp_time else None,
                'last_alert_time': {k: v.isoformat() for k, v in self.last_alert_time.items()}
            }
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not save state: {e}")
    
    def read_temperature(self) -> Optional[float]:
        """Read temperature from configured sensor
        
        Returns:
            Temperature in Celsius, or None if reading failed
        """
        sensor_type = self.config.get('sensor', '').lower()
        sensor_pin = self.config.get('sensor_pin', 'auto')
        
        # In a real implementation, this would interface with actual sensors
        # For now, we provide a mock implementation and plugin architecture
        
        try:
            if sensor_type == 'sht40':
                return self._read_sht40(sensor_pin)
            elif sensor_type == 'dht22':
                return self._read_dht22(sensor_pin)
            elif sensor_type == 'bme280':
                return self._read_bme280(sensor_pin)
            elif sensor_type == 'dallas':
                return self._read_dallas(sensor_pin)
            else:
                logger.error(f"Unsupported sensor type: {sensor_type}")
                return None
        except Exception as e:
            logger.error(f"Error reading sensor: {e}")
            return None
    
    def _read_sht40(self, pin: str) -> float:
        """Read from SHT40 sensor (I2C)
        
        This is a placeholder. Real implementation would use smbus2 or adafruit-circuitpython-sht4x
        """
        # TODO: Implement actual sensor reading
        # Example: from adafruit_sht4x import SHT4x
        logger.info(f"Reading SHT40 sensor on {pin}")
        # Mock reading for demonstration
        return 22.5
    
    def _read_dht22(self, pin: str) -> float:
        """Read from DHT22 sensor (GPIO)"""
        logger.info(f"Reading DHT22 sensor on {pin}")
        # TODO: Implement using Adafruit_DHT library
        return 23.0
    
    def _read_bme280(self, pin: str) -> float:
        """Read from BME280 sensor (I2C/SPI)"""
        logger.info(f"Reading BME280 sensor on {pin}")
        # TODO: Implement using adafruit-circuitpython-bme280
        return 24.5
    
    def _read_dallas(self, pin: str) -> float:
        """Read from Dallas DS18B20 sensor (1-Wire)"""
        logger.info(f"Reading Dallas sensor on {pin}")
        # TODO: Implement using w1thermsensor
        return 25.0
    
    def check_thresholds(self, temp: float) -> Tuple[str, str]:
        """Check if temperature exceeds thresholds
        
        Args:
            temp: Current temperature in Celsius
        
        Returns:
            Tuple of (severity, message) where severity is:
            'normal', 'high_warning', 'high_critical', 'low_warning', 'low_critical'
        """
        thresholds = self.config.get('thresholds', {})
        
        high_critical = thresholds.get('high_critical', 45.0)
        high_warning = thresholds.get('high_warning', 35.0)
        low_warning = thresholds.get('low_warning', 5.0)
        low_critical = thresholds.get('low_critical', 0.0)
        
        if temp >= high_critical:
            return ('high_critical', 
                    f'🚨 CRITICAL: Temperature {temp}°C exceeds critical threshold {high_critical}°C!')
        elif temp >= high_warning:
            return ('high_warning', 
                    f'⚠️ WARNING: Temperature {temp}°C exceeds warning threshold {high_warning}°C')
        elif temp <= low_critical:
            return ('low_critical', 
                    f'🥶 CRITICAL: Temperature {temp}°C below critical threshold {low_critical}°C!')
        elif temp <= low_warning:
            return ('low_warning', 
                    f'❄️ WARNING: Temperature {temp}°C below warning threshold {low_warning}°C')
        else:
            return ('normal', f'Temperature normal: {temp}°C')
    
    def check_rate_of_change(self, temp: float) -> Optional[Tuple[str, str]]:
        """Check if temperature is changing too rapidly
        
        Args:
            temp: Current temperature in Celsius
        
        Returns:
            Tuple of (severity, message) if rate exceeded, None otherwise
        """
        if self.last_temp is None or self.last_temp_time is None:
            return None
        
        time_diff = (datetime.now() - self.last_temp_time).total_seconds() / 60  # minutes
        if time_diff == 0:
            return None
        
        temp_diff = abs(temp - self.last_temp)
        rate = temp_diff / time_diff
        
        max_rate = self.config.get('thresholds', {}).get('rate_of_change', 5.0)
        
        if rate > max_rate:
            return ('rapid_change', 
                    f'⚡ ALERT: Rapid temperature change detected: {rate:.1f}°C/min '
                    f'(threshold: {max_rate}°C/min)')
        
        return None
    
    def should_send_alert(self, severity: str) -> bool:
        """Check if enough time has passed since last alert (cooldown)
        
        Args:
            severity: Alert severity level
        
        Returns:
            True if alert should be sent, False if in cooldown period
        """
        cooldown = self.config.get('notifications', {}).get('cooldown', 300)
        last_alert = self.last_alert_time.get(severity)
        
        if last_alert is None:
            return True
        
        time_since_last = (datetime.now() - last_alert).total_seconds()
        return time_since_last >= cooldown
    
    def send_telegram_alert(self, message: str) -> bool:
        """Send alert via Telegram
        
        Args:
            message: Alert message to send
        
        Returns:
            True if successful, False otherwise
        """
        telegram_config = self.config.get('notifications', {}).get('telegram', {})
        
        if not telegram_config.get('enabled', False):
            return False
        
        bot_token = telegram_config.get('bot_token', '')
        chat_id = telegram_config.get('chat_id', '')
        
        if not bot_token or not chat_id:
            logger.warning("Telegram enabled but credentials missing")
            return False
        
        try:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            logger.info("Telegram alert sent successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to send Telegram alert: {e}")
            return False
    
    def send_discord_alert(self, message: str) -> bool:
        """Send alert via Discord webhook
        
        Args:
            message: Alert message to send
        
        Returns:
            True if successful, False otherwise
        """
        discord_config = self.config.get('notifications', {}).get('discord', {})
        
        if not discord_config.get('enabled', False):
            return False
        
        webhook_url = discord_config.get('webhook_url', '')
        
        if not webhook_url:
            logger.warning("Discord enabled but webhook URL missing")
            return False
        
        try:
            payload = {
                'content': message,
                'username': 'Temperature Alert Bot'
            }
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            logger.info("Discord alert sent successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to send Discord alert: {e}")
            return False
    
    def send_webhook_alert(self, severity: str, temp: float, message: str) -> bool:
        """Send alert via custom webhook
        
        Args:
            severity: Alert severity level
            temp: Current temperature
            message: Alert message
        
        Returns:
            True if successful, False otherwise
        """
        webhook_config = self.config.get('notifications', {}).get('webhook', {})
        
        if not webhook_config.get('enabled', False):
            return False
        
        url = webhook_config.get('url', '')
        headers = webhook_config.get('headers', {})
        
        if not url:
            logger.warning("Webhook enabled but URL missing")
            return False
        
        try:
            # Extract threshold value based on severity
            # Map severity name to config key ('rapid_change' -> 'rate_of_change')
            severity_to_config_key = {
                'rapid_change': 'rate_of_change'
            }
            thresholds = self.config.get('thresholds', {})
            config_key = severity_to_config_key.get(severity, severity)
            threshold_value = thresholds.get(config_key, None)
            
            payload = {
                'event': 'temperature_alert',
                'severity': severity,
                'temperature': temp,
                'threshold': threshold_value,
                'sensor': self.config.get('sensor', 'unknown'),
                'timestamp': datetime.now().isoformat(),
                'message': message
            }
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            logger.info("Webhook alert sent successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to send webhook alert: {e}")
            return False
    
    def send_alert(self, severity: str, temp: float, message: str):
        """Send alert via all enabled channels
        
        Args:
            severity: Alert severity level
            temp: Current temperature
            message: Alert message
        """
        if not self.should_send_alert(severity):
            logger.info(f"Alert suppressed due to cooldown: {severity}")
            return
        
        logger.info(f"Sending alert: {message}")
        
        # Send to all enabled channels
        self.send_telegram_alert(message)
        self.send_discord_alert(message)
        self.send_webhook_alert(severity, temp, message)
        
        # Update last alert time
        self.last_alert_time[severity] = datetime.now()
    
    def run_check(self):
        """Run a single temperature check cycle"""
        temp = self.read_temperature()
        
        if temp is None:
            logger.error("Failed to read temperature")
            return
        
        logger.info(f"Current temperature: {temp}°C")
        
        # Check thresholds
        severity, message = self.check_thresholds(temp)
        
        if severity != 'normal':
            self.send_alert(severity, temp, message)
        else:
            logger.info(message)
        
        # Check rate of change
        rate_alert = self.check_rate_of_change(temp)
        if rate_alert:
            severity, message = rate_alert
            self.send_alert(severity, temp, message)
        
        # Update state
        self.last_temp = temp
        self.last_temp_time = datetime.now()
        self._save_state()
    
    def run_continuous(self, interval: int = 300):
        """Run continuous monitoring loop
        
        Args:
            interval: Check interval in seconds (default: 5 minutes)
        """
        logger.info(f"Starting continuous monitoring (interval: {interval}s)")
        
        try:
            while True:
                self.run_check()
                time.sleep(interval)
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Monitoring error: {e}")
            raise


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Temperature Alert Skill')
    parser.add_argument('--config', default='config.yaml', help='Configuration file path')
    parser.add_argument('--check', action='store_true', help='Run single check and exit')
    parser.add_argument('--interval', type=int, default=300, help='Check interval in seconds')
    
    args = parser.parse_args()
    
    try:
        alert_system = TemperatureAlert(args.config)
        
        if args.check:
            alert_system.run_check()
        else:
            alert_system.run_continuous(args.interval)
    
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
