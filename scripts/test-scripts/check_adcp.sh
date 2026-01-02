#!/bin/bash
# Quick check if ADCP port is open

echo "Checking if ADCP port 53595 is open..."
python3 test_projector.py scan --ip 192.168.50.182 2>&1 | grep -A 2 "Port 53595"

