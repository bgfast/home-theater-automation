# Configuration Setup

## Initial Setup

1. **Copy the template files:**
   ```bash
   cp config.yaml.template config.yaml
   cp .env.template .env
   ```

2. **Edit `config.yaml` with your values:**
   - Set your projector's MAC address or IP
   - Set your Denon AVR's MAC address or IP
   - Adjust other settings as needed

3. **Edit `.env` with your sensitive values:**
   - Set `PROJECTOR_PASSWORD` (required for HTTP interface access)
   - Optionally override other settings
   - **Note**: `.env` file is gitignored and will not be committed

## Environment Variables (.env file)

**Best Practice**: Store sensitive data (like passwords) in a `.env` file rather than setting environment variables manually.

1. **Copy the template:**
   ```bash
   cp .env.template .env
   ```

2. **Edit `.env` with your passwords:**
   ```bash
   PROJECTOR_PASSWORD=your_actual_password_here
   RASPBERRY_PI_IP=192.168.50.110
   RASPBERRY_PI_USER=admin
   RASPBERRY_PI_PASSWORD=admin
   ```

3. **Scripts automatically load `.env` file** from:
   - Project root directory
   - Current working directory
   - `~/.config/projector-trigger/.env`

**Note**: The `.env` file is gitignored and will never be committed to source control.

## Environment Variables for Test Scripts

Test scripts automatically load `.env` file. You can also use environment variables or command-line arguments:

### Projector HTTP Proxy (`proxy_auth.py`)

**IMPORTANT**: The projector's HTTP interface uses Digest authentication (not Basic auth).

**Best Practice**: The script now reads IP address and username from `config.yaml`. Password is still required via environment variable or command-line argument (for security).

**Using config.yaml and .env (recommended):**
```bash
# 1. Create .env file with password
echo "PROJECTOR_PASSWORD=your_password_here" > .env

# 2. Run script (IP and username come from config.yaml, password from .env)
python3 scripts/test-scripts/proxy_auth.py
```

**Or use environment variable:**
```bash
export PROJECTOR_PASSWORD="your_password_here"
python3 scripts/test-scripts/proxy_auth.py
```

**Override with command-line:**
```bash
python3 scripts/test-scripts/proxy_auth.py \
  --ip 192.168.1.100 \
  --username root \
  --password "your_password_here"
```

**Using environment variables (alternative):**
```bash
export PROJECTOR_IP="192.168.1.100"
export PROJECTOR_USERNAME="root"
export PROJECTOR_PASSWORD="your_password_here"
export PROXY_PORT="8888"
python3 scripts/test-scripts/proxy_auth.py
```

**Note**: 
- Default password is `Projector` (capital P) but MUST be changed on first login
- Password is never stored in config.yaml for security (use env var or --password)
- Configuration priority: command-line > environment > config.yaml > defaults

### Projector HTTP Connection (`http_connect.py`)

**IMPORTANT**: The projector's HTTP interface uses Digest authentication (not Basic auth).

**Using .env file (recommended):**
```bash
# Create .env file with password
echo "PROJECTOR_PASSWORD=your_password_here" > .env

# Run script (password loaded from .env)
python3 scripts/test-scripts/http_connect.py --ip 192.168.1.100
```

**Or use environment variable:**
```bash
export PROJECTOR_PASSWORD="your_password_here"
python3 scripts/test-scripts/http_connect.py --ip 192.168.1.100
```

**Note**: Default password is `Projector` (capital P) but MUST be changed on first login. After that, use your new password.

### Projector Web Script (`open_projector_web.sh`)

**Using .env file (recommended):**
```bash
# Create .env file
echo "PROJECTOR_PASSWORD=your_password_here" > .env

# Run script (automatically loads .env)
./scripts/test-scripts/open_projector_web.sh
```

**Or use environment variables:**
```bash
export PROJECTOR_IP="192.168.1.100"
export PROJECTOR_USERNAME="root"
export PROJECTOR_PASSWORD="your_password_here"

./scripts/test-scripts/open_projector_web.sh
```

## Projector HTTP Interface Authentication

**Important Information:**
- The projector's HTTP web interface (port 80) uses **HTTP Digest authentication** (non-standard, not Basic auth)
- **Default credentials**: `root` / `Projector` (capital P)
- **Password change required**: The password MUST be changed on first login (enforced by projector)
- **After first login**: The default password will no longer work - you must use the new password you set
- **Password requirements**: 8-16 characters, must include both letters and numbers, case-sensitive
- **If password forgotten**: Perform "All Reset" on projector (Menu > Setup > All Reset) to restore defaults

**Note**: The HTTP interface is for configuration only. Power control uses the ADCP protocol on port 53595, which does not require HTTP authentication.

## Security Notes

- **Never commit `config.yaml`** - it contains MAC addresses and potentially IP addresses
- **Never commit `.env`** - it contains passwords and sensitive data
- **Use `.env` file for passwords** - it's gitignored and automatically loaded by scripts
- **Default passwords are temporary** - they must be changed on first use
- The `.gitignore` file is configured to exclude sensitive files
- Template files (`.template`) are safe to commit

## Configuration Priority

For all scripts, configuration is loaded in this order (highest to lowest priority):

1. **Command-line arguments** (highest priority)
2. **Environment variables** (set via `export` or `.env` file)
3. **config.yaml file** (for non-sensitive settings like IP, username, ports)
4. **Defaults** (lowest priority)

**Important**: Passwords are never read from `config.yaml` for security. They must be provided via:
- `.env` file (recommended)
- Environment variable (`PROJECTOR_PASSWORD`)
- Command-line argument (`--password`)

## Files Excluded from Git

- `config.yaml` - Contains MAC addresses and IPs
- `*.local.yaml` - Local configuration overrides
- `*.secret.yaml` - Secret configuration files
- `proxy_auth.local.py` - Local proxy configuration with passwords
- `*.log` - Log files
- `downloads/*.img` - Downloaded OS images

## Files Safe to Commit

- `config.yaml.template` - Template with placeholder values
- All Python source files (they use environment variables or config files)
- Documentation files
- Scripts (they accept parameters or use environment variables)

