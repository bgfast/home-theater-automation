#!/usr/bin/env python3
"""Simple HTTP connection to Sony projector web interface.

IMPORTANT NOTES:
- Default credentials are for the PROJECTOR's HTTP web interface (port 80)
- The projector uses HTTP Digest authentication (non-standard, not Basic auth)
- Default credentials: username="root", password="Projector" (capital P)
- Password MUST be changed on first login (enforced by projector)
- After first login, you must use the new password you set
- If password is forgotten, perform "All Reset" on projector to restore defaults
"""

import requests
from requests.auth import HTTPDigestAuth
import sys
import os
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

# Default credentials from manual (can be overridden via .env file or environment variables)
# NOTE: These are the factory defaults. If password was changed, use the new password.
USERNAME = os.getenv("PROJECTOR_USERNAME", "root")
PASSWORD = os.getenv("PROJECTOR_PASSWORD", "Projector")  # Default from manual - must be changed on first use

def connect(ip: str, port: int = 80, username: str = USERNAME, password: str = PASSWORD):
    """Connect to projector HTTP interface."""
    url = f"http://{ip}:{port}/"
    
    print(f"Connecting to {url}")
    print(f"Username: {username}")
    print(f"Password: {'*' * len(password)}")
    print("-" * 60)
    
    try:
        # Use Digest authentication (Sony projectors use Digest, not Basic auth)
        # This is non-standard - most browsers don't handle Digest well
        auth = HTTPDigestAuth(username, password)
        response = requests.get(url, auth=auth, timeout=5, verify=False)
        
        print(f"Status Code: {response.status_code}")
        print(f"Status: {'✓ SUCCESS' if response.status_code == 200 else '✗ FAILED'}")
        print("-" * 60)
        
        if response.status_code == 200:
            print(f"\nResponse Headers:")
            for key, value in response.headers.items():
                print(f"  {key}: {value}")
            
            print(f"\nResponse Body (first 500 chars):")
            print(response.text[:500])
            
            return True
        else:
            print(f"Error: {response.status_code}")
            print(response.text[:200])
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Connection error: {e}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Connect to Sony projector HTTP interface")
    parser.add_argument("--ip", required=True, help="Projector IP address")
    parser.add_argument("--port", type=int, default=80, help="HTTP port (default: 80)")
    parser.add_argument("--username", default=USERNAME, help=f"Username (default: {USERNAME})")
    parser.add_argument("--password", default=PASSWORD, help=f"Password (default: {PASSWORD})")
    
    args = parser.parse_args()
    
    success = connect(args.ip, args.port, args.username, args.password)
    sys.exit(0 if success else 1)

