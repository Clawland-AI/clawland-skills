#!/usr/bin/env python3
"""Validate the aquaculture monitoring skill package."""

from __future__ import annotations

import json
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - optional dependency
    yaml = None


ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = ROOT / "skill.yaml"
SAMPLE_PATH = ROOT / "examples" / "sample-reading.json"


def fail(message: str) -> None:
    raise SystemExit(f"aquaculture skill validation failed: {message}")


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def main() -> None:
    skill_text = SKILL_PATH.read_text(encoding="utf-8")

    if yaml is None:
        validate_by_text(skill_text)
    else:
        with SKILL_PATH.open("r", encoding="utf-8") as handle:
            validate_by_yaml(yaml.safe_load(handle))

    with SAMPLE_PATH.open("r", encoding="utf-8") as handle:
        sample = json.load(handle)

    for field in ("pond_id", "timestamp", "dissolved_oxygen_mg_l", "ph", "water_temperature_c"):
        require(field in sample, f"sample reading missing required field: {field}")

    print("aquaculture skill validation ok")


def validate_by_yaml(skill: object) -> None:
    require(isinstance(skill, dict), "skill.yaml must parse to a mapping")
    require(skill.get("name") == "aquaculture-monitoring", "skill name must be aquaculture-monitoring")
    require(skill.get("agent") == "picclaw", "agent must be picclaw")

    for section in skill.get("validation", {}).get("required_sections", []):
        require(section in skill, f"missing required section: {section}")

    thresholds = skill.get("thresholds", {})
    for metric in ("dissolved_oxygen", "ph", "water_temperature"):
        require(metric in thresholds, f"missing threshold group: {metric}")
        require("warning_low" in thresholds[metric], f"{metric} missing warning_low")
        require("critical_low" in thresholds[metric], f"{metric} missing critical_low")
        require("warning_high" in thresholds[metric], f"{metric} missing warning_high")
        require("critical_high" in thresholds[metric], f"{metric} missing critical_high")

    aerator_modes = skill.get("aerator_control", {}).get("modes", {})
    for mode in ("normal", "boost", "emergency"):
        require(mode in aerator_modes, f"missing aerator mode: {mode}")

    daily_report = skill.get("daily_report", {})
    require(daily_report.get("enabled") is True, "daily report must be enabled")
    report_template = ROOT / daily_report.get("template", "")
    require(report_template.exists(), f"daily report template missing: {report_template}")

    memory_learning = skill.get("memory_learning", {})
    require(memory_learning.get("enabled") is True, "Memory learning must be enabled")
    require(len(memory_learning.get("learned_patterns", [])) >= 5, "expected at least five learned patterns")

def validate_by_text(skill_text: str) -> None:
    required_tokens = [
        "name: aquaculture-monitoring",
        "agent: picclaw",
        "thresholds:",
        "dissolved_oxygen:",
        "ph:",
        "water_temperature:",
        "aerator_control:",
        "normal:",
        "boost:",
        "emergency:",
        "daily_report:",
        "memory_learning:",
        "learned_patterns:",
        "actions:",
        "templates/daily-report.md",
    ]
    for token in required_tokens:
        require(token in skill_text, f"missing required token: {token}")

    require((ROOT / "templates" / "daily-report.md").exists(), "daily report template missing")


if __name__ == "__main__":
    main()
