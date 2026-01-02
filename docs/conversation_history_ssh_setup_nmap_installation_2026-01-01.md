# Conversation History: SSH Setup & nmap Installation
**Date:** January 1, 2026  
**Topic:** Raspberry Pi Projector Trigger Bridge - SSH Configuration, nmap Installation, and Service Deployment

## Summary
This conversation covered setting up SSH keys, installing nmap for MAC address discovery, fixing GPIO code compatibility issues, and successfully deploying the projector trigger bridge service to the Raspberry Pi.

## Key Accomplishments

### 1. SSH Key Configuration
- **Issue:** SSH keys were already installed for `admin` user, but config was using `pi` user
- **Solution:** Updated `~/.ssh/config` to use `admin` user for Raspberry Pi at `192.168.50.110`
- **Result:** Passwordless SSH access working

### 2. nmap Installation
- **Requirement:** Needed nmap for automatic projector discovery by MAC address (for future homeowners)
- **Implementation:** Added `nmap` to `scripts/install.sh` dependency installation
- **Location:** `/opt/projector-trigger` on Raspberry Pi
- **Result:** MAC address discovery now works automatically

### 3. GPIO Code Fix
- **Issue:** `active_low` parameter not supported in gpiozero version on Pi
- **Error:** `DigitalInputDevice.__init__() got an unexpected keyword argument 'active_low'`
- **Solution:** Removed `active_low` parameter and manually inverted the logic:
  - `when_deactivated` → trigger ON (LOW = active)
  - `when_activated` → trigger OFF (HIGH = idle)
  - `read_state()` returns `not device.is_active` to invert the logic
- **File:** `projector_trigger/gpio_monitor.py`

### 4. Configuration Updates
- **Config File:** Updated to use MAC address `F8-4E-17-B8-E0-9E` by default
- **Default Config:** Changed install script default to use MAC address instead of static IP
- **Reason:** Enables automatic discovery even when network changes (perfect for new homeowners)

### 5. Service Deployment
- **Status:** Service successfully installed and running
- **Location:** `/opt/projector-trigger`
- **Service:** `projector-trigger.service` (systemd)
- **Projector Discovery:** Successfully finding projector at `192.168.50.182` via MAC address

## Technical Details

### SSH Configuration
```ssh-config
Host raspberrypi
    HostName 192.168.50.110
    User admin
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

### GPIO Monitor Fix
**Before:**
```python
self._device = DigitalInputDevice(
    pin=pin,
    pull_up=True,
    active_low=True  # Not supported in this gpiozero version
)
```

**After:**
```python
self._device = DigitalInputDevice(
    pin=pin,
    pull_up=True
)
# Manually invert: LOW = trigger ON, HIGH = trigger OFF
self._device.when_deactivated = self._on_activated
self._device.when_activated = self._on_deactivated
```

### Install Script Changes
Added `nmap` to dependencies:
```bash
apt-get install -y python3 python3-pip python3-venv git nmap
```

### Projector Configuration
- **MAC Address:** `F8-4E-17-B8-E0-9E`
- **IP Address:** `192.168.50.182` (auto-discovered)
- **Port:** `53595`
- **Commands:** `POWR 1` (on), `POWR 0` (off)

## Commands Used

### File Transfer
```bash
scp -r projector_trigger scripts systemd config.yaml requirements.txt README.md admin@192.168.50.110:~/projector-trigger-bridge/
```

### Installation
```bash
ssh admin@192.168.50.110 "cd ~/projector-trigger-bridge && sudo bash scripts/install.sh"
```

### Service Management
```bash
# Start service
sudo systemctl start projector-trigger

# Check status
sudo systemctl status projector-trigger

# View logs
sudo journalctl -u projector-trigger -f
```

### Testing
```bash
# Test projector discovery
sudo PYTHONPATH=/opt/projector-trigger python3 -c 'from projector_trigger.network_discovery import discover_projector_ip; ip = discover_projector_ip(mac_address="F8-4E-17-B8-E0-9E"); print(f"Found: {ip}")'
```

## Files Modified
1. `scripts/install.sh` - Added nmap to dependencies
2. `config.yaml` - Updated to use MAC address by default
3. `projector_trigger/gpio_monitor.py` - Fixed active_low compatibility
4. `README.md` - Documented nmap installation
5. `~/.ssh/config` - Added Raspberry Pi SSH configuration

## Current Status
✅ SSH keys configured and working  
✅ nmap installed on Raspberry Pi  
✅ Service installed and running  
✅ Projector discovery working via MAC address  
✅ GPIO code fixed for gpiozero compatibility  
✅ Configuration set for automatic discovery (future-homeowner friendly)

## Notes
- The system is now configured to automatically discover the projector by MAC address
- This works even when the network changes (new router, DHCP, etc.)
- No technical configuration needed for future homeowners - just set the MAC address once
- Service runs as systemd service and starts automatically on boot

