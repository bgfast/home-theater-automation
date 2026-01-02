# Cursor AI Project Prompt: Denon 12V Trigger → Raspberry Pi → Sony VPL-XW5000 IP Power Control

Copy/paste the prompt below into Cursor to start the project.

---

## Prompt to paste into Cursor

You are a senior embedded + Linux automation engineer.

Build a Raspberry Pi project that:

1) Reads a Denon AVR 12V trigger via an optocoupler input module (PC817). The optocoupler output is connected to Raspberry Pi GPIO17 and GND.
   - The input is ACTIVE-LOW at the GPIO (trigger ON pulls GPIO LOW).
   - Use internal pull-up on the GPIO.
   - Debounce/validate state changes (e.g., require stable level for 250–500 ms).

2) Sends IP control commands to a Sony VPL-XW5000 projector over the network when the trigger changes state.
   - On trigger ON (GPIO LOW): send PROJECTOR POWER ON.
   - On trigger OFF (GPIO HIGH): send PROJECTOR POWER OFF.
   - Implement the network send as TCP to the projector IP and configurable port.
   - Commands should be configurable in a config file (YAML or JSON) as plain strings (default: "POWR 1" and "POWR 0").
   - Add retries and timeouts:
     - Timeout per attempt: 1.5s
     - Retries: 3
     - Backoff: 0.5s increasing.

3) Runs as a systemd service on boot.
   - Provide a systemd unit file.
   - Provide an install script that:
     - Installs dependencies
     - Copies code into /opt/projector-trigger
     - Installs and enables the systemd service
     - Logs to journald
   - Service should restart on failure.

4) Provide a CLI for manual testing:
   - `python -m projector_trigger status` (shows GPIO state and last action)
   - `python -m projector_trigger on` (send power on)
   - `python -m projector_trigger off` (send power off)
   - `python -m projector_trigger monitor` (runs foreground and prints events)

5) Provide robust logging and clear error messages.

Deliverables in the repo:
- README.md with wiring diagram, configuration, and step-by-step setup
- `projector_trigger/` Python package
- `config.yaml` example
- `scripts/install.sh`
- `systemd/projector-trigger.service`

Constraints:
- Use Python 3.
- Prefer `gpiozero` or `RPi.GPIO` for GPIO; choose the simplest.
- Use only standard library for TCP sockets (unless strongly justified).
- Make the projector IP, port, GPIO pin, debounce interval configurable.
- Code must be clean, production-ready, and easy to modify.

Also include a section in README for troubleshooting:
- GPIO reads inverted
- No network route to projector
- Projector not waking (Remote Start / Power Saving settings)

---

## Suggested Repo Name

projector-trigger-bridge

---

# Clean Raspberry Pi Setup (New SD Card)

This section is for installing a clean OS and getting ready to run the service.

## What to install
Use Raspberry Pi OS Lite (64-bit). It is stable and perfect for a headless service.

## Install steps

1) Download Raspberry Pi Imager on your Mac/PC.
2) Insert the new SD card.
3) In Raspberry Pi Imager:
   - Choose Device: your Raspberry Pi (e.g., Pi Zero 2 W)
   - Choose OS: Raspberry Pi OS Lite (64-bit)
   - Choose Storage: your SD card
4) Click the gear icon (Advanced Options) and set:
   - Hostname: projector-bridge
   - Enable SSH: ON (password auth is fine)
   - Set username/password (write these down)
   - Configure Wi‑Fi: SSID + password (if using Wi‑Fi)
   - Set locale/timezone
5) Write the image to the SD card.
6) Put SD card in the Pi and power it up.

## First login
Find the Pi’s IP address:
- Check your router’s DHCP leases
- Or use a network scanner app

SSH in:
- `ssh <username>@<pi_ip>`

## Update the system
Run:
- `sudo apt-get update`
- `sudo apt-get -y upgrade`

## Install basics
Run:
- `sudo apt-get -y install git python3 python3-venv`

## Clone your repo
- `git clone <your_repo_url>`
- `cd projector-trigger-bridge`

## Run the installer
- `bash scripts/install.sh`

## View logs
- `journalctl -u projector-trigger -f`

---

# Wiring Summary (PC817 Optocoupler Module)

Denon Trigger:
- Tip = +12V
- Sleeve = GND

Optocoupler INPUT:
- IN+  ← Denon +12V
- IN-  ← Denon GND

Optocoupler OUTPUT to Pi:
- OUT → GPIO17
- GND → Pi GND
- VCC → Pi 3.3V (only if your specific module requires it; otherwise leave unconnected and use pull-up)

In software:
- Use pull-up
- Treat GPIO LOW as trigger ON

---

# Notes

- This project intentionally avoids HDMI-CEC and IR.
- Denon trigger is authoritative; projector is controlled via IP.
