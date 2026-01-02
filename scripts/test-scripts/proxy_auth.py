#!/usr/bin/env python3
"""Simple HTTP proxy to handle Digest authentication for Chrome.

IMPORTANT NOTES:
- Default credentials are for the PROJECTOR's HTTP web interface (port 80)
- The projector uses HTTP Digest authentication (non-standard, not Basic auth)
- Default credentials: username="root", password="Projector" (capital P)
- Password MUST be changed on first login (enforced by projector)
- After first login, you must use the new password you set
- Chrome doesn't handle Digest auth well, so this proxy is needed
- If password is forgotten, perform "All Reset" on projector to restore defaults
"""

import http.server
import socketserver
import requests
from requests.auth import HTTPDigestAuth
import urllib.parse
import os
import sys
from pathlib import Path

# Load .env file if available
try:
    from dotenv import load_dotenv
    # Try to load .env from project root or current directory
    env_paths = [
        Path(__file__).parent.parent.parent / ".env",
        Path.cwd() / ".env",
        Path.home() / ".config" / "projector-trigger" / ".env",
    ]
    for env_path in env_paths:
        if env_path.exists():
            load_dotenv(env_path)
            break
    else:
        # Try current directory as fallback
        load_dotenv()
except ImportError:
    # python-dotenv not installed, skip .env loading
    pass

# Try to import Config class, fallback to direct YAML loading
try:
    # Try relative import first (if running from project root)
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from projector_trigger.config import Config
    from projector_trigger.network_discovery import discover_projector_ip
    USE_CONFIG_CLASS = True
except ImportError:
    # Fallback: load YAML directly
    USE_CONFIG_CLASS = False


def load_config(config_path=None):
    """Load configuration from config.yaml.
    
    Returns dict with projector settings, or None if config not found.
    """
    if USE_CONFIG_CLASS:
        try:
            config = Config(config_path)
            # Discover projector IP if MAC is configured
            projector_ip = discover_projector_ip(
                mac_address=config.projector_mac,
                ip_address=config.projector_ip
            )
            return {
                'ip': projector_ip or config.projector_ip or "192.168.1.100",
                'http_username': config._config.get('projector_http', {}).get('username', 'root'),
                'http_port': config._config.get('projector_http', {}).get('port', 80),
            }
        except Exception as e:
            print(f"Note: Could not load config using Config class: {e}")
    
    # Fallback: direct YAML loading
    if config_path is None:
        # Try standard locations
        for path in [
            Path(__file__).parent.parent.parent / "config.yaml",
            Path.home() / ".config" / "projector-trigger" / "config.yaml",
            Path("/opt/projector-trigger/config.yaml"),
        ]:
            if path.exists():
                config_path = path
                break
    
    if config_path and Path(config_path).exists():
        try:
            import yaml
            with open(config_path) as f:
                config = yaml.safe_load(f) or {}
            projector = config.get("projector", {})
            projector_http = config.get("projector_http", {})
            
            # Get IP (prefer direct IP, otherwise use placeholder)
            ip = projector.get("ip") or "192.168.1.100"
            
            return {
                'ip': ip,
                'http_username': projector_http.get('username', 'root'),
                'http_port': projector_http.get('port', 80),
            }
        except Exception as e:
            print(f"Note: Could not load config.yaml: {e}")
    
    return None


def create_proxy_handler(projector_ip, projector_port, username, password):
    """Create a ProxyHandler class with the specified configuration.
    
    This factory function creates a handler class with the config values
    bound via closure, allowing the handler to use config values.
    """
    class ProxyHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            """Handle GET requests."""
            # Build full URL
            url = f"http://{projector_ip}:{projector_port}{self.path}"
            
            try:
                # Make authenticated request to projector
                auth = HTTPDigestAuth(username, password)
                response = requests.get(url, auth=auth, verify=False, timeout=5)
                
                # Send response to browser
                self.send_response(response.status_code)
                
                # Copy headers (except some that shouldn't be forwarded)
                skip_headers = {'content-encoding', 'transfer-encoding', 'connection'}
                for key, value in response.headers.items():
                    if key.lower() not in skip_headers:
                        self.send_header(key, value)
                
                self.end_headers()
                self.wfile.write(response.content)
                
            except Exception as e:
                self.send_error(500, f"Proxy error: {e}")
        
        def do_POST(self):
            """Handle POST requests."""
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else b''
            
            # Build full URL
            url = f"http://{projector_ip}:{projector_port}{self.path}"
            
            try:
                # Make authenticated request to projector
                auth = HTTPDigestAuth(username, password)
                response = requests.post(
                    url, 
                    data=body,
                    headers={k: v for k, v in self.headers.items() if k.lower() not in ['host', 'connection']},
                    auth=auth, 
                    verify=False, 
                    timeout=5
                )
                
                # Send response to browser
                self.send_response(response.status_code)
                for key, value in response.headers.items():
                    if key.lower() not in {'content-encoding', 'transfer-encoding', 'connection'}:
                        self.send_header(key, value)
                self.end_headers()
                self.wfile.write(response.content)
                
            except Exception as e:
                self.send_error(500, f"Proxy error: {e}")
        
        def log_message(self, format, *args):
            """Suppress default logging."""
            pass
    
    return ProxyHandler


def main(projector_ip, projector_port, username, password, proxy_port, config_loaded=False):
    """Start the proxy server with the given configuration."""
    if not password:
        print("ERROR: Password not provided")
        print("Set it via:")
        print("  - Environment variable: export PROJECTOR_PASSWORD='your_password'")
        print("  - Command-line: --password 'your_password'")
        print("\nNote: Password is not stored in config.yaml for security.")
        sys.exit(1)
    
    print(f"Starting proxy server on port {proxy_port}")
    print(f"Projector: http://{projector_ip}:{projector_port}")
    print(f"Username: {username}")
    if config_loaded:
        print(f"(Loaded from config.yaml)")
    print(f"\nTo use:")
    print(f"1. Configure Chrome to use proxy: localhost:{proxy_port}")
    print(f"   OR use a proxy extension like 'Proxy SwitchyOmega'")
    print(f"2. Visit: http://{projector_ip}/")
    print(f"\nOr use this simpler method:")
    print(f"   Visit: http://localhost:{proxy_port}/")
    print(f"   (This will proxy to the projector)")
    print(f"\nPress Ctrl+C to stop\n")
    
    # Create handler class with config values
    ProxyHandler = create_proxy_handler(projector_ip, projector_port, username, password)
    
    with socketserver.TCPServer(("", proxy_port), ProxyHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down proxy...")


if __name__ == "__main__":
    import argparse
    
    # Load config first (for defaults in help text)
    _config = load_config()
    
    # Get defaults from config, env, or hardcoded
    default_ip = (
        _config['ip'] if _config and _config.get('ip')
        else os.getenv("PROJECTOR_IP", "192.168.1.100")
    )
    default_port = (
        _config['http_port'] if _config and _config.get('http_port')
        else int(os.getenv("PROJECTOR_PORT", "80"))
    )
    default_username = (
        _config['http_username'] if _config and _config.get('http_username')
        else os.getenv("PROJECTOR_USERNAME", "root")
    )
    default_password = os.getenv("PROJECTOR_PASSWORD", "")
    default_proxy_port = int(os.getenv("PROXY_PORT", "8888"))
    
    parser = argparse.ArgumentParser(
        description="HTTP proxy for Sony projector with Digest auth",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Configuration Priority (highest to lowest):
  1. Command-line arguments
  2. Environment variables
  3. config.yaml file
  4. Defaults

Security Note:
  Password is never read from config.yaml for security.
  Use PROJECTOR_PASSWORD environment variable or --password argument.
        """
    )
    parser.add_argument(
        "--config",
        help="Path to config.yaml (default: auto-detect)"
    )
    parser.add_argument(
        "--ip",
        default=default_ip,
        help=f"Projector IP (default: from config or {default_ip})"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=default_port,
        help=f"HTTP port (default: from config or {default_port})"
    )
    parser.add_argument(
        "--proxy-port",
        type=int,
        default=default_proxy_port,
        help=f"Proxy port (default: {default_proxy_port})"
    )
    parser.add_argument(
        "--username",
        default=default_username,
        help=f"HTTP username (default: from config or {default_username})"
    )
    parser.add_argument(
        "--password",
        default=default_password,
        help="HTTP password (required if PROJECTOR_PASSWORD not set)"
    )
    
    args = parser.parse_args()
    
    # Reload config if custom path provided
    config_loaded = False
    if args.config:
        _config = load_config(args.config)
        config_loaded = _config is not None
    elif _config:
        config_loaded = True
    
    # Override with command-line arguments (they already have defaults)
    projector_ip = args.ip
    projector_port = args.port
    username = args.username
    password = args.password
    proxy_port = args.proxy_port
    
    # If config was loaded and args weren't explicitly set, use config values
    if _config and not args.config:  # Only if we auto-loaded config
        if not args.ip or args.ip == default_ip:
            projector_ip = _config.get('ip', projector_ip)
        if not args.port or args.port == default_port:
            projector_port = _config.get('http_port', projector_port)
        if not args.username or args.username == default_username:
            username = _config.get('http_username', username)
    
    main(projector_ip, projector_port, username, password, proxy_port, config_loaded)

