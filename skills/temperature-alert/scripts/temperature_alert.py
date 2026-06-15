#!/usr/bin/env python3
"""Evaluate temperature sensor events and send threshold alerts."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen


DEFAULT_THRESHOLDS = {
    "high_warning_c": 35.0,
    "high_critical_c": 45.0,
    "low_warning_c": 5.0,
    "low_critical_c": 0.0,
    "rate_of_change_c_per_min": 5.0,
}


@dataclass
class SensorEvent:
    sensor_id: str
    temperature_c: float
    timestamp: datetime


def parse_timestamp(value: str | None) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def load_event(path: Path) -> SensorEvent:
    data = json.loads(path.read_text(encoding="utf-8"))
    return SensorEvent(
        sensor_id=str(data["sensor_id"]),
        temperature_c=float(data["temperature_c"]),
        timestamp=parse_timestamp(data.get("timestamp")),
    )


def parse_scalar(value: str) -> Any:
    value = value.strip()
    if not value:
        return ""
    try:
        return float(value)
    except ValueError:
        return value.strip("\"'")


def load_simple_yaml(path: Path) -> dict[str, Any]:
    """Parse the small key/value YAML subset used by config.example.yaml."""
    result: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, result)]
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        key, _, value = line.strip().partition(":")
        while stack and indent <= stack[-1][0]:
            stack.pop()
        current = stack[-1][1]
        if value.strip():
            current[key] = parse_scalar(value)
        else:
            child: dict[str, Any] = {}
            current[key] = child
            stack.append((indent, child))
    return result


def load_config(path: Path | None) -> dict[str, Any]:
    if not path:
        return {"thresholds": DEFAULT_THRESHOLDS, "notifications": {}}
    config = load_simple_yaml(path)
    thresholds = DEFAULT_THRESHOLDS | config.get("thresholds", {})
    return {"thresholds": thresholds, "notifications": config.get("notifications", {})}


def load_previous_state(path: Path, sensor_id: str) -> dict[str, Any] | None:
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get(sensor_id)


def save_state(path: Path, event: SensorEvent) -> None:
    data: dict[str, Any] = {}
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
    data[event.sensor_id] = {
        "temperature_c": event.temperature_c,
        "timestamp": event.timestamp.isoformat(),
    }
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def evaluate(event: SensorEvent, thresholds: dict[str, float], previous: dict[str, Any] | None) -> dict[str, Any]:
    level = "normal"
    reasons: list[str] = []

    if event.temperature_c >= float(thresholds["high_critical_c"]):
        level = "critical"
        reasons.append(f"temperature {event.temperature_c:.1f}C >= high critical {thresholds['high_critical_c']}C")
    elif event.temperature_c >= float(thresholds["high_warning_c"]):
        level = "warning"
        reasons.append(f"temperature {event.temperature_c:.1f}C >= high warning {thresholds['high_warning_c']}C")

    if event.temperature_c <= float(thresholds["low_critical_c"]):
        level = "critical"
        reasons.append(f"temperature {event.temperature_c:.1f}C <= low critical {thresholds['low_critical_c']}C")
    elif event.temperature_c <= float(thresholds["low_warning_c"]) and level != "critical":
        level = "warning"
        reasons.append(f"temperature {event.temperature_c:.1f}C <= low warning {thresholds['low_warning_c']}C")

    if previous:
        previous_time = parse_timestamp(str(previous["timestamp"]))
        previous_temp = float(previous["temperature_c"])
        elapsed_min = max((event.timestamp - previous_time).total_seconds() / 60.0, 0.001)
        change_rate = abs(event.temperature_c - previous_temp) / elapsed_min
        if change_rate >= float(thresholds["rate_of_change_c_per_min"]):
            if level == "normal":
                level = "warning"
            reasons.append(
                "temperature changed "
                f"{change_rate:.1f}C/min >= limit {thresholds['rate_of_change_c_per_min']}C/min"
            )

    message = f"[{level.upper()}] {event.sensor_id}: {event.temperature_c:.1f}C"
    if reasons:
        message += " - " + "; ".join(reasons)
    return {"level": level, "reasons": reasons, "message": message}


def post_json(url: str, payload: dict[str, Any]) -> str:
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=10) as response:
            return f"sent:{response.status}"
    except (URLError, TimeoutError) as exc:
        return f"error:{exc}"


def deliver(message: str, level: str, notifications: dict[str, Any]) -> dict[str, str]:
    delivered = {"stdout": "sent"}
    print(message, file=sys.stderr)

    webhook_url = str(notifications.get("webhook_url") or "")
    if webhook_url:
        delivered["webhook"] = post_json(webhook_url, {"level": level, "message": message})

    discord_url = str(notifications.get("discord_webhook_url") or "")
    if discord_url:
        delivered["discord"] = post_json(discord_url, {"content": message})

    telegram_token = str(notifications.get("telegram_bot_token") or "")
    telegram_chat_id = str(notifications.get("telegram_chat_id") or "")
    if telegram_token and telegram_chat_id:
        telegram_url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
        delivered["telegram"] = post_json(telegram_url, {"chat_id": telegram_chat_id, "text": message})

    return delivered


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate a temperature event and send alerts.")
    parser.add_argument("--event", required=True, type=Path, help="JSON event file.")
    parser.add_argument("--config", type=Path, help="YAML config file.")
    parser.add_argument("--state", default=Path(".temperature-alert-state.json"), type=Path)
    parser.add_argument("--no-save-state", action="store_true", help="Evaluate without updating the state file.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    event = load_event(args.event)
    config = load_config(args.config)
    previous = load_previous_state(args.state, event.sensor_id)
    decision = evaluate(event, config["thresholds"], previous)
    decision["delivered"] = deliver(decision["message"], decision["level"], config["notifications"])
    if not args.no_save_state:
        save_state(args.state, event)
    print(json.dumps(decision, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
