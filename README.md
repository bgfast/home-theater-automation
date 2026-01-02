# Projector Trigger Bridge

A Raspberry Pi service that monitors a Denon AVR power state over network and controls a Sony VPL-XW5000 projector over IP network.

## Overview

This project bridges a Denon AVR's power state to a Sony projector's IP control interface. When the Denon AVR powers on (detected via network polling), the Raspberry Pi automatically sends a power-on command to the projector. When the AVR powers off, it sends a power-off command.

**Two Approaches Available:**
1. **Network-Based (Recommended)**: Monitors Denon AVR power state via telnet polling - no hardware wiring needed
2. **GPIO-Based (Alternative)**: Uses 12V trigger from Denon via optocoupler - requires additional hardware

## Features

- **Network Monitoring**: Polls Denon AVR power state via telnet (port 23)
- **MAC Address Auto-Discovery**: Automatically finds Denon and projector IPs via MAC addresses (works with DHCP)
- **Adaptive Polling**: Faster polling when AVR is on, slower when off (saves network resources)
- **Debouncing**: Validates state changes to prevent false triggers
- **Network Control**: Sends TCP/IP commands to projector with retry logic
- **Systemd Service**: Runs automatically on boot
- **CLI Tools**: Manual testing and status commands
- **Robust Error Handling**: Retries, timeouts, and comprehensive logging

## Hardware Requirements

### Network-Based Approach (Recommended)
- Raspberry Pi (tested on Pi Zero 2 W)
- Denon AVR with network control enabled (telnet on port 23)
- Sony VPL-XW5000 projector (or compatible IP-controlled projector)
- Network connection (Wi-Fi or Ethernet) - all devices on same network

**No additional hardware needed!** See [Hardware Requirements](docs/HARDWARE_REQUIREMENTS.md) for details.

### GPIO-Based Approach (Alternative)
- All of the above, plus:
- PC817 optocoupler module (or equivalent)
- Jumper wires
- Denon AVR with 12V trigger output

See [Hardware Requirements](docs/HARDWARE_REQUIREMENTS.md) for complete purchase list.

## Network Architecture

```
┌─────────────────┐
│  Denon AVR      │
│  (Port 23)      │
│  MAC: XX-XX-XX  │
└────────┬────────┘
         │
         │ Network (Telnet Polling)
         │ PW? → PWON/PWSTANDBY
         │
┌────────▼────────┐
│  Raspberry Pi   │
│  (Service)      │
└────────┬────────┘
         │
         │ Network (ADCP Protocol)
         │ power "on" / power "off"
         │
┌────────▼────────┐
│  Sony Projector │
│  (Port 53595)   │
│  MAC: XX-XX-XX  │
└─────────────────┘
```

**Key Features:**
- **MAC Address Auto-Discovery**: Both Denon and projector discovered by MAC address
- **DHCP Compatible**: Works even when IP addresses change
- **No Physical Wiring**: Everything over network
- **Adaptive Polling**: Efficient network usage

### GPIO Wiring (Alternative Approach)

If using GPIO-based monitoring instead:

```
Denon AVR 12V Trigger:
┌─────────────────┐
│  Tip = +12V     │──┐
│  Sleeve = GND   │──┼──┐
└─────────────────┘  │  │
                      │  │
PC817 Optocoupler:    │  │
┌─────────────────┐   │  │
│  IN+  ← +12V    │───┘  │
│  IN-  ← GND     │──────┘
│                 │
│  OUT → GPIO17   │──────→ Raspberry Pi GPIO17
│  GND → GND      │──────→ Raspberry Pi GND
│  VCC → 3.3V     │──────→ Raspberry Pi 3.3V (if needed)
└─────────────────┘
```

**Important Notes:**
- The trigger is **ACTIVE-LOW** at the GPIO (trigger ON pulls GPIO LOW)
- Internal pull-up resistor is used
- GPIO LOW = Trigger ON = Projector ON
- GPIO HIGH = Trigger OFF = Projector OFF

## Software Setup

### 1. Install Raspberry Pi OS

#### Option A: Using Scripts (Recommended)

1. **Download the OS image:**
   ```bash
   cd /path/to/raspberry-pi
   bash scripts/download_image.sh
   ```
   This downloads Raspberry Pi OS Lite (64-bit) to `downloads/` directory.

2. **Write image to SD card:**
   ```bash
   bash scripts/write_image.sh
   ```
   Follow the prompts to select your SD card. **WARNING**: This will erase all data on the SD card.

#### Option B: Using Raspberry Pi Imager

1. Download [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
2. Insert SD card
3. Choose Device: **Raspberry Pi Zero 2 W**
4. Choose OS: **Raspberry Pi OS Lite (64-bit)**
5. Click gear icon and configure:
   - Hostname: `projector-bridge`
   - Enable SSH: **ON**
   - Set username/password
   - Configure Wi‑Fi (SSID + password)
   - Set locale/timezone
6. Write image to SD card

### 2. First Boot and System Update

1. Insert SD card into Pi and power on
2. Find Pi's IP address (check router DHCP leases or use network scanner)
3. SSH into the Pi:
   ```bash
   ssh <username>@<pi_ip>
   ```

4. Update the system:
   ```bash
   sudo apt-get update
   sudo apt-get -y upgrade
   ```

5. Install basics:
   ```bash
   sudo apt-get -y install git python3 python3-venv
   ```

### 3. Install Projector Trigger Bridge

1. Clone or copy this repository to the Pi:
   ```bash
   git clone <your_repo_url>
   cd projector-trigger-bridge
   ```
   Or use `scp` to copy files from your development machine.

2. Run the installer:
   ```bash
   sudo bash scripts/install.sh
   ```

3. Edit the configuration:
   ```bash
   sudo nano /opt/projector-trigger/config.yaml
   ```
   
   Update at minimum:
   - `denon.mac`: Your Denon AVR's MAC address (recommended - enables auto-discovery)
     - OR `denon.ip`: Static IP address (alternative)
   - `projector.mac`: Your projector's MAC address (recommended - enables auto-discovery)
     - OR `projector.ip`: Static IP address (alternative)
   
   **Tip**: Using MAC addresses is recommended - the system will automatically find both devices' IP addresses even if they change (DHCP). This makes it work seamlessly for new homeowners without any network configuration!
   
   **Finding MAC Addresses:**
   - **Denon AVR**: Check the AVR's network settings menu, or use `arp -a` on your computer
   - **Projector**: Check the projector's network settings menu, or use `arp -a` on your computer

4. (Optional) Create `.env` file for HTTP interface password:
   ```bash
   sudo nano /opt/projector-trigger/.env
   ```
   
   Add your projector HTTP password:
   ```
   PROJECTOR_PASSWORD=your_password_here
   ```
   
   **Note**: This is only needed if you want to access the projector's HTTP web interface. The main service (ADCP control) doesn't require HTTP authentication.

4. Start the service:
   ```bash
   sudo systemctl start projector-trigger
   sudo systemctl enable projector-trigger  # Enable on boot
   ```

5. Check status:
   ```bash
   sudo systemctl status projector-trigger
   ```

6. View logs:
   ```bash
   sudo journalctl -u projector-trigger -f
   ```

## Configuration

Edit `/opt/projector-trigger/config.yaml`:

```yaml
# GPIO settings (only needed for GPIO-based approach)
gpio:
  pin: 17                    # GPIO pin number
  debounce_ms: 300          # Debounce interval (milliseconds)

# Denon AVR settings (for network-based monitoring - RECOMMENDED)
denon:
  # Option 1: MAC address for auto-discovery (RECOMMENDED)
  # The system will automatically find the Denon's IP address via DHCP
  mac: "AA-BB-CC-DD-EE-FF"  # Denon AVR MAC address
  
  # Option 2: Static IP address (alternative)
  # ip: "192.168.1.100"     # Uncomment if you prefer static IP
  
  port: 23                  # Telnet port (default 23)
  poll_interval_off: 5.0    # Polling interval when AVR is off (seconds)
  poll_interval_on: 2.0     # Polling interval when AVR is on (seconds)

# Projector network settings
projector:
  # Option 1: MAC address for auto-discovery (RECOMMENDED)
  # The system will automatically find the projector's IP address via DHCP
  mac: "F8-4E-17-B8-E0-9E"  # Projector MAC address
  
  # Option 2: Static IP address (alternative)
  # ip: "192.168.1.100"     # Uncomment if you prefer static IP
  
  port: 53595               # TCP port (Sony projectors use 53595)
  power_on_command: 'power "on"'   # Power on command (ADCP format)
  power_off_command: 'power "off"'  # Power off command (ADCP format)
  timeout_seconds: 1.5      # TCP timeout per attempt
  max_retries: 3            # Maximum retry attempts
  retry_backoff_seconds: 0.5  # Base backoff delay

logging:
  level: "INFO"              # DEBUG, INFO, WARNING, ERROR
```

**Important**: Using MAC address auto-discovery is recommended because:
- Works automatically with DHCP (no static IP configuration needed)
- Survives network changes (new router, new internet connection)
- No configuration needed for new homeowners
- The system finds both devices automatically on startup

After changing config, restart the service:
```bash
sudo systemctl restart projector-trigger
```

## CLI Commands

Test and control the bridge manually:

```bash
# Show current status
python3 -m projector_trigger status

# Manually send power on command
python3 -m projector_trigger on

# Manually send power off command
python3 -m projector_trigger off

# Monitor GPIO changes in real-time
python3 -m projector_trigger monitor
```

## Service Management

```bash
# Start service
sudo systemctl start projector-trigger

# Stop service
sudo systemctl stop projector-trigger

# Restart service
sudo systemctl restart projector-trigger

# Enable on boot
sudo systemctl enable projector-trigger

# Disable on boot
sudo systemctl disable projector-trigger

# View logs
sudo journalctl -u projector-trigger -f

# View recent logs
sudo journalctl -u projector-trigger -n 50
```

## Troubleshooting

### GPIO reads inverted

**Symptoms**: Projector turns on when trigger goes OFF, turns off when trigger goes ON.

**Solution**: The optocoupler wiring may be reversed. Check:
- Denon +12V → Optocoupler IN+
- Denon GND → Optocoupler IN-
- Optocoupler OUT → GPIO17
- Optocoupler GND → Pi GND

Alternatively, you can modify the code to invert the logic in `gpio_monitor.py`.

### No network route to projector

**Symptoms**: Logs show "Socket error" or "Timeout connecting to projector".

**Solution**:
1. Verify projector IP address in config:
   ```bash
   python3 -m projector_trigger status
   ```

2. Test network connectivity:
   ```bash
   ping <projector_ip>
   telnet <projector_ip> <port>
   ```

3. Check firewall rules on Pi and network

4. Verify projector is on the same network segment

5. Test manually:
   ```bash
   python3 -m projector_trigger on
   ```

### Projector not waking (Remote Start / Power Saving settings)

**Symptoms**: Commands are sent successfully but projector doesn't respond.

**Solution**:
1. Check projector's "Remote Start" or "Network Standby" setting - it must be enabled
2. Verify projector's power saving mode allows network wake
3. Check projector's IP control settings in its menu
4. Try sending commands manually to verify projector responds:
   ```bash
   echo "POWR 1" | nc <projector_ip> <port>
   ```

### Service won't start

**Symptoms**: `systemctl status` shows failed state.

**Solution**:
1. Check logs for errors:
   ```bash
   sudo journalctl -u projector-trigger -n 100
   ```

2. Verify config file syntax:
   ```bash
   python3 -c "import yaml; yaml.safe_load(open('/opt/projector-trigger/config.yaml'))"
   ```

3. Test manually:
   ```bash
   cd /opt/projector-trigger
   python3 -m projector_trigger.main --config config.yaml
   ```

4. Check GPIO permissions (service runs as root, should be OK)

### GPIO not working

**Symptoms**: Status shows "GPIO State: Not available".

**Solution**:
1. Verify you're running on a Raspberry Pi (not a development machine)
2. Check GPIO pin number in config matches your wiring
3. Verify `gpiozero` is installed:
   ```bash
   pip3 show gpiozero
   ```

4. Test GPIO manually:
   ```python
   from gpiozero import DigitalInputDevice
   device = DigitalInputDevice(pin=17, pull_up=True, active_low=True)
   print(device.is_active)
   ```

### Projector HTTP Web Interface Access

**About the HTTP Interface:**
The Sony XW5000 projector provides an HTTP web interface on port 80 for configuration and monitoring. This is separate from the ADCP control protocol (port 53595) used for power control.

**Important Authentication Notes:**
- **Default Credentials**: `root` / `Projector` (capital P)
- **Authentication Type**: HTTP Digest authentication (non-standard, not Basic auth)
- **Password Change Required**: The password MUST be changed on first login (enforced by projector)
- **After First Login**: The default password will no longer work - you must use the new password you set
- **Password Requirements**: 8-16 characters, must include both letters and numbers, case-sensitive

**Accessing the Web Interface:**
1. **Using Firefox** (recommended - handles Digest auth better):
   - Navigate to `http://<projector_ip>/`
   - Enter credentials when prompted

2. **Using Chrome** (requires proxy):
   - Use the provided `proxy_auth.py` script:
     ```bash
     export PROJECTOR_PASSWORD="your_password"
     python3 scripts/test-scripts/proxy_auth.py
     ```
   - Then visit `http://localhost:8888/` in Chrome

3. **If Password is Forgotten**:
   - Perform "All Reset" on projector: Menu > Setup > All Reset
   - This restores default password: `root` / `Projector`
   - You will be prompted to change it again on first login

**Note**: The HTTP interface is for configuration only. Power control uses the ADCP protocol on port 53595, which does not require HTTP authentication.

## Project Structure

```
projector-trigger-bridge/
├── projector_trigger/          # Python package
│   ├── __init__.py
│   ├── config.py               # Configuration management
│   ├── gpio_monitor.py         # GPIO monitoring with debouncing
│   ├── projector_control.py    # TCP/IP projector control
│   ├── main.py                 # Service daemon
│   └── cli.py                  # CLI commands
├── config.yaml                 # Example configuration
├── systemd/
│   └── projector-trigger.service  # Systemd service file
├── scripts/
│   ├── install.sh              # Installation script
│   ├── download_image.sh       # Download Raspberry Pi OS image
│   └── write_image.sh          # Write image to SD card
└── README.md                   # This file
```

## Development

### Running on Non-Pi Hardware

The code will run on non-Raspberry Pi systems for testing, but GPIO monitoring will be disabled. You can still test the projector control and CLI commands.

### Dependencies

- Python 3.7+
- `pyyaml` - Configuration file parsing
- `gpiozero` - GPIO control (Raspberry Pi only)
- `nmap` - Network scanning for MAC address discovery (installed automatically by install script)

Install development dependencies:
```bash
pip3 install pyyaml gpiozero
```

**Note**: The `install.sh` script automatically installs `nmap` on the Raspberry Pi, which enables automatic projector discovery by MAC address. This allows the system to find the projector even when the network changes, making it work seamlessly for new homeowners without any technical configuration.

## License

This project is provided as-is for personal use.

## Notes

- This project intentionally avoids HDMI-CEC and IR control methods
- The Denon trigger is authoritative; projector is controlled via IP
- The service automatically restarts on failure (systemd restart policy)
- All logging goes to journald (view with `journalctl`)

