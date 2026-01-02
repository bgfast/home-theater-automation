# Denon AVR-X6700H Manuals and Documentation

## Official Product Manuals

### Owner's Manual (Online)
**URL:** https://manuals.denon.com/AVRX6700H/NA/EN/

Comprehensive guide covering:
- Setup and connections
- Operation and features
- Settings and configuration
- Troubleshooting

### Owner's Manual (PDF Download)
**URL:** https://www.denon.com/en-us/product/archive-av-receivers/avr-x6700h/300005.html

Downloadable PDF version for offline reference.

### Quick Start Guide
**URL:** https://assets.denon.com/documentmaster/nl/avr-x6700he3_eng_quickstartguide_im_v00.pdf

Quick setup instructions to get started.

### Product Information Sheet
**URL:** https://www.denon.com/on/demandware.static/-/Library-Sites-denon_northamerica_shared/default/dwef9b9886/downloads/avr-x6700h-info-sheet-en.pdf

Features and specifications overview.

## Network Control Documentation

### Protocol Manual / IP Control Guide

**Note:** Denon typically provides protocol documentation separately. Look for:
- "IP Control Protocol Manual"
- "Network Control Protocol"
- "Denon Control Protocol (DCP)"
- "Telnet Control Commands"

**Where to find:**
1. Check the Denon support page for your model
2. Look for "Technical Documentation" or "Protocol Manual" sections
3. May be in a separate "Installation" or "Custom Installer" section

### Common Denon Network Control Information

**Default Port:** 23 (Telnet)

**Common Commands:**
- Power Query: `PW?` → Returns `PWON` or `PWSTANDBY`
- Power On: `PWON`
- Power Off: `PWSTANDBY`
- Volume Query: `MV?`
- Input Query: `SI?`

**Protocol Format:**
- Commands end with `\r` (carriage return)
- Responses are ASCII text
- No authentication required by default

## Additional Resources

### Denon Support Page
**URL:** https://www.denon.com/en-us/product/archive-av-receivers/avr-x6700h/300005.html

Main product page with links to all documentation.

### ManualsLib
**URL:** https://www.manualslib.com/manual/2563734/Denon-Avr-X6700h.html

Alternative source for manuals (may include user-uploaded versions).

## Finding Protocol Documentation

If the protocol manual isn't easily found:

1. **Check the Owner's Manual:**
   - Look for "Network Control" or "IP Control" sections
   - May be in "Advanced Setup" or "Custom Installer" sections

2. **Contact Denon Support:**
   - Request the "IP Control Protocol Manual" or "Custom Installer Guide"
   - These are often available but may require registration

3. **Community Resources:**
   - Home Assistant Denon integration documentation
   - GitHub repositories for Denon control libraries
   - AVS Forum or other AV enthusiast forums

## Testing Network Control

Use the provided `test_denon.py` script to test your AVR's network interface:

```bash
# Test connection
python3 test_denon.py test --ip <denon_ip>

# Query power state
python3 test_denon.py query --ip <denon_ip>

# Test commands
python3 test_denon.py commands --ip <denon_ip>

# Monitor continuously
python3 test_denon.py monitor --ip <denon_ip>
```

