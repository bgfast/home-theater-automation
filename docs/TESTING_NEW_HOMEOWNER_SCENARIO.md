# Testing the "New Homeowner" Scenario

This document explains how to test and verify that the system works for a new homeowner who:
- Has a different network setup (not 192.168.50.x)
- Only knows the MAC addresses of the devices
- Doesn't need to configure any IP addresses

## How MAC Address Auto-Discovery Works

The system automatically:
1. **Detects the local network** using `ip route` and `ip addr` commands
2. **Scans the network** using `nmap` to find all devices
3. **Matches MAC addresses** to locate your specific devices
4. **Works on any subnet** (192.168.x.x, 10.x.x.x, 172.16.x.x, etc.)

## Test Methods

### Method 1: Run the Test Script

```bash
python3 scripts/test-scripts/test_mac_discovery.py
```

This script will:
- Test network auto-detection
- Test projector discovery by MAC only
- Test Denon AVR discovery by MAC only
- Show you how to configure for MAC-only discovery

### Method 2: Manual Testing

#### Step 1: Configure with MAC Addresses Only

Edit `config.yaml` and remove/comment out the IP addresses:

```yaml
projector:
  mac: "F8-4E-17-B8-E0-9E"  # Only MAC - no IP!
  # ip: "192.168.50.182"     # Commented out

denon:
  mac: "00:06:78:97:0F:48"   # Only MAC - no IP!
  # ip: "192.168.50.148"     # Commented out
```

#### Step 2: Test Discovery

On the Raspberry Pi:

```bash
# Test projector discovery
cd /opt/projector-trigger
sudo python3 -c "
from projector_trigger.network_discovery import discover_projector_ip
ip = discover_projector_ip(mac_address='F8-4E-17-B8-E0-9E')
print(f'Found projector at: {ip}' if ip else 'Not found')
"

# Test Denon discovery
sudo python3 -c "
from projector_trigger.network_discovery import discover_denon_ip
ip = discover_denon_ip(mac_address='00:06:78:97:0F:48')
print(f'Found Denon at: {ip}' if ip else 'Not found')
"
```

#### Step 3: Restart Service

```bash
sudo systemctl restart projector-trigger
sudo journalctl -u projector-trigger -f
```

Watch the logs - you should see:
- Network detection: `Detected local network: 192.168.x.0/24`
- Scanning: `Scanning network 192.168.x.0/24 for device...`
- Discovery: `Found projector at 192.168.x.xxx via MAC address discovery`

### Method 3: Simulate Different Network

To test on a completely different network:

1. **Change your network** (if possible):
   - Connect Raspberry Pi to a different router/network
   - Or use a different subnet on your router

2. **Verify network detection**:
   ```bash
   ssh raspberrypi "python3 -c 'from projector_trigger.network_discovery import get_local_network; print(get_local_network())'"
   ```

3. **Test discovery**:
   ```bash
   ssh raspberrypi "cd /opt/projector-trigger && sudo python3 -c 'from projector_trigger.network_discovery import discover_projector_ip; print(discover_projector_ip(mac_address=\"F8-4E-17-B8-E0-9E\"))'"
   ```

## What to Verify

✅ **Network Auto-Detection**: System detects the correct network subnet
✅ **Projector Discovery**: Finds projector by MAC address on any network
✅ **Denon Discovery**: Finds Denon AVR by MAC address on any network
✅ **Service Startup**: Service starts successfully with MAC-only config
✅ **No IP Configuration**: No IP addresses needed in config.yaml

## Expected Behavior

When the service starts with MAC-only configuration:

1. **Initial Discovery** (takes 30-60 seconds):
   ```
   INFO - Searching for device with MAC address: f8:4e:17:b8:e0:9e
   INFO - Scanning network 192.168.x.0/24 for device...
   INFO - Found projector at 192.168.x.xxx via MAC address discovery
   ```

2. **Denon Discovery**:
   ```
   INFO - Searching for device with MAC address: 00:06:78:97:0f:48
   INFO - Scanning network 192.168.x.0/24 for device...
   INFO - Found Denon AVR at 192.168.x.xxx via MAC address discovery
   ```

3. **Service Running**:
   ```
   INFO - Projector control initialized: 192.168.x.xxx:53595
   INFO - Denon monitor initialized: 192.168.x.xxx:23
   INFO - Starting projector trigger bridge service...
   ```

## Troubleshooting

### Discovery Fails

**Check:**
- Devices are on the same network as Raspberry Pi
- Devices are powered on
- `nmap` is installed: `sudo apt-get install nmap`
- Network scanning is not blocked by firewall

**Test manually:**
```bash
# Check if nmap can see the devices
sudo nmap -sn 192.168.x.0/24 | grep -A2 "MAC Address"
```

### Network Detection Fails

**Check:**
- `ip` command is available: `which ip`
- Network interface is up: `ip addr show`
- Default route exists: `ip route show default`

### Service Won't Start

**Check logs:**
```bash
sudo journalctl -u projector-trigger -n 50
```

**Common issues:**
- MAC address format incorrect (should work with dashes or colons)
- Devices not reachable on network
- Network tools not installed

## For New Homeowners

**Setup Instructions:**

1. **Get MAC addresses** (from device labels or network settings):
   - Projector MAC: `F8-4E-17-B8-E0-9E`
   - Denon AVR MAC: `00:06:78:97:0F:48`

2. **Edit config.yaml**:
   ```yaml
   projector:
     mac: "F8-4E-17-B8-E0-9E"  # Your projector MAC
   
   denon:
     mac: "00:06:78:97:0F:48"   # Your Denon MAC
   ```

3. **No IP addresses needed!** The system will find them automatically.

4. **Restart service**:
   ```bash
   sudo systemctl restart projector-trigger
   ```

5. **Verify**:
   ```bash
   sudo journalctl -u projector-trigger -f
   ```

That's it! The system works on any network without IP configuration.

