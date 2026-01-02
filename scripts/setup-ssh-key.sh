#!/bin/bash
# One-time script to copy SSH key to Raspberry Pi
# Run this once: bash setup-ssh-key.sh

PI_IP="192.168.50.110"
PI_USER="pi"  # Change this if your Pi username is different

echo "Copying SSH key to Raspberry Pi..."
echo "You will be prompted for the Pi password (one time only)"
echo ""

ssh-copy-id ${PI_USER}@${PI_IP}

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

