#!/bin/bash
# One-time script to copy SSH key to Raspberry Pi
# Run this once: bash setup-ssh-key.sh
#
# Credentials can be set via:
#   - .env file (recommended): RASPBERRY_PI_IP, RASPBERRY_PI_USER, RASPBERRY_PI_PASSWORD
#   - Environment variables: export RASPBERRY_PI_IP=...
#   - Script defaults (fallback)

# Load .env file if it exists (from project root or current directory)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
for env_file in "$PROJECT_ROOT/.env" "$(pwd)/.env" "$HOME/.config/projector-trigger/.env"; do
    if [ -f "$env_file" ]; then
        # Source .env file, ignoring comments and empty lines
        set -a
        source <(grep -v '^#' "$env_file" | grep -v '^$')
        set +a
        break
    fi
done

# Get credentials from environment or use defaults
PI_IP="${RASPBERRY_PI_IP:-192.168.50.110}"
PI_USER="${RASPBERRY_PI_USER:-admin}"  # Default: admin (created by write_image.sh)
PI_PASSWORD="${RASPBERRY_PI_PASSWORD:-admin}"

echo "Copying SSH key to Raspberry Pi..."
echo "IP: $PI_IP"
echo "User: $PI_USER"
echo "You will be prompted for the Pi password (one time only)"
echo ""

# Use sshpass if available and password is set, otherwise use interactive prompt
if command -v sshpass >/dev/null 2>&1 && [ -n "$PI_PASSWORD" ]; then
    sshpass -p "$PI_PASSWORD" ssh-copy-id -o StrictHostKeyChecking=no ${PI_USER}@${PI_IP}
else
    ssh-copy-id ${PI_USER}@${PI_IP}
fi

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ SSH key successfully copied!"
    echo "You can now SSH without a password."
else
    echo ""
    echo "✗ Failed to copy SSH key. Make sure:"
    echo "  - The Pi username is correct (currently: $PI_USER)"
    echo "  - Password authentication is enabled on the Pi"
    echo "  - You can reach the Pi at $PI_IP"
fi

