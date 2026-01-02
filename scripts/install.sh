#!/bin/bash
# Installation script for projector trigger bridge service

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
INSTALL_DIR="/opt/projector-trigger"
SERVICE_NAME="projector-trigger"

echo "=========================================="
echo "Projector Trigger Bridge Installation"
echo "=========================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Error: This script must be run as root (use sudo)"
    exit 1
fi

# Update package list
echo "Updating package list..."
apt-get update

# Install dependencies
echo "Installing dependencies..."
apt-get install -y python3 python3-pip python3-venv git nmap

# Install Python packages
echo "Installing Python packages..."
pip3 install --break-system-packages pyyaml gpiozero

# Create installation directory
echo "Creating installation directory: $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"

# Copy project files
echo "Copying project files..."
cp -r "$PROJECT_DIR/projector_trigger" "$INSTALL_DIR/"

# Copy config if it doesn't exist
if [ ! -f "$INSTALL_DIR/config.yaml" ]; then
    if [ -f "$PROJECT_DIR/config.yaml" ]; then
        cp "$PROJECT_DIR/config.yaml" "$INSTALL_DIR/config.yaml"
        echo "Copied config.yaml to $INSTALL_DIR"
    else
        echo "Warning: config.yaml not found, creating default..."
        cat > "$INSTALL_DIR/config.yaml" << 'EOF'
gpio:
  pin: 17
  debounce_ms: 300
projector:
  # Option 1: MAC address for auto-discovery (recommended - works with DHCP)
  mac: "F8-4E-17-B8-E0-9E"  # Replace with your projector's MAC address
  # Option 2: Static IP address (alternative)
  # ip: "192.168.1.100"
  port: 53595
  power_on_command: "POWR 1"
  power_off_command: "POWR 0"
  timeout_seconds: 1.5
  max_retries: 3
  retry_backoff_seconds: 0.5
logging:
  level: "INFO"
EOF
    fi
else
    echo "config.yaml already exists, skipping..."
fi

# Install systemd service
echo "Installing systemd service..."
if [ -f "$PROJECT_DIR/systemd/$SERVICE_NAME.service" ]; then
    cp "$PROJECT_DIR/systemd/$SERVICE_NAME.service" "/etc/systemd/system/"
    systemctl daemon-reload
    systemctl enable "$SERVICE_NAME.service"
    echo "Service installed and enabled"
else
    echo "Error: Service file not found at $PROJECT_DIR/systemd/$SERVICE_NAME.service"
    exit 1
fi

# Set permissions
echo "Setting permissions..."
chown -R root:root "$INSTALL_DIR"
chmod -R 755 "$INSTALL_DIR"

echo ""
echo "=========================================="
echo "Installation complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit $INSTALL_DIR/config.yaml with your projector IP and settings"
echo "2. Start the service: sudo systemctl start $SERVICE_NAME"
echo "3. Check status: sudo systemctl status $SERVICE_NAME"
echo "4. View logs: sudo journalctl -u $SERVICE_NAME -f"
echo ""
echo "To test manually:"
echo "  python3 -m projector_trigger status"
echo "  python3 -m projector_trigger on"
echo "  python3 -m projector_trigger off"
echo "  python3 -m projector_trigger monitor"
echo ""

