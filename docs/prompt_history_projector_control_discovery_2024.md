# Prompt History: Sony Projector Control & Network Integration Discovery

**Date:** 2024  
**Session Focus:** Sony XW5000 projector control setup, ADCP protocol discovery, Denon AVR network integration planning

---

## Key Questions & Discoveries

### 1. CEC Support Investigation
**Question:** Can Sony XW5000 be configured to start via CEC?

**Answer:** No. The Sony VPL-XW5000 does NOT support HDMI-CEC for power control. Alternative methods:
- Network/Remote Start (IP control) - **This is what we're using**
- Direct Power-On Function (circuit breaker method)

**Reference:** Manual confirms CEC is not supported for this model.

---

### 2. TCP/IP Command Testing
**Created:** `test_projector.py` - Script to test TCP/IP commands to projector

**Initial Issue:** Commands were failing with connection refused errors.

**Discovery Process:**
- Port 53595 (ADCP) was closed initially
- Port 80 (HTTP) was open - web interface available
- Required enabling "Network Management" and "Remote Start" in projector menu
- Also needed to enable "ADCP Service" in Advanced Settings

---

### 3. HTTP Web Interface Access
**Question:** How to access projector web interface from Chrome?

**Discovery:**
- Default credentials: `root` / `Projector` (capital P)
- First login requires password change (8-16 chars, letters + numbers)
- Chrome doesn't handle Digest auth well - created proxy solution
- Created `proxy_auth.py` for Chrome browser access

**Created Files:**
- `test_http_auth.py` - Brute force credential testing
- `http_connect.py` - Simple HTTP connection test
- `proxy_auth.py` - HTTP proxy with Digest authentication
- `open_projector_web.sh` - Browser launcher script

---

### 4. ADCP Command Format Discovery
**Initial Assumption:** Commands were `POWR 1` and `POWR 0`

**Actual Discovery:** 
- Correct format: `power "on"` and `power "off"`
- Response: `ok` when successful
- Initial `NOKEY` message is informational, not an error
- Commands must end with `\r\n`

**Testing Process:**
- Tested various command formats
- Discovered correct format through hex dump analysis
- Updated `test_projector.py` and `config.yaml` with correct commands

**Key Commands:**
```python
power "on"   # Power on projector
power "off"  # Power off projector
```

---

### 5. Network-Based Trigger Approach
**Question:** Can we use Ethernet connection on Denon AVR-X6700H instead of 12V trigger?

**Investigation:**
- Denon AVRs support telnet control on port 23
- Power query command: `PW?` → Returns `PWON` or `PWSTANDBY`
- No unsolicited wake-up events - requires polling
- Polling approach (2-5 second intervals) is standard and acceptable

**Created Files:**
- `network_trigger_approach.md` - Comprehensive planning document
- `test_denon.py` - Test script for Denon network control
- `denon_manuals.md` - Manual references and links

**Recommendation:** 
- Telnet polling with adaptive intervals (slower when OFF, faster when ON)
- Similar debouncing logic as GPIO approach
- Eliminates need for optocoupler hardware

---

### 6. Source Control & Security
**Task:** Set up proper git repository with sensitive data protection

**Actions Taken:**
- Created `.gitignore` to exclude sensitive files
- Created `config.yaml.template` with placeholder values
- Removed hardcoded passwords from source files
- Updated scripts to use environment variables
- Created documentation: `README_CONFIG.md`, `SOURCE_CONTROL.md`

**Files Excluded:**
- `config.yaml` (contains MAC addresses, IPs)
- `downloads/*.img` (OS images)
- `*.log` files
- Password-containing files

**Environment Variables:**
- `PROJECTOR_IP` - Projector IP address
- `PROJECTOR_USERNAME` - HTTP username (default: root)
- `PROJECTOR_PASSWORD` - HTTP password (must be set)
- `PROXY_PORT` - Proxy server port

---

## Files Created During Session

### Test & Utility Scripts
1. `test_projector.py` - TCP/IP command testing for projector
2. `test_http_auth.py` - HTTP authentication credential testing
3. `test_denon.py` - Denon AVR network control testing
4. `http_connect.py` - Simple HTTP connection test
5. `proxy_auth.py` - HTTP proxy for Chrome browser access
6. `open_projector_web.sh` - Browser launcher script
7. `check_adcp.sh` - Quick ADCP port check script

### Documentation
1. `network_trigger_approach.md` - Network-based trigger planning
2. `denon_manuals.md` - Denon AVR manual references
3. `README_CONFIG.md` - Configuration setup guide
4. `SOURCE_CONTROL.md` - Git source control guidelines
5. `config.yaml.template` - Configuration template

### Configuration
1. `.gitignore` - Git ignore rules
2. `config.yaml.template` - Safe configuration template

---

## Key Technical Discoveries

### Sony XW5000 ADCP Protocol
- **Port:** 53595
- **Format:** ASCII text commands
- **Commands:** `power "on"`, `power "off"`
- **Response:** `ok` for success, `err_*` for errors
- **Initial Message:** `NOKEY` (informational, not an error)

### Sony XW5000 HTTP Interface
- **Port:** 80
- **Authentication:** Digest (HTTPDigestAuth)
- **Default Credentials:** `root` / `Projector`
- **First Login:** Requires password change
- **Password Requirements:** 8-16 chars, letters + numbers, case-sensitive

### Denon AVR-X6700H Network Control
- **Port:** 23 (Telnet)
- **Power Query:** `PW?` → `PWON` or `PWSTANDBY`
- **Power Control:** `PWON`, `PWSTANDBY`
- **Protocol:** ASCII text, commands end with `\r`
- **No Authentication:** Required by default

---

## Configuration Values Discovered

### Projector Settings
- **MAC Address:** F8-4E-17-B8-E0-9E (example - use your actual)
- **IP Address:** 192.168.50.182 (example - use your actual)
- **ADCP Port:** 53595
- **HTTP Port:** 80
- **HTTP Username:** root
- **HTTP Password:** admin123 (changed from default "Projector")

### Required Projector Settings
1. **Network Management:** Menu > Setup > Network Management > On
2. **Remote Start:** Menu > Setup > Remote Start > On
3. **ADCP Service:** Advanced Settings > ADCP > Start ADCP Service > On

---

## Lessons Learned

1. **CEC Not Available:** Sony XW5000 doesn't support CEC - network control is the way to go
2. **Command Format Matters:** ADCP uses `power "on"` not `POWR 1`
3. **Initial Messages:** `NOKEY` is informational, not an error
4. **HTTP Access:** Chrome needs proxy for Digest auth, or use Firefox
5. **Network Polling:** Not "archaic" - it's standard for device monitoring
6. **Security:** Always use templates and environment variables for sensitive data

---

## Next Steps

1. **Test Denon Network Control:**
   - Find Denon AVR IP address
   - Test with `test_denon.py`
   - Verify telnet commands work

2. **Implement Network Monitor (Alternative to GPIO):**
   - Create `denon_monitor.py` based on `gpio_monitor.py`
   - Use telnet polling with adaptive intervals
   - Replace GPIO monitor in main service

3. **Production Deployment:**
   - Set up on Raspberry Pi
   - Configure `config.yaml` with actual values
   - Test end-to-end trigger functionality

---

## Command Reference

### Test Projector
```bash
python3 test_projector.py on --ip 192.168.50.182
python3 test_projector.py off --ip 192.168.50.182
python3 test_projector.py scan --ip 192.168.50.182
```

### Test HTTP Access
```bash
export PROJECTOR_PASSWORD="your_password"
python3 proxy_auth.py
# Then visit http://localhost:8888/ in Chrome
```

### Test Denon
```bash
python3 test_denon.py test --ip <denon_ip>
python3 test_denon.py query --ip <denon_ip>
python3 test_denon.py monitor --ip <denon_ip>
```

---

## Resources

- Sony XW5000 Manual: https://helpguide.sony.net/vpl/xw5000/v1/en/
- Denon AVR-X6700H Manual: https://manuals.denon.com/AVRX6700H/NA/EN/
- ADCP Protocol: Discovered through testing (no official public docs found)

---

*This document captures the key discoveries and decisions made during the projector control setup session.*

