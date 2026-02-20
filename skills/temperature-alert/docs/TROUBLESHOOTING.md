# Temperature Alert Skill - Troubleshooting Guide

Common issues and solutions for the Temperature Alert skill.

## Sensor Issues

### Problem: Sensor Not Detected

**Symptoms:**
- No devices in `/sys/bus/w1/devices/`
- Error: "Temperature sensor not found"
- Skill shows "sensor_status: offline"

**Solutions:**

1. **Check 1-Wire Interface** (DS18B20):
   ```bash
   # Enable 1-Wire if not enabled
   sudo raspi-config
   # Interface Options → 1-Wire → Enable
   sudo reboot
   
   # Verify interface is loaded
   lsmod | grep w1
   # Should show: w1_gpio, w1_therm, wire
   ```

2. **Verify Wiring**:
   - Check power connections (3.3V and Ground)
   - Verify data wire to GPIO4 (pin 7)
   - Ensure 4.7kΩ pull-up resistor between data and VDD
   - Try different jumper wires

3. **Test with Multimeter**:
   - VDD to GND should read ~3.3V
   - Data line should read ~3.3V when pulled up
   - Continuity test all connections

4. **Try Different GPIO Pin**:
   ```bash
   # Edit /boot/config.txt
   sudo nano /boot/config.txt
   
   # Change or add:
   dtoverlay=w1-gpio,gpiopin=18  # Use GPIO18 instead of GPIO4
   
   sudo reboot
   ```

### Problem: Intermittent Sensor Readings

**Symptoms:**
- Sometimes works, sometimes fails
- Inconsistent temperature readings
- "CRC check failed" errors

**Solutions:**

1. **Check Power Supply**:
   - Ensure stable 3.3V supply
   - Try external power supply if using many devices
   - Check for loose connections

2. **Cable Length**:
   - Keep sensor cables under 10 meters for reliable operation
   - Use shielded cable for long runs
   - Add stronger pull-up resistor (2.2kΩ) for long cables

3. **Electrical Interference**:
   - Route sensor cables away from power lines
   - Add ferrite beads to reduce interference
   - Use twisted pair cables

### Problem: Wrong Temperature Readings

**Symptoms:**
- Temperature readings obviously incorrect
- Constant high/low values
- Values don't change with environment

**Solutions:**

1. **Verify Sensor Calibration**:
   ```bash
   # Compare with known thermometer
   cat /sys/bus/w1/devices/28-*/w1_slave
   
   # Check multiple sensors if available
   for device in /sys/bus/w1/devices/28-*; do
     echo "Device: $device"
     cat $device/w1_slave
   done
   ```

2. **Sensor Placement**:
   - Avoid direct sunlight
   - Keep away from heat sources (CPU, power supplies)
   - Allow air circulation around sensor
   - Wait 5 minutes after powering on for thermal equilibrium

3. **Add Calibration Offset**:
   ```yaml
   config:
     sensor_id: "temp_01"
     calibration_offset: -2.5  # Adjust by -2.5°C
   ```

## Notification Issues

### Problem: Email Notifications Not Sending

**Symptoms:**
- No alert emails received
- SMTP connection errors in logs
- Authentication failures

**Solutions:**

1. **Gmail App Passwords**:
   ```yaml
   notifications:
     email:
       enabled: true
       smtp_server: "smtp.gmail.com"
       smtp_port: 587
       username: "your-email@gmail.com"
       password: "abcd-efgh-ijkl-mnop"  # 16-char app password, not account password
   ```
   
   Generate app password:
   - Google Account → Security → 2-Step Verification → App passwords

2. **Test SMTP Connection**:
   ```bash
   # Test SMTP manually
   telnet smtp.gmail.com 587
   # Should connect and show greeting
   
   # Test with Python
   python3 -c "
   import smtplib
   server = smtplib.SMTP('smtp.gmail.com', 587)
   server.starttls()
   server.login('user@gmail.com', 'app-password')
   print('SMTP connection successful')
   server.quit()
   "
   ```

3. **Firewall Issues**:
   ```bash
   # Check if port 587 is blocked
   sudo ufw status
   telnet smtp.gmail.com 587
   
   # Allow outbound SMTP if needed
   sudo ufw allow out 587
   ```

4. **Alternative SMTP Providers**:
   ```yaml
   # SendGrid
   notifications:
     email:
       smtp_server: "smtp.sendgrid.net"
       smtp_port: 587
       username: "apikey"
       password: "YOUR_SENDGRID_API_KEY"
   
   # Mailgun  
   notifications:
     email:
       smtp_server: "smtp.mailgun.org"
       smtp_port: 587
       username: "postmaster@your-domain.mailgun.org"
       password: "YOUR_MAILGUN_PASSWORD"
   ```

### Problem: Telegram Notifications Failing

**Symptoms:**
- Telegram messages not received
- "Bot token invalid" errors
- "Chat not found" errors

**Solutions:**

1. **Verify Bot Token**:
   ```bash
   # Test bot token
   curl -X GET "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getMe"
   # Should return bot information
   ```

2. **Get Correct Chat ID**:
   ```bash
   # Start conversation with bot first, then:
   curl -X GET "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates"
   # Find "chat":{"id": NUMBER} in response
   ```

3. **Bot Permissions**:
   - Ensure bot can send messages to chat
   - For groups: add bot as member with message permissions
   - For channels: add bot as admin with posting permissions

### Problem: Discord Webhook Not Working

**Symptoms:**
- No messages in Discord channel
- "Webhook URL invalid" errors
- HTTP 404 errors

**Solutions:**

1. **Verify Webhook URL**:
   ```bash
   # Test webhook directly
   curl -H "Content-Type: application/json" \
        -X POST \
        -d '{"content":"Test message"}' \
        "YOUR_WEBHOOK_URL"
   ```

2. **Webhook Permissions**:
   - Ensure bot has "Send Messages" permission in channel
   - Check webhook hasn't been deleted from Discord
   - Recreate webhook if necessary

3. **Rate Limiting**:
   - Discord limits webhooks to 30 requests per minute
   - Increase cooldown if sending too many alerts

## Alert Issues

### Problem: Too Many Alerts (Spam)

**Symptoms:**
- Constant stream of notifications
- Alert fatigue
- Repeated alerts for same condition

**Solutions:**

1. **Adjust Cooldown Period**:
   ```yaml
   config:
     cooldown_minutes: 60  # Increase from default 15 minutes
   ```

2. **Fine-tune Thresholds**:
   ```yaml
   config:
     high_threshold: 28.0  # Was 25.0, increase to reduce false alerts
     rate_threshold: 10.0  # Was 5.0, increase to ignore small changes
   ```

3. **Add Hysteresis** (prevent bouncing):
   ```yaml
   config:
     high_threshold: 30.0
     high_threshold_reset: 28.0  # Must drop to 28°C before re-alerting
   ```

### Problem: No Alerts When Expected

**Symptoms:**
- Temperature exceeds thresholds but no alerts sent
- Skill appears inactive
- No log entries

**Solutions:**

1. **Check Skill Status**:
   ```bash
   picclaw skill status temperature-alert
   picclaw skill logs temperature-alert --tail 50
   ```

2. **Verify Skill Is Enabled**:
   ```bash
   picclaw skill list --enabled
   picclaw skill enable temperature-alert
   ```

3. **Test Alert System**:
   ```bash
   # Force test alert
   picclaw skill run temperature-alert --simulate high_temp=50.0
   picclaw skill run temperature-alert --action test_notifications
   ```

4. **Check Threshold Configuration**:
   ```bash
   picclaw skill config temperature-alert --show
   ```

### Problem: False Alerts

**Symptoms:**
- Alerts for normal temperature conditions
- Sensor readings seem wrong
- Alerts at unexpected times

**Solutions:**

1. **Sensor Placement Review**:
   - Move away from heat sources (electronics, sunlight)
   - Ensure good ventilation
   - Use sensor enclosure for outdoor monitoring

2. **Environmental Factors**:
   - Account for daily temperature variations
   - Consider seasonal changes
   - Review historical data for patterns

3. **Adjust Sensitivity**:
   ```yaml
   config:
     rate_threshold: 8.0     # Less sensitive to changes
     cooldown_minutes: 30    # Longer between alerts
   ```

## Performance Issues

### Problem: High CPU Usage

**Symptoms:**
- System slowdown
- High temperature readings from CPU thermal sensor
- Skill consuming excessive resources

**Solutions:**

1. **Increase Monitoring Interval**:
   ```yaml
   triggers:
     - type: cron
       schedule: "*/5 * * * *"  # Every 5 minutes instead of 2
   ```

2. **Optimize Notifications**:
   ```yaml
   config:
     cooldown_minutes: 30      # Reduce notification frequency
     max_alerts_per_hour: 4    # Limit total alerts
   ```

3. **Check for Memory Leaks**:
   ```bash
   # Monitor memory usage
   picclaw skill stats temperature-alert
   ps aux | grep temperature-alert
   ```

### Problem: Network Connectivity Issues

**Symptoms:**
- Webhook notifications failing
- Internet-dependent features not working
- Intermittent connection errors

**Solutions:**

1. **Add Network Retry Logic**:
   ```yaml
   notifications:
     webhook:
       timeout_seconds: 30
       retry_attempts: 3
       retry_delay_seconds: 10
   ```

2. **Local Fallbacks**:
   ```yaml
   notifications:
     local_log:
       enabled: true
       log_file: "/var/log/temperature-alerts.log"
   ```

3. **Network Diagnostics**:
   ```bash
   # Test connectivity
   ping -c 4 8.8.8.8
   curl -I https://api.telegram.org
   nslookup smtp.gmail.com
   ```

## Configuration Issues

### Problem: Skill Won't Start

**Symptoms:**
- "Failed to load skill" errors
- Configuration validation errors
- Skill status shows "error"

**Solutions:**

1. **Validate YAML Configuration**:
   ```bash
   # Check YAML syntax
   picclaw skill validate temperature-alert
   
   # Or manually with Python
   python3 -c "import yaml; yaml.safe_load(open('skill.yaml'))"
   ```

2. **Check Required Fields**:
   ```yaml
   # Ensure minimum required configuration
   config:
     sensor_id: "temp_01"      # Required
     
   notifications:
     email:
       enabled: true
       to_email: "admin@example.com"  # Required when email enabled
   ```

3. **Permission Issues**:
   ```bash
   # Check file permissions
   ls -la ~/.picclaw/skills/temperature-alert/
   
   # Fix if needed
   chmod 644 ~/.picclaw/skills/temperature-alert/skill.yaml
   ```

### Problem: Environment Variables Not Working

**Symptoms:**
- Values like "${TELEGRAM_BOT_TOKEN}" appear literally
- Authentication failures with placeholder values

**Solutions:**

1. **Set Environment Variables**:
   ```bash
   # Set in shell
   export TELEGRAM_BOT_TOKEN="1234567890:ABC..."
   
   # Or in systemd service file
   sudo systemctl edit picclaw
   # Add:
   [Service]
   Environment="TELEGRAM_BOT_TOKEN=1234567890:ABC..."
   ```

2. **Use Configuration Files**:
   ```yaml
   # Instead of environment variables, use direct values
   notifications:
     telegram:
       bot_token: "1234567890:ABC..."  # Direct value
   ```

3. **Check Variable Expansion**:
   ```bash
   # Verify variables are set
   env | grep TELEGRAM
   echo $TELEGRAM_BOT_TOKEN
   ```

## Debugging Tools

### Enable Debug Logging

```yaml
# In skill.yaml
debug:
  enabled: true
  log_level: "DEBUG"
  log_file: "/var/log/temperature-alert-debug.log"
```

### Manual Testing Commands

```bash
# Test sensor reading
picclaw skill run temperature-alert --action read_sensor --debug

# Test notifications
picclaw skill run temperature-alert --action test_notifications --debug

# Simulate conditions  
picclaw skill run temperature-alert --simulate temp=40.0 --debug

# View configuration
picclaw skill config temperature-alert --show

# Check skill health
picclaw skill health temperature-alert
```

### Log Analysis

```bash
# View recent logs
picclaw skill logs temperature-alert --tail 100

# Follow logs in real-time
picclaw skill logs temperature-alert --follow

# Search for errors
picclaw skill logs temperature-alert | grep -i error

# Check system logs
journalctl -u picclaw | grep temperature-alert
```

### Network Diagnostics

```bash
# Test webhook connectivity
curl -X POST -H "Content-Type: application/json" \
     -d '{"test": "message"}' \
     "YOUR_WEBHOOK_URL"

# Test SMTP
telnet smtp.gmail.com 587

# Test DNS resolution
nslookup api.telegram.org
```

## Getting Help

If these troubleshooting steps don't resolve your issue:

1. **Check GitHub Issues**: [clawland-skills/issues](https://github.com/Clawland-AI/clawland-skills/issues)

2. **Gather Debug Information**:
   ```bash
   # Collect system info for support
   picclaw system info > system-info.txt
   picclaw skill logs temperature-alert --tail 200 > skill-logs.txt
   picclaw skill config temperature-alert --show > skill-config.txt
   ```

3. **Community Support**:
   - [Clawland Discord](https://discord.gg/clawland)
   - [Community Forum](https://community.clawland.ai)

4. **Create Issue Report** with:
   - System information
   - Skill configuration (remove secrets)
   - Log files
   - Steps to reproduce
   - Expected vs actual behavior

## Preventive Maintenance

### Regular Checks

```bash
# Weekly health check
picclaw skill health temperature-alert

# Monthly log review  
picclaw skill logs temperature-alert --since "30 days ago" | grep -i error

# Quarterly sensor calibration
picclaw skill run temperature-alert --calibrate
```

### Backup Configuration

```bash
# Backup skill configuration
cp ~/.picclaw/skills/temperature-alert/skill.yaml \
   ~/backups/temperature-alert-config-$(date +%Y%m%d).yaml
```

### Update Notifications

```bash
# Check for skill updates
picclaw skill update --check temperature-alert

# Update to latest version
picclaw skill update temperature-alert
```