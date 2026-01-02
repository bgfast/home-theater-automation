# Projector Trigger Bridge - Setup Session History

**Date**: January 1, 2025  
**Project**: Denon 12V Trigger → Raspberry Pi → Sony VPL-XW5000 IP Control

## Overview

This document captures the complete setup session for the projector trigger bridge project, including all code changes, configuration updates, and implementation decisions.

## Initial Project Setup

### Project Requirements
- Read Denon AVR 12V trigger via optocoupler (PC817) on GPIO17
- Send IP control commands to Sony VPL-XW5000 projector
- Run as systemd service
- Provide CLI for testing
- Support MAC address auto-discovery (added during session)

### Files Created

#### Core Python Package
- `projector_trigger/__init__.py` - Package initialization
- `projector_trigger/config.py` - Configuration management with MAC/IP support
- `projector_trigger/gpio_monitor.py` - GPIO monitoring with debouncing
- `projector_trigger/projector_control.py` - TCP/IP projector control with retries
- `projector_trigger/main.py` - Main service daemon
- `projector_trigger/cli.py` - CLI commands (status, on, off, monitor)
- `projector_trigger/network_discovery.py` - MAC address-based auto-discovery (NEW)

#### Configuration & Deployment
- `config.yaml` - Configuration file with MAC address support
- `systemd/projector-trigger.service` - Systemd service file
- `scripts/install.sh` - Installation script
- `requirements.txt` - Python dependencies

#### SD Card Setup Scripts
- `scripts/download_image.sh` - Downloads Raspberry Pi OS Lite (64-bit)
- `scripts/write_image.sh` - Writes image to SD card with SSH/user setup

#### Documentation
- `README.md` - Complete documentation with wiring diagram and troubleshooting

## Key Implementation Decisions

### 1. MAC Address Auto-Discovery (Major Enhancement)

**Problem**: Original design required static IP configuration, which would be problematic for new homeowners with different networks.

**Solution**: Implemented MAC address-based auto-discovery that:
- Automatically finds projector IP via ARP table, nmap, or arp-scan
- Works with DHCP (no static IP needed)
- Survives network changes
- Zero configuration for new homeowners

**Implementation**:
- Created `network_discovery.py` module
- Updated `config.py` to support both `mac` and `ip` options
- Modified `main.py` and `cli.py` to use auto-discovery
- Updated `config.yaml` to use MAC address by default

**Config Example**:
```yaml
projector:
  mac: "F8-4E-17-B8-E0-9E"  # Auto-discovers IP - works with DHCP!
  port: 53595
  power_on_command: "POWR 1"
  power_off_command: "POWR 0"
```

### 2. Raspberry Pi OS Setup

**Process**:
1. Downloaded Raspberry Pi OS Lite (64-bit) image
2. Created script to write image to SD card
3. Configured SSH and user account (admin/admin) on boot partition
4. Successfully booted Pi Zero 2 W on network at `192.168.50.110`

**SSH Key Setup**:
- Generated SSH key pair for passwordless access
- Configured on Pi for non-interactive operations

### 3. Installation Process

**Steps Completed**:
1. ✅ Updated system packages
2. ✅ Installed Python 3, pip, git
3. ✅ Copied project files to Pi
4. ✅ Ran installation script
5. ✅ Service installed and enabled (not started yet - waiting for projector network connection)

## Hardware Configuration

### Raspberry Pi Zero 2 W
- **IP Address**: `192.168.50.110`
- **MAC Address**: `9C:69:D3:19:D9:B6`
- **OS**: Raspberry Pi OS Lite (64-bit) Bookworm
- **User**: admin (password: admin)

### Sony VPL-XW5000 Projector
- **MAC Address**: `F8-4E-17-B8-E0-9E`
- **IP Control Port**: `53595` (default)
- **Commands**: `POWR 1` (on), `POWR 0` (off)
- **Status**: Awaiting ethernet connection

### Required Projector Settings

1. **Network Management**: `On` (Setup → Network Management)
2. **Remote Start**: `On` (Setup → Remote Start) - **Critical for network wake**
3. **Network Setting**: `Auto(DHCP)` (Installation → Network Setting → IPv4 Setting)
4. **Web Control UI**: Optional (Setup → Web Control UI)

## Wiring Configuration

### Denon 12V Trigger → Optocoupler
- Tip = +12V → Optocoupler IN+
- Sleeve = GND → Optocoupler IN-

### Optocoupler → Raspberry Pi
- OUT → GPIO17
- GND → Pi GND
- VCC → Pi 3.3V (if module requires it)

### Software Configuration
- GPIO17 with internal pull-up
- Active-LOW: GPIO LOW = Trigger ON = Projector ON
- Debounce: 300ms (configurable)

## Code Architecture

### Network Discovery Module (`network_discovery.py`)

**Functions**:
- `normalize_mac()` - Converts MAC to standard format
- `get_local_network()` - Auto-detects network CIDR
- `find_ip_by_mac()` - Searches for device by MAC address
- `discover_projector_ip()` - Main discovery function

**Discovery Methods** (in order):
1. ARP table lookup (fastest)
2. nmap network scan (if available)
3. arp-scan (if available)

### Configuration System

**Supports**:
- MAC address (recommended) - auto-discovery
- Static IP (alternative) - direct specification
- All other settings remain configurable

### Service Architecture

**Components**:
- `GPIOMonitor` - Monitors GPIO with debouncing
- `ProjectorControl` - Sends TCP commands with retries
- `NetworkDiscovery` - Finds projector IP automatically
- `Config` - Manages all configuration

**Service Flow**:
1. Load configuration
2. Discover projector IP (if MAC specified)
3. Initialize GPIO monitor
4. Initialize projector control
5. Monitor GPIO for trigger changes
6. Send commands on state change

## CLI Commands

All commands support auto-discovery:

```bash
python3 -m projector_trigger status   # Show status (discovers IP)
python3 -m projector_trigger on       # Send power on
python3 -m projector_trigger off      # Send power off
python3 -m projector_trigger monitor  # Monitor GPIO in real-time
```

## Next Steps

### Immediate
1. ✅ Complete ethernet cable crimping for projector
2. ⏳ Connect projector to network
3. ⏳ Verify projector gets IP address
4. ⏳ Test auto-discovery: `python3 -m projector_trigger status`
5. ⏳ Start service: `sudo systemctl start projector-trigger`
6. ⏳ Test GPIO trigger → projector control

### Future Enhancements
- Add periodic IP re-discovery (in case projector IP changes)
- Add web interface for configuration
- Add status monitoring/health checks
- Add support for multiple projectors

## Troubleshooting Notes

### SSH Connection Issues
- Initial connection refused - fixed by manually creating `/boot/ssh` and `/boot/userconf` files
- SSH key authentication configured for non-interactive access

### Network Discovery
- Uses ARP table first (fastest)
- Falls back to network scanning if needed
- Handles MAC address format variations

### Projector Settings
- **Critical**: Remote Start must be ON for network wake
- Network Management must be ON for IP control
- Projector will consume more power in standby with network enabled

## Files Modified During Session

1. `projector_trigger/config.py` - Added MAC address support
2. `projector_trigger/main.py` - Added auto-discovery on startup
3. `projector_trigger/cli.py` - Added auto-discovery to all commands
4. `projector_trigger/network_discovery.py` - NEW - Complete discovery module
5. `config.yaml` - Updated to use MAC address by default
6. `README.md` - Updated documentation for MAC-based discovery
7. `scripts/write_image.sh` - Added SSH and user account configuration

## Technical Details

### GPIO Configuration
- **Pin**: GPIO17 (physical pin 11)
- **Mode**: Input with pull-up
- **Active**: LOW (trigger ON pulls GPIO LOW)
- **Debounce**: 300ms (configurable 250-500ms)

### Network Protocol
- **Protocol**: TCP
- **Port**: 53595 (Sony default)
- **Commands**: Plain text strings
- **Timeout**: 1.5s per attempt
- **Retries**: 3 attempts with exponential backoff

### Service Configuration
- **Type**: systemd service
- **User**: root (for GPIO access)
- **Restart**: always (auto-restart on failure)
- **Logging**: journald (view with `journalctl -u projector-trigger -f`)

## Session Timeline

1. **Initial Setup**: Created all project files
2. **SD Card Setup**: Downloaded and wrote Raspberry Pi OS image
3. **SSH Configuration**: Set up SSH and user account
4. **Pi Setup**: Connected to Pi, updated system, installed dependencies
5. **Code Deployment**: Copied files to Pi, ran installation script
6. **Auto-Discovery Enhancement**: Added MAC-based discovery for DHCP compatibility
7. **Configuration**: Updated config to use MAC address
8. **Documentation**: Updated README with new features

## Project Status

✅ **Complete**: Core functionality, auto-discovery, installation  
⏳ **Pending**: Projector network connection, final testing, GPIO wiring

---

**End of Setup Session History**

