#!/bin/bash
# Test script to verify MAC-only configuration works
# This simulates the "new homeowner" scenario

echo "=========================================="
echo "Testing MAC-Only Configuration"
echo "Simulating New Homeowner Scenario"
echo "=========================================="
echo ""

# Backup current config
echo "1. Backing up current config.yaml..."
ssh raspberrypi "sudo cp /opt/projector-trigger/config.yaml /opt/projector-trigger/config.yaml.backup"

# Create MAC-only config (remove IPs)
echo ""
echo "2. Creating MAC-only config (removing IP addresses)..."
ssh raspberrypi "sudo sed -i 's/^  ip:.*/# &/' /opt/projector-trigger/config.yaml"

echo ""
echo "3. Current config (MAC addresses only):"
ssh raspberrypi "grep -A2 'projector:\|denon:' /opt/projector-trigger/config.yaml | head -10"

echo ""
echo "4. Restarting service with MAC-only config..."
ssh raspberrypi "sudo systemctl restart projector-trigger"

echo ""
echo "5. Waiting for discovery (30 seconds)..."
sleep 30

echo ""
echo "6. Checking service status and logs:"
ssh raspberrypi "sudo systemctl status projector-trigger --no-pager | head -15"

echo ""
echo "7. Recent logs (showing discovery process):"
ssh raspberrypi "sudo journalctl -u projector-trigger -n 30 --no-pager | grep -E '(discover|Found|Scanning|MAC|network)'"

echo ""
echo "=========================================="
echo "Test Complete"
echo "=========================================="
echo ""
echo "If you see 'Found projector at...' and 'Found Denon AVR at...'"
echo "in the logs, the MAC-only discovery is working!"
echo ""
echo "To restore original config:"
echo "  ssh raspberrypi 'sudo cp /opt/projector-trigger/config.yaml.backup /opt/projector-trigger/config.yaml'"
echo "  ssh raspberrypi 'sudo systemctl restart projector-trigger'"

