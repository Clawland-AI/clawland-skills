import sys
import json

def notify(message, channels):
    print(f"Sending notification to {channels}: {message}")

def handle(event, context):
    # Cursor Bugbot was right! Fix: Read from actions[].input mapped to event/context
    # Aligning with Clawland standard: inputs are merged into the event object
    threshold_high = event.get('threshold_high', 80.0)
    threshold_low = event.get('threshold_low', 10.0)
    channels = event.get('channels', ['telegram'])

    # Current temperature from sensor
    current_temp = event.get('temperature', 25.0)

    if current_temp > threshold_high:
        notify(f"⚠️ HIGH TEMP ALERT: {current_temp}°C exceeds {threshold_high}°C", channels)
    elif current_temp < threshold_low:
        notify(f"⚠️ LOW TEMP ALERT: {current_temp}°C is below {threshold_low}°C", channels)
    else:
        print(f"Temperature OK: {current_temp}°C")

if __name__ == "__main__":
    # Test execution with fixed input mapping
    test_event = {
        "temperature": 85.0,
        "threshold_high": 80.0,
        "channels": ["discord"]
    }
    handle(test_event, {})
