# Network-Based Trigger Approach for Denon AVR-X6700H

## Overview

Instead of using the 12V trigger → GPIO approach, we can monitor the Denon AVR's power state over Ethernet and trigger the projector accordingly.

## Denon AVR-X6700H Network Control Options

### 1. **Telnet Control (Port 23) - RECOMMENDED**

Denon AVRs support telnet-based control on port 23. This is the most reliable method.

**Power Status Query:**
- Command: `PW?` (query power state)
- Response: `PWSTANDBY` or `PWON`

**Power Control:**
- Power On: `PWON`
- Power Off: `PWSTANDBY`

**Advantages:**
- ✅ Standard protocol, well-documented
- ✅ Real-time status queries
- ✅ No polling overhead (can query on-demand)
- ✅ Reliable and widely used

**Implementation:**
```python
# Query power state
sock.sendall(b'PW?\r')
response = sock.recv(1024)  # Returns "PWON" or "PWSTANDBY"
```

### 2. **HTTP API (if available)**

Some Denon AVRs expose an HTTP API, but this varies by model.

**Check if available:**
- Try: `http://<denon_ip>/goform/formMainZone_MainZoneXmlStatusLite.xml`
- Or: `http://<denon_ip>/MainZone/index.put.asp`

**Advantages:**
- ✅ RESTful interface
- ✅ Easy to parse XML/JSON responses

**Disadvantages:**
- ❌ May not be available on all models
- ❌ Requires HTTP parsing

### 3. **Network Wake-up Detection**

**Does Denon send wake-up events?**
- Most AVRs do NOT send unsolicited wake-up notifications
- They respond to queries but don't broadcast state changes

**Options:**
1. **Polling (not ideal but works):**
   - Query power state every 1-5 seconds
   - Detect state changes
   - Pros: Simple, reliable
   - Cons: Network traffic, slight delay

2. **Connection State Monitoring:**
   - Monitor if telnet port 23 becomes available (AVR wakes up)
   - Pros: Event-driven
   - Cons: May miss rapid state changes

3. **ARP Table Monitoring:**
   - Watch for AVR MAC address appearing in ARP table
   - Pros: Low-level detection
   - Cons: May not be reliable, requires root

## Recommended Approach: Telnet Polling with Smart Intervals

### Architecture

```
┌─────────────────┐
│  Denon AVR      │
│  (Port 23)      │
└────────┬────────┘
         │
         │ Telnet: PW?
         │
┌────────▼────────┐
│  Raspberry Pi   │
│  Polls every     │
│  2-5 seconds     │
└────────┬────────┘
         │
         │ State Change Detected
         │
┌────────▼────────┐
│  Projector      │
│  Control        │
└─────────────────┘
```

### Implementation Strategy

1. **Polling with Adaptive Intervals:**
   - When AVR is OFF: Poll every 5-10 seconds (low power state)
   - When AVR is ON: Poll every 2-3 seconds (active monitoring)
   - After state change: Immediate follow-up query to confirm

2. **State Change Detection:**
   - Track last known state
   - Compare with current query result
   - Trigger callback on change

3. **Debouncing:**
   - Similar to GPIO debouncing
   - Require state to be stable for 500ms-1s before triggering

### Code Structure

```python
class DenonMonitor:
    def __init__(self, ip, port=23, poll_interval_off=5.0, poll_interval_on=2.0):
        self.ip = ip
        self.port = port
        self.poll_interval_off = poll_interval_off
        self.poll_interval_on = poll_interval_on
        self.last_state = None
        self.running = False
    
    def query_power_state(self) -> Optional[bool]:
        """Query AVR power state. Returns True if ON, False if OFF, None on error."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2.0)
            sock.connect((self.ip, self.port))
            sock.sendall(b'PW?\r')
            response = sock.recv(1024).decode('utf-8', errors='ignore').strip()
            sock.close()
            
            if 'PWON' in response:
                return True
            elif 'PWSTANDBY' in response:
                return False
            return None
        except:
            return None
    
    def monitor(self, callback):
        """Monitor AVR state and call callback on changes."""
        while self.running:
            current_state = self.query_power_state()
            
            if current_state is not None and current_state != self.last_state:
                # State changed - trigger callback
                callback(current_state)
                self.last_state = current_state
            
            # Adaptive polling interval
            interval = self.poll_interval_on if current_state else self.poll_interval_off
            time.sleep(interval)
```

## Comparison: GPIO vs Network

| Aspect | GPIO (12V Trigger) | Network (Telnet) |
|-------|-------------------|------------------|
| **Reliability** | ✅ Very reliable | ✅ Reliable |
| **Latency** | ✅ Instant | ⚠️ 2-5 second delay |
| **Wiring** | ❌ Requires optocoupler | ✅ No wiring |
| **Power Consumption** | ✅ Very low | ⚠️ Network polling overhead |
| **Complexity** | ✅ Simple hardware | ⚠️ Network protocol |
| **Network Dependency** | ✅ Works offline | ❌ Requires network |
| **Detection Method** | ✅ Hardware interrupt | ⚠️ Software polling |

## Hybrid Approach (Best of Both)

You could implement both methods and use network as a fallback:

1. **Primary: GPIO** (fast, reliable)
2. **Fallback: Network** (if GPIO fails or for verification)

## Testing the Denon Network Interface

Before implementing, test if your Denon AVR-X6700H responds to telnet:

```bash
# Test telnet connection
telnet <denon_ip> 23

# Once connected, try:
PW?
# Should return: PWSTANDBY or PWON

# Try power commands:
PWON
PWSTANDBY
```

## Next Steps

1. **Test Denon telnet interface:**
   - Verify port 23 is open
   - Test `PW?` command
   - Document response format

2. **Implement DenonMonitor class:**
   - Replace GPIOMonitor with DenonMonitor
   - Keep same callback interface for compatibility

3. **Update config.yaml:**
   ```yaml
   denon:
     ip: "192.168.1.xxx"
     port: 23
     poll_interval_off: 5.0
     poll_interval_on: 2.0
   ```

4. **Update main.py:**
   - Replace GPIOMonitor initialization with DenonMonitor
   - Keep projector control logic unchanged

## Notes

- **Polling is not "archaic"** - it's a standard approach for network monitoring
- Modern systems (Home Assistant, etc.) use similar polling for device state
- 2-5 second intervals are reasonable and won't cause network congestion
- Consider using asyncio for more efficient polling if needed

