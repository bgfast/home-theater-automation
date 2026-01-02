# Raspberry Pi Deployment Files

This directory contains all files that need to be copied to the Raspberry Pi for installation.

## Contents

- `projector_trigger/` - Python package (main application code)
- `systemd/` - Systemd service files
- `requirements.txt` - Python dependencies
- `config.yaml.template` - Configuration template

## Installation

These files are automatically installed by the `scripts/install.sh` script, which:
1. Copies files to `/opt/projector-trigger/`
2. Installs Python dependencies
3. Sets up the systemd service
4. Creates configuration from template

## Manual Installation

If installing manually:

```bash
# Copy files to Raspberry Pi
scp -r raspberry-pi-deploy/* pi@<pi_ip>:/tmp/projector-trigger/

# SSH into Pi
ssh pi@<pi_ip>

# Move to installation directory
sudo mkdir -p /opt/projector-trigger
sudo mv /tmp/projector-trigger/* /opt/projector-trigger/

# Install dependencies
cd /opt/projector-trigger
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Copy and enable systemd service
sudo cp systemd/projector-trigger.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable projector-trigger

# Create config from template
sudo cp config.yaml.template config.yaml
sudo nano config.yaml  # Edit with your values

# Start service
sudo systemctl start projector-trigger
```

## File Structure on Raspberry Pi

```
/opt/projector-trigger/
├── projector_trigger/     # Python package
├── systemd/               # Service files
├── config.yaml            # Configuration (created from template)
├── config.yaml.template   # Template
└── requirements.txt       # Dependencies
```

