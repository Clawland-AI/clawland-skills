#!/usr/bin/env python3
"""
Temperature Alert Skill
Monitor temperature sensors and send alerts when thresholds are exceeded.
"""

import os
import json
import time
import logging
import threading
import argparse
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime
import requests
try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('temperature_alert')


@dataclass
class SensorConfig:
    """Configuration for temperature sensor."""
    sensor_type: str
    file_path: Optional[str] = None
    url: Optional[str] = None
    headers: Optional[Dict[str, str]] = None
    broker: Optional[str] = None
    topic: Optional[str] = None
    pin: Optional[int] = None


@dataclass
class AlertConfig:
    """Configuration for alerts."""
    threshold: float
    hysteresis: float = 1.0
    check_interval: int = 60
    rate_of_change_threshold: float = 5.0
    notification_type: str = "webhook"
    notification_config: Dict[str, Any] = field(default_factory=dict)


class TemperatureSensor(ABC):
    """Abstract base class for temperature sensors."""
    
    @abstractmethod
    def read_temperature(self) -> Optional[float]:
        """Read current temperature in Celsius."""
        pass


class FileSensor(TemperatureSensor):
    """Read temperature from a file (1-wire, etc.)."""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
    
    def read_temperature(self) -> Optional[float]:
        try:
            with open(self.file_path, 'r') as f:
                content = f.read().strip()
                # Handle different file formats
                if '\n' in content:
                    # Multiple lines, find temperature line
                    for line in content.split('\n'):
                        if 't=' in line:
                            # Dallas 1-wire format: t=23500 means 23.500°C
                            temp_str = line.split('t=')[1]
                            return float(temp_str) / 1000.0
                return float(content)
        except (FileNotFoundError, ValueError, IOError) as e:
            logger.error(f"Error reading temperature file: {e}")
            return None


class HTTPSensor(TemperatureSensor):
    """Read temperature from HTTP endpoint."""
    
    def __init__(self, url: str, headers: Optional[Dict[str, str]] = None):
        self.url = url
        self.headers = headers or {}
    
    def read_temperature(self) -> Optional[float]:
        try:
            response = requests.get(self.url, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Handle common JSON temperature field names
            for key in ['temperature', 'temp', 'temp_c', 'celsius', 'value']:
                if key in data:
                    return float(data[key])
                    
            logger.error(f"Could not find temperature in response: {data}")
            return None
        except Exception as e:
            logger.error(f"Error reading temperature from HTTP: {e}")
            return None


class MQTTSensor(TemperatureSensor):
    """Read temperature from MQTT broker."""
    
    def __init__(self, broker: str, topic: str):
        if not MQTT_AVAILABLE:
            raise ImportError("paho-mqtt not installed")
        
        self.broker = broker
        self.topic = topic
        self._temperature = None
        self._client = mqtt.Client()
        self._client.on_message = self._on_message
        self._connected = threading.Event()
        
        self._client.on_connect = lambda client, userdata, flags, rc: (
            self._connected.set() if rc == 0 else None
        )
        
        self._client.connect(broker.split(':')[0], int(broker.split(':')[1]) if ':' in broker else 1883, 60)
        self._client.subscribe(topic)
        self._client.loop_start()
        
        if not self._connected.wait(timeout=5):
            logger.warning("MQTT connection timeout")
    
    def _on_message(self, client, userdata, msg):
        try:
            self._temperature = float(msg.payload.decode())
        except ValueError:
            logger.error(f"Invalid temperature payload: {msg.payload}")
    
    def read_temperature(self) -> Optional[float]:
        return self._temperature


class GPIOSensor(TemperatureSensor):
    """Read temperature from GPIO-connected sensor (DS18B20 via GPIO)."""
    
    def __init__(self, pin: int):
        self.pin = pin
        # This would require GPIO library - placeholder
        logger.warning("GPIO sensor requires additional setup")
    
    def read_temperature(self) -> Optional[float]:
        # Placeholder - actual implementation depends on hardware
        logger.error("GPIO sensor not implemented")
        return None


class Notifier(ABC):
    """Abstract base class for notifications."""
    
    @abstractmethod
    def send(self, message: str, temperature: float, alert: bool):
        """Send notification."""
        pass


class TelegramNotifier(Notifier):
    """Send alerts via Telegram."""
    
    def __init__(self, config: Dict[str, Any]):
        self.bot_token = config.get('bot_token')
        self.chat_id = config.get('chat_id')
    
    def send(self, message: str, temperature: float, alert: bool):
        if not self.bot_token or not self.chat_id:
            logger.error("Telegram bot_token and chat_id required")
            return
        
        emoji = "🔴" if alert else "🟢"
        text = f"{emoji} *Temperature Alert*\n\n{message}\n\nCurrent: *{temperature}°C*"
        
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        data = {
            'chat_id': self.chat_id,
            'text': text,
            'parse_mode': 'Markdown'
        }
        
        try:
            requests.post(url, json=data)
        except Exception as e:
            logger.error(f"Error sending Telegram notification: {e}")


class DiscordNotifier(Notifier):
    """Send alerts via Discord webhook."""
    
    def __init__(self, config: Dict[str, Any]):
        self.webhook_url = config.get('webhook_url')
    
    def send(self, message: str, temperature: float, alert: bool):
        if not self.webhook_url:
            logger.error("Discord webhook_url required")
            return
        
        color = 16711680 if alert else 65280  # Red or Green
        
        payload = {
            'embeds': [{
                'title': '🔔 Temperature Alert' if alert else '✅ Temperature Normal',
                'description': message,
                'color': color,
                'fields': [
                    {'name': 'Current Temperature', 'value': f'{temperature}°C', 'inline': True}
                ],
                'timestamp': datetime.utcnow().isoformat()
            }]
        }
        
        try:
            requests.post(self.webhook_url, json=payload)
        except Exception as e:
            logger.error(f"Error sending Discord notification: {e}")


class WebhookNotifier(Notifier):
    """Send alerts to generic webhook."""
    
    def __init__(self, config: Dict[str, Any]):
        self.url = config.get('url')
        self.method = config.get('method', 'POST')
    
    def send(self, message: str, temperature: float, alert: bool):
        if not self.url:
            logger.error("Webhook URL required")
            return
        
        payload = {
            'alert': alert,
            'temperature': temperature,
            'message': message,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        try:
            if self.method.upper() == 'POST':
                requests.post(self.url, json=payload)
            else:
                requests.get(self.url, params=payload)
        except Exception as e:
            logger.error(f"Error sending webhook notification: {e}")


class TemperatureAlert:
    """Main temperature monitoring and alert class."""
    
    def __init__(self, sensor_config: SensorConfig, alert_config: AlertConfig):
        self.sensor_config = sensor_config
        self.alert_config = alert_config
        
        # Create sensor
        self.sensor = self._create_sensor(sensor_config)
        
        # Create notifier
        self.notifier = self._create_notifier(alert_config)
        
        # State
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._current_temp: Optional[float] = None
        self._alert_active = False
        self._last_temp: Optional[float] = None
        self._last_check_time: Optional[float] = None
        self._history: List[float] = []
    
    def _create_sensor(self, config: SensorConfig) -> TemperatureSensor:
        """Create sensor based on type."""
        if config.sensor_type == 'file':
            return FileSensor(config.file_path)
        elif config.sensor_type == 'http':
            return HTTPSensor(config.url, config.headers)
        elif config.sensor_type == 'mqtt':
            return MQTTSensor(config.broker, config.topic)
        elif config.sensor_type == 'gpio':
            return GPIOSensor(config.pin)
        else:
            raise ValueError(f"Unknown sensor type: {config.sensor_type}")
    
    def _create_notifier(self, config: AlertConfig) -> Notifier:
        """Create notifier based on type."""
        if config.notification_type == 'telegram':
            return TelegramNotifier(config.notification_config)
        elif config.notification_type == 'discord':
            return DiscordNotifier(config.notification_config)
        elif config.notification_type == 'webhook':
            return WebhookNotifier(config.notification_config)
        else:
            raise ValueError(f"Unknown notification type: {config.notification_type}")
    
    def _check_alert(self, temperature: float) -> bool:
        """Check if temperature triggers alert."""
        threshold = self.alert_config.threshold
        
        # Rate of change check
        if self._last_temp and self._last_check_time:
            time_diff = time.time() - self._last_check_time
            if time_diff > 0:
                rate_of_change = abs(temperature - self._last_temp) / (time_diff / 60)
                if rate_of_change > self.alert_config.rate_of_change_threshold:
                    self.notifier.send(
                        f"Temperature changing too fast: {rate_of_change:.1f}°C/min",
                        temperature,
                        True
                    )
        
        # Threshold check with hysteresis
        if temperature >= threshold and not self._alert_active:
            self._alert_active = True
            return True
        elif temperature < (threshold - self.alert_config.hysteresis) and self._alert_active:
            self._alert_active = False
            return False
        
        return self._alert_active
    
    def _monitor_loop(self):
        """Main monitoring loop."""
        while self._running:
            try:
                temperature = self.sensor.read_temperature()
                
                if temperature is not None:
                    self._current_temp = temperature
                    self._history.append(temperature)
                    if len(self._history) > 100:
                        self._history.pop(0)
                    
                    alert = self._check_alert(temperature)
                    
                    if alert:
                        self.notifier.send(
                            f"Temperature exceeded threshold: {self.alert_config.threshold}°C",
                            temperature,
                            True
                        )
                    
                    logger.info(f"Temperature: {temperature}°C, Alert: {alert}")
                
                self._last_temp = temperature
                self._last_check_time = time.time()
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
            
            time.sleep(self.alert_config.check_interval)
    
    def start(self, duration: int = 0):
        """Start temperature monitoring."""
        if self._running:
            logger.warning("Already running")
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop)
        self._thread.daemon = True
        self._thread.start()
        
        logger.info(f"Temperature monitoring started (duration: {duration}s, 0=forever)")
        
        if duration > 0:
            time.sleep(duration)
            self.stop()
    
    def stop(self):
        """Stop temperature monitoring."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("Temperature monitoring stopped")
    
    def status(self) -> Dict[str, Any]:
        """Get current status."""
        return {
            'running': self._running,
            'current_temp': self._current_temp,
            'alert_active': self._alert_active,
            'last_check': datetime.fromtimestamp(self._last_check_time).isoformat() if self._last_check_time else None,
            'history_count': len(self._history)
        }


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description='Temperature Alert Monitor')
    parser.add_argument('--config', type=str, help='Path to config JSON file')
    parser.add_argument('--sensor-type', type=str, choices=['file', 'http', 'mqtt', 'gpio'])
    parser.add_argument('--threshold', type=float, help='Temperature threshold (°C)')
    parser.add_argument('--interval', type=int, default=60, help='Check interval (seconds)')
    parser.add_argument('--duration', type=int, default=0, help='Duration to run (0=forever)')
    
    args = parser.parse_args()
    
    if args.config:
        # Load from config file
        with open(args.config, 'r') as f:
            config = json.load(f)
        
        sensor_config = SensorConfig(
            sensor_type=config['sensor_type'],
            file_path=config.get('file_path'),
            url=config.get('url'),
            headers=config.get('headers'),
            broker=config.get('broker'),
            topic=config.get('topic'),
            pin=config.get('pin')
        )
        
        alert_config = AlertConfig(
            threshold=config['threshold'],
            hysteresis=config.get('hysteresis', 1.0),
            check_interval=config.get('check_interval', 60),
            rate_of_change_threshold=config.get('rate_of_change_threshold', 5.0),
            notification_type=config['notification']['type'],
            notification_config=config['notification'].get('config', {})
        )
    else:
        # Use command line arguments
        sensor_config = SensorConfig(sensor_type=args.sensor_type)
        alert_config = AlertConfig(
            threshold=args.threshold,
            check_interval=args.interval
        )
    
    monitor = TemperatureAlert(sensor_config, alert_config)
    monitor.start(duration=args.duration)


if __name__ == '__main__':
    main()
