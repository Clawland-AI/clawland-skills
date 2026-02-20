#!/bin/bash
# Temperature Alert Skill Setup Script
# Automated installation and configuration for temperature monitoring

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration variables
SKILL_NAME="temperature-alert"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Temperature Alert Skill Setup${NC}"
echo -e "${BLUE}================================${NC}"
echo

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if running on supported system
check_system() {
    print_step "Checking system compatibility..."
    
    if [[ ! -f /etc/os-release ]]; then
        print_error "Cannot detect operating system"
        exit 1
    fi
    
    . /etc/os-release
    
    case $ID in
        "raspbian"|"debian"|"ubuntu")
            print_status "Detected $PRETTY_NAME - Compatible"
            ;;
        *)
            print_warning "Detected $PRETTY_NAME - May not be fully supported"
            ;;
    esac
}

# Check for required tools
check_dependencies() {
    print_step "Checking dependencies..."
    
    local missing_deps=()
    
    # Check for required tools (gpio is optional — only needed for GPIO-wired sensors)
    for cmd in python3 pip3; do
        if ! command -v $cmd &> /dev/null; then
            missing_deps+=($cmd)
        fi
    done
    if ! command -v gpio &> /dev/null; then
        print_warning "gpio utility not found — OK if using USB/I2C sensors or virtual mode"
    fi
    
    # Check for picclaw/nanoclaw/microclaw/moltclaw
    local claw_found=false
    for claw in picclaw nanoclaw microclaw moltclaw; do
        if command -v $claw &> /dev/null; then
            print_status "Found $claw"
            CLAW_COMMAND=$claw
            # moltclaw uses 'fleet skill' sub-command; others use 'skill' directly
            if [[ "$claw" == "moltclaw" ]]; then
                CLAW_SKILL_CMD="moltclaw fleet"
            else
                CLAW_SKILL_CMD="$claw"
            fi
            claw_found=true
            break
        fi
    done
    
    if [[ $claw_found == false ]]; then
        missing_deps+=("claw-agent")
    fi
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        print_error "Missing dependencies: ${missing_deps[*]}"
        print_status "Please install missing dependencies and run setup again"
        exit 1
    fi
    
    print_status "All dependencies found"
}

# Enable required interfaces
enable_interfaces() {
    print_step "Enabling required interfaces..."
    
    # Check if 1-Wire is enabled
    if ! grep -q "dtoverlay=w1-gpio" /boot/config.txt 2>/dev/null; then
        print_status "Enabling 1-Wire interface..."
        
        if [[ $EUID -ne 0 ]]; then
            print_warning "Root privileges needed to enable 1-Wire"
            sudo bash -c 'echo "dtoverlay=w1-gpio" >> /boot/config.txt'
        else
            echo "dtoverlay=w1-gpio" >> /boot/config.txt
        fi
        
        print_warning "Reboot required after setup to activate 1-Wire"
        REBOOT_REQUIRED=true
    else
        print_status "1-Wire interface already enabled"
    fi
    
    # Load 1-Wire modules
    if ! lsmod | grep -q w1_gpio; then
        print_status "Loading 1-Wire modules..."
        sudo modprobe w1-gpio
        sudo modprobe w1-therm
    fi
}

# Install Python dependencies
install_python_deps() {
    print_step "Installing Python dependencies..."
    
    local pip_packages=(
        "requests>=2.28.0"
        "PyYAML>=6.0"
        "schedule>=1.2.0"
    )
    
    for package in "${pip_packages[@]}"; do
        print_status "Installing $package..."
        pip3 install --user "$package" 2>/dev/null || {
            print_warning "Failed to install $package - may already be installed"
        }
    done
}

# Detect temperature sensors
detect_sensors() {
    print_step "Detecting temperature sensors..."
    
    # Check for 1-Wire sensors
    local w1_devices="/sys/bus/w1/devices"
    if [[ -d $w1_devices ]]; then
        # Use || true so set -e doesn't exit when no 28- devices are present
        local sensors=($(ls "$w1_devices" 2>/dev/null | grep "^28-" || true))
        
        if [[ ${#sensors[@]} -gt 0 ]]; then
            print_status "Found ${#sensors[@]} DS18B20 sensor(s):"
            for sensor in "${sensors[@]}"; do
                echo "  - $sensor"
                # Test reading
                if cat "$w1_devices/$sensor/w1_slave" 2>/dev/null | grep -q "YES"; then
                    # cut only accepts single-char delimiter — use '=' not 't='
                    local temp=$(cat "$w1_devices/$sensor/w1_slave" | grep "t=" | cut -d= -f2)
                    local temp_c=$(echo "scale=3; $temp/1000" | bc 2>/dev/null || echo "N/A")
                    echo "    Temperature: ${temp_c}°C"
                    DETECTED_SENSORS+=("$sensor")
                else
                    print_warning "    Sensor $sensor not responding"
                fi
            done
        else
            print_warning "No DS18B20 sensors detected on 1-Wire bus"
        fi
    else
        print_warning "1-Wire interface not available - check wiring and reboot"
    fi
    
    # Check for I2C sensors (basic detection)
    if command -v i2cdetect &> /dev/null; then
        print_status "Scanning I2C bus for sensors..."
        local i2c_devices=$(i2cdetect -y 1 2>/dev/null | grep -v "^     " | grep -v "^00:" | grep -oE '[0-9a-f]{2}' | wc -l)
        if [[ $i2c_devices -gt 0 ]]; then
            print_status "Found $i2c_devices I2C device(s) - may include sensors"
        fi
    fi
}

# Interactive configuration
configure_skill() {
    print_step "Configuring temperature alert skill..."
    
    local config_file="$HOME/.${CLAW_COMMAND}/skills/${SKILL_NAME}/config.yaml"
    local config_dir="$(dirname "$config_file")"
    
    # Create config directory
    mkdir -p "$config_dir"
    
    # Get user preferences
    echo
    echo "Configuration Questions:"
    echo
    
    # Sensor configuration
    if [[ ${#DETECTED_SENSORS[@]} -gt 0 ]]; then
        echo "Detected sensors:"
        for i in "${!DETECTED_SENSORS[@]}"; do
            echo "  $((i+1)). ${DETECTED_SENSORS[$i]}"
        done
        echo
        read -p "Select sensor number (1-${#DETECTED_SENSORS[@]}) [1]: " sensor_choice
        sensor_choice=${sensor_choice:-1}
        
        if [[ $sensor_choice -ge 1 && $sensor_choice -le ${#DETECTED_SENSORS[@]} ]]; then
            SELECTED_SENSOR="${DETECTED_SENSORS[$((sensor_choice-1))]}"
        else
            SELECTED_SENSOR="${DETECTED_SENSORS[0]}"
        fi
    else
        read -p "Enter sensor ID [temp_01]: " SELECTED_SENSOR
        SELECTED_SENSOR=${SELECTED_SENSOR:-temp_01}
    fi
    
    # Temperature thresholds
    read -p "High temperature threshold (°C) [35.0]: " high_threshold
    high_threshold=${high_threshold:-35.0}
    
    read -p "Low temperature threshold (°C) [5.0]: " low_threshold  
    low_threshold=${low_threshold:-5.0}
    
    # Notification preferences
    echo
    echo "Notification setup:"
    echo
    
    read -p "Enable email notifications? (y/n) [y]: " enable_email
    enable_email=${enable_email:-y}
    
    if [[ $enable_email == "y" || $enable_email == "Y" ]]; then
        read -p "SMTP server [smtp.gmail.com]: " smtp_server
        smtp_server=${smtp_server:-smtp.gmail.com}
        
        read -p "SMTP port [587]: " smtp_port
        smtp_port=${smtp_port:-587}
        
        read -p "Email username: " email_user
        read -s -p "Email password (will be hidden): " email_pass
        echo
        
        read -p "From email address: " from_email
        read -p "To email address: " to_email
    fi
    
    read -p "Enable Telegram notifications? (y/n) [n]: " enable_telegram
    enable_telegram=${enable_telegram:-n}
    
    if [[ $enable_telegram == "y" || $enable_telegram == "Y" ]]; then
        read -p "Telegram bot token: " telegram_token
        read -p "Telegram chat ID: " telegram_chat
    fi
    
    # Generate configuration file
    cat > "$config_file" <<EOF
# Temperature Alert Skill Configuration
# Generated by setup script on $(date)

config:
  high_threshold: $high_threshold
  low_threshold: $low_threshold
  rate_threshold: 5.0
  cooldown_minutes: 15
  sensor_id: "$SELECTED_SENSOR"
  sensor_type: "${SENSOR_TYPE:-DS18B20}"

notifications:
EOF
    
    if [[ $enable_email == "y" || $enable_email == "Y" ]]; then
        cat >> "$config_file" <<EOF
  email:
    enabled: true
    smtp_server: "$smtp_server"
    smtp_port: $smtp_port
    username: "$email_user"
    password: "$email_pass"
    from_email: "$from_email"
    to_email: "$to_email"
EOF
    fi
    
    if [[ $enable_telegram == "y" || $enable_telegram == "Y" ]]; then
        cat >> "$config_file" <<EOF
  telegram:
    enabled: true
    bot_token: "$telegram_token"
    chat_id: "$telegram_chat"
EOF
    fi
    
    print_status "Configuration saved to $config_file"
}

# Install the skill
install_skill() {
    print_step "Installing temperature alert skill..."
    
    if [[ -f "$SKILL_DIR/skill.yaml" ]]; then
        $CLAW_SKILL_CMD skill install "$SKILL_DIR"
        print_status "Skill installed successfully"
    else
        print_error "Skill definition not found at $SKILL_DIR/skill.yaml"
        exit 1
    fi
}

# Test the installation
test_installation() {
    print_step "Testing installation..."
    
    # Test sensor reading
    print_status "Testing sensor reading..."
    if $CLAW_SKILL_CMD skill test $SKILL_NAME --action read_sensor; then
        print_status "Sensor reading test passed"
    else
        print_warning "Sensor reading test failed - check sensor connection"
    fi
    
    # Test notification system
    read -p "Send test notification? (y/n) [y]: " send_test
    send_test=${send_test:-y}
    
    if [[ $send_test == "y" || $send_test == "Y" ]]; then
        print_status "Sending test notification..."
        if $CLAW_SKILL_CMD skill run $SKILL_NAME --action test_notifications; then
            print_status "Test notification sent successfully"
        else
            print_warning "Test notification failed - check configuration"
        fi
    fi
}

# Enable monitoring
enable_monitoring() {
    print_step "Enabling temperature monitoring..."
    
    $CLAW_SKILL_CMD skill enable $SKILL_NAME
    print_status "Temperature monitoring enabled"
    
    echo
    print_status "Setup complete! Temperature monitoring is now active."
    echo
    echo "Useful commands:"
    echo "  $CLAW_SKILL_CMD skill status $SKILL_NAME     # Check status"
    echo "  $CLAW_SKILL_CMD skill logs $SKILL_NAME       # View logs"  
    echo "  $CLAW_SKILL_CMD skill config $SKILL_NAME     # Edit config"
    echo "  $CLAW_SKILL_CMD skill test $SKILL_NAME       # Run tests"
    echo
}

# Main setup flow
main() {
    local REBOOT_REQUIRED=false
    local DETECTED_SENSORS=()
    local SELECTED_SENSOR=""
    local CLAW_COMMAND=""
    local CLAW_SKILL_CMD=""
    local SENSOR_TYPE="DS18B20"
    
    check_system
    check_dependencies
    enable_interfaces
    install_python_deps
    detect_sensors
    configure_skill
    install_skill
    test_installation
    enable_monitoring
    
    if [[ $REBOOT_REQUIRED == true ]]; then
        echo
        print_warning "A reboot is required to complete 1-Wire setup"
        read -p "Reboot now? (y/n) [n]: " reboot_now
        
        if [[ $reboot_now == "y" || $reboot_now == "Y" ]]; then
            print_status "Rebooting system..."
            sudo reboot
        else
            print_warning "Please reboot manually to complete setup"
        fi
    fi
}

# Run setup if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi