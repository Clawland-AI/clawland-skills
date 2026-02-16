import sys
import json

def notify(message, channels):
    print(f"Sending notification to {channels}: {message}")
    # In a real Claw agent, this would call the 'message' tool or internal APIs.
    # For this template, we log the action.

def handle(event, context):
    config = context.get('config', {})
    threshold_high = config.get('threshold_high', 80.0)
    threshold_low = config.get('threshold_low', 10.0)
    channels = config.get('channels', ['telegram'])

    # Mock sensor data extraction
    current_temp = event.get('temperature', 25.0)

    if current_temp > threshold_high:
        notify(f"⚠️ HIGH TEMP ALERT: {current_temp}°C exceeds {threshold_high}°C", channels)
    elif current_temp < threshold_low:
        notify(f"⚠️ LOW TEMP ALERT: {current_temp}°C is below {threshold_low}°C", channels)
    else:
        print(f"Temperature OK: {current_temp}°C")

if __name__ == "__main__":
    # Test execution
    test_event = {"temperature": 85.0}
    test_context = {"config": {"threshold_high": 80.0, "channels": ["discord"]}}
    handle(test_event, test_context)
