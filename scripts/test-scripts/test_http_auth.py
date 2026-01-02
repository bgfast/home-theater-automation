#!/usr/bin/env python3
"""Test common default credentials for Sony projector HTTP interface.

IMPORTANT NOTES:
- Default credentials are for the PROJECTOR's HTTP web interface (port 80)
- The projector uses HTTP Digest authentication (non-standard, not Basic auth)
- Default credentials: username="root", password="Projector" (capital P)
- Password MUST be changed on first login (enforced by projector)
- After first login, the default password will no longer work
- If password is forgotten, perform "All Reset" on projector to restore defaults
"""

import requests
from requests.auth import HTTPDigestAuth
import sys
import time
from urllib3.exceptions import InsecureRequestWarning
import warnings

# Suppress SSL warnings for testing
warnings.filterwarnings('ignore', category=InsecureRequestWarning)

# Common default credentials for Sony projectors
COMMON_CREDENTIALS = [
    # Common defaults
    ("admin", "admin"),
    ("admin", ""),
    ("admin", "password"),
    ("admin", "1234"),
    ("admin", "0000"),
    ("admin", "admin123"),
    ("admin", "sony"),
    ("admin", "Sony"),
    ("admin", "SONY"),
    
    # Sony-specific
    ("sony", "sony"),
    ("sony", "admin"),
    ("sony", ""),
    ("user", "user"),
    ("user", ""),
    ("root", "root"),
    ("root", ""),
    
    # Empty combinations
    ("", ""),
    ("", "admin"),
    
    # Numeric
    ("admin", "12345"),
    ("admin", "1111"),
    ("admin", "2222"),
    ("admin", "8888"),
    
    # Projector model specific
    ("admin", "xw5000"),
    ("admin", "XW5000"),
    ("admin", "vpl"),
    ("admin", "VPL"),
    
    # Sony XW5000 default (from manual - after factory reset)
    ("root", "Projector"),
    ("root", "projector"),
    ("root", "PROJECTOR"),
]


def test_credentials(ip: str, port: int = 80, timeout: float = 3.0):
    """Test common credentials against the HTTP interface.
    
    Args:
        ip: Projector IP address
        port: HTTP port (default 80)
        timeout: Request timeout in seconds
    """
    url = f"http://{ip}:{port}/"
    
    print(f"\n{'='*60}")
    print(f"Testing HTTP Authentication")
    print(f"{'='*60}")
    print(f"Target: {url}")
    print(f"Testing {len(COMMON_CREDENTIALS)} credential combinations...")
    print(f"{'='*60}\n")
    
    session = requests.Session()
    session.timeout = timeout
    
    for i, (username, password) in enumerate(COMMON_CREDENTIALS, 1):
        try:
            # Try Digest authentication (most common for Sony projectors)
            auth = HTTPDigestAuth(username, password)
            response = session.get(url, auth=auth, timeout=timeout, verify=False)
            
            status = response.status_code
            if status == 200:
                print(f"✓ SUCCESS! Credentials found:")
                print(f"  Username: {username!r}")
                print(f"  Password: {password!r}")
                print(f"  Status: {status}")
                print(f"\nResponse preview:")
                print(f"  {response.text[:200]}...")
                return (username, password)
            elif status == 401:
                # Still unauthorized, try next
                print(f"  [{i:2d}/{len(COMMON_CREDENTIALS)}] {username!r} / {password!r} - Failed (401)")
            else:
                print(f"  [{i:2d}/{len(COMMON_CREDENTIALS)}] {username!r} / {password!r} - Status {status}")
                
        except requests.exceptions.Timeout:
            print(f"  [{i:2d}/{len(COMMON_CREDENTIALS)}] {username!r} / {password!r} - Timeout")
        except requests.exceptions.RequestException as e:
            print(f"  [{i:2d}/{len(COMMON_CREDENTIALS)}] {username!r} / {password!r} - Error: {e}")
        
        # Small delay to avoid overwhelming the device
        time.sleep(0.2)
    
    print(f"\n{'='*60}")
    print("No valid credentials found in common defaults.")
    print(f"{'='*60}")
    print("\nIMPORTANT INFORMATION:")
    print("The Sony XW5000 projector HTTP interface:")
    print("- Uses HTTP Digest authentication (not Basic auth)")
    print("- Default credentials: root / Projector (capital P)")
    print("- Password MUST be changed on first login")
    print("- After password change, default password no longer works")
    print("\nIf password was changed and forgotten:")
    print("1. Perform 'All Reset' on projector (Menu > Setup > All Reset)")
    print("2. This restores default password: root / Projector")
    print("3. You will be prompted to change it again on first login")
    print(f"{'='*60}\n")
    
    return None


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Test common default credentials for Sony projector HTTP interface"
    )
    parser.add_argument(
        "--ip",
        required=True,
        help="Projector IP address"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=80,
        help="HTTP port (default: 80)"
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=3.0,
        help="Request timeout in seconds (default: 3.0)"
    )
    
    args = parser.parse_args()
    
    try:
        result = test_credentials(args.ip, args.port, args.timeout)
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

