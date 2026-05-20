#!/usr/bin/env python3
"""
Temperature Alert Skill for Clawland Agents
Monitors temperature sensors and sends alerts when thresholds are exceeded.
"""

import json
import sys
import time
from datetime import datetime
from typing import Optional

try:
    import requests
except ImportError:
    requests = None


class TemperatureAlert:
    def __init__(self, config_path: str = "skill.yaml"):
        self.config = self._load_config(config_path)
        self.thresholds = self.config.get("thresholds", {"high": 30.0, "low": 10.0})
        self.unit = self.config.get("unit", "celsius")
        self.cooldown = self.config.get("cooldown", 300)
        self.last_alert_time = 0

    def _load_config(self, path: str) -> dict:
        """Load configuration from YAML file."""
        try:
            import yaml
            with open(path, "r") as f:
                return yaml.safe_load(f).get("config", {})
        except ImportError:
            # Fallback to default config if pyyaml not installed
            return {
                "thresholds": {"high": 30.0, "low": 10.0},
                "unit": "celsius",
                "cooldown": 300,
            }

    def check_temperature(self, temperature: float) -> Optional[str]:
        """Check if temperature exceeds thresholds."""
        if temperature >= self.thresholds["high"]:
            return f"🔴 HIGH TEMPERATURE ALERT: {temperature}°{self.unit[0].upper()}"
        elif temperature <= self.thresholds["low"]:
            return f"🔵 LOW TEMPERATURE ALERT: {temperature}°{self.unit[0].upper()}"
        return None

    def should_alert(self) -> bool:
        """Check if cooldown period has passed."""
        current_time = time.time()
        if current_time - self.last_alert_time >= self.cooldown:
            self.last_alert_time = current_time
            return True
        return False

    def send_notification(self, message: str, channels: list = None):
        """Send notification to configured channels."""
        if channels is None:
            channels = ["telegram", "discord", "webhook"]

        for channel in channels:
            try:
                if channel == "telegram":
                    self._send_telegram(message)
                elif channel == "discord":
                    self._send_discord(message)
                elif channel == "webhook":
                    self._send_webhook(message)
            except Exception as e:
                print(f"Error sending to {channel}: {e}")

    def _send_telegram(self, message: str):
        """Send notification via Telegram."""
        bot_token = self.config.get("telegram_bot_token")
        chat_id = self.config.get("telegram_chat_id")
        if bot_token and chat_id and requests:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            requests.post(url, json={"chat_id": chat_id, "text": message})

    def _send_discord(self, message: str):
        """Send notification via Discord webhook."""
        webhook_url = self.config.get("discord_webhook")
        if webhook_url and requests:
            requests.post(webhook_url, json={"content": message})

    def _send_webhook(self, message: str):
        """Send notification via generic webhook."""
        webhook_url = self.config.get("webhook_url")
        if webhook_url and requests:
            requests.post(webhook_url, json={
                "text": message,
                "timestamp": datetime.now().isoformat(),
            })

    def run(self, temperature: float):
        """Main entry point - check temperature and alert if needed."""
        alert = self.check_temperature(temperature)
        if alert and self.should_alert():
            self.send_notification(alert)
            print(alert)
        else:
            print(f"✅ Temperature normal: {temperature}°{self.unit[0].upper()}")


def main():
    if len(sys.argv) < 2:
        print("Usage: temperature-alert <temperature>")
        print("Example: temperature-alert 35.5")
        sys.exit(1)

    try:
        temperature = float(sys.argv[1])
    except ValueError:
        print("Error: Temperature must be a number")
        sys.exit(1)

    alert = TemperatureAlert()
    alert.run(temperature)


if __name__ == "__main__":
    main()
