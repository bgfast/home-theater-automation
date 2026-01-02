# Source Control Guidelines

## Files to EXCLUDE from Git (in .gitignore)

### Configuration Files with Sensitive Data
- ✅ `config.yaml` - Contains MAC addresses and IP addresses
- ✅ `*.local.yaml` - Local configuration overrides
- ✅ `*.secret.yaml` - Secret configuration files
- ✅ `proxy_auth.local.py` - Local proxy config with passwords

### Generated/Downloaded Files
- ✅ `downloads/*.img` - Downloaded OS images
- ✅ `downloads/*.zip` - Downloaded archives
- ✅ `*.tar.gz` - Archive files
- ✅ `print.pdf` - May contain sensitive info

### Development Files
- ✅ `__pycache__/` - Python cache
- ✅ `*.pyc`, `*.pyo` - Compiled Python
- ✅ `.DS_Store` - macOS files
- ✅ `*.swp`, `*.swo` - Editor temp files
- ✅ `.vscode/`, `.idea/` - IDE configs
- ✅ `venv/`, `.venv/`, `env/` - Virtual environments
- ✅ `*.log` - Log files

### Security Files
- ✅ `*.pem`, `*.key` - Private keys
- ✅ `id_rsa`, `id_rsa.pub` - SSH keys
- ✅ `.env`, `.env.local` - Environment files

## Files to INCLUDE in Git

### Templates
- ✅ `config.yaml.template` - Safe template with placeholders
- ✅ All `.template` files

### Source Code
- ✅ All Python source files (`.py`)
- ✅ All shell scripts (`.sh`)
- ✅ `requirements.txt` - Python dependencies
- ✅ `systemd/*.service` - Service files

### Documentation
- ✅ `README.md` - Main documentation
- ✅ `README_CONFIG.md` - Configuration guide
- ✅ `*.md` - All markdown documentation
- ✅ `denon_manuals.md` - Manual references
- ✅ `network_trigger_approach.md` - Planning docs

### Project Structure
- ✅ `projector_trigger/` - Python package
- ✅ `scripts/` - Installation scripts
- ✅ `.gitignore` - Git ignore rules

## Sensitive Data Handling

### MAC Addresses
- ❌ **Never commit** actual MAC addresses
- ✅ Use `XX-XX-XX-XX-XX-XX` in templates
- ✅ Store real MAC in `config.yaml` (gitignored)

### IP Addresses
- ❌ **Never commit** actual IP addresses in config files
- ✅ Use placeholder IPs like `192.168.1.100` in templates
- ✅ Store real IPs in `config.yaml` (gitignored)
- ✅ Test scripts can accept IPs as command-line args

### Passwords
- ❌ **Never commit** passwords in code or config
- ✅ Use environment variables: `PROJECTOR_PASSWORD`
- ✅ Use command-line arguments for test scripts
- ✅ Store in `config.yaml` (gitignored) if needed

### Usernames
- ✅ Default usernames like "root" are OK (documented defaults)
- ❌ Don't commit custom usernames in config files

## Quick Reference

### Before Committing
```bash
# Check what will be committed
git status

# Verify no sensitive data
grep -r "192.168.50" . --exclude-dir=.git
grep -r "F8-4E-17" . --exclude-dir=.git
grep -r "admin123" . --exclude-dir=.git
```

### Setup for New Clone
```bash
# 1. Copy template
cp config.yaml.template config.yaml

# 2. Edit with your values
nano config.yaml

# 3. Set environment variables (optional)
export PROJECTOR_PASSWORD="your_password"
```

## Current Status

✅ `.gitignore` created
✅ `config.yaml.template` created
✅ Hardcoded passwords removed from source files
✅ Environment variable support added
✅ Documentation created

