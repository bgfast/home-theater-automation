#!/usr/bin/env python3
"""Test script to send TCP/IP commands to Sony XW5000 projector."""

import socket
import sys
import argparse
from pathlib import Path

# Default values (from config.yaml)
DEFAULT_PORT = 53595
DEFAULT_POWER_ON_CMD = 'power "on"'
DEFAULT_POWER_OFF_CMD = 'power "off"'
DEFAULT_TIMEOUT = 1.5

# Legacy format commands (for reference - may not work)
LEGACY_POWER_ON_CMD = "POWR 1"
LEGACY_POWER_OFF_CMD = "POWR 0"
ADCP_POWER_ON_CMD = "POWR0001"
ADCP_POWER_OFF_CMD = "POWR0000"


def check_port(ip: str, port: int, timeout: float = 2.0) -> bool:
    """Check if a port is open.
    
    Returns:
        True if port is open, False otherwise
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except Exception:
        return False


def send_command(ip: str, port: int, command: str, timeout: float = DEFAULT_TIMEOUT) -> bool:
    """Send a TCP command to the projector.
    
    Args:
        ip: Projector IP address
        port: TCP port
        command: Command string to send
        timeout: Connection timeout in seconds
        
    Returns:
        True if successful, False otherwise
    """
    # First check if port is open
    print(f"Checking if port {port} is open...")
    if not check_port(ip, port, timeout):
        print(f"✗ Port {port} is not open (connection refused)")
        print("\n" + "="*60)
        print("TROUBLESHOOTING:")
        print("="*60)
        print("The projector's ADCP network control service is not responding.")
        print("\nREQUIRED SETTINGS (both must be enabled):")
        print("1. Network Management must be enabled")
        print("   → Go to: Menu > Setup > Network Management > On")
        print("\n2. Remote Start must be enabled")
        print("   → Go to: Menu > Setup > Remote Start > On")
        print("\nOther possible causes:")
        print("3. Projector is in deep standby/power saving mode")
        print("   → Power on the projector manually first")
        print("   → Check Power Saving settings in projector menu")
        print("\n4. Wrong port number")
        print("   → Default ADCP port is 53595")
        print("   → Port 80 is HTTP web interface (not for control)")
        print("\n5. Firewall blocking the connection")
        print("   → Check network/router firewall settings")
        print("\nNote: Enabling network features increases power consumption")
        print("      as the network stays active in standby mode.")
        print("="*60)
        return False
    
    print(f"✓ Port {port} is open")
    
    try:
        print(f"Connecting to {ip}:{port}...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((ip, port))
        
        # Read initial response (projector may send "NOKEY" or other initial message)
        try:
            sock.settimeout(0.5)
            initial = sock.recv(1024)
            if initial:
                initial_msg = initial.decode('utf-8', errors='ignore').strip()
                if initial_msg and initial_msg != 'NOKEY':
                    print(f"Initial message: {initial_msg!r}")
        except socket.timeout:
            pass  # No initial message is OK
        
        # Send command (add newline if not present)
        cmd_bytes = command.encode('utf-8')
        if not command.endswith('\n') and not command.endswith('\r'):
            cmd_bytes += b'\r\n'
        
        print(f"Sending command: {command!r}")
        sock.sendall(cmd_bytes)
        
        # Read command response
        try:
            sock.settimeout(1.0)
            response = sock.recv(1024)
            if response:
                response_text = response.decode('utf-8', errors='ignore').strip()
                print(f"Response: {response_text!r}")
                # Check if response indicates success
                if 'ok' in response_text.lower():
                    print("✓ Command accepted by projector")
                elif 'err' in response_text.lower():
                    print("⚠️  Projector returned an error")
        except socket.timeout:
            print("(No response received - command may have been accepted)")
        
        sock.close()
        print("✓ Command sent successfully")
        return True
        
    except socket.timeout:
        print(f"✗ Timeout connecting to {ip}:{port}")
        return False
    except socket.error as e:
        print(f"✗ Socket error: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def load_config():
    """Try to load config from config.yaml if available."""
    config_path = Path(__file__).parent / "config.yaml"
    if config_path.exists():
        try:
            import yaml
            with open(config_path) as f:
                config = yaml.safe_load(f)
            projector = config.get("projector", {})
            return {
                "ip": projector.get("ip"),
                "port": projector.get("port", DEFAULT_PORT),
                "power_on_cmd": projector.get("power_on_command", DEFAULT_POWER_ON_CMD),
                "power_off_cmd": projector.get("power_off_command", DEFAULT_POWER_OFF_CMD),
            }
        except Exception as e:
            print(f"Note: Could not load config.yaml: {e}")
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Test TCP/IP commands to Sony XW5000 projector"
    )
    parser.add_argument(
        "action",
        choices=["on", "off", "test", "scan"],
        help="Action: 'on' (power on), 'off' (power off), 'test' (test connection), 'scan' (scan for open ports)"
    )
    parser.add_argument(
        "--ip",
        help="Projector IP address (required if not in config.yaml)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help=f"TCP port (default: {DEFAULT_PORT})"
    )
    parser.add_argument(
        "--command",
        help="Custom command to send (overrides default for on/off)"
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT,
        help=f"Connection timeout in seconds (default: {DEFAULT_TIMEOUT})"
    )
    parser.add_argument(
        "--scan-ports",
        help="Comma-separated list of ports to scan (e.g., '53595,8080,80')"
    )
    parser.add_argument(
        "--adcp",
        action="store_true",
        help="Use ADCP command format (POWR0001/POWR0000) instead of default format"
    )
    
    args = parser.parse_args()
    
    # Try to load config
    config = load_config()
    
    # Determine IP address
    ip = args.ip
    if not ip and config and config.get("ip"):
        ip = config["ip"]
        print(f"Using IP from config.yaml: {ip}")
    
    if not ip:
        print("ERROR: Projector IP address required")
        print("  Specify with --ip <address> or set 'projector.ip' in config.yaml")
        sys.exit(1)
    
    # Determine port
    port = args.port
    if config and config.get("port"):
        port = config["port"]
    
    # Handle port scanning
    if args.action == "scan":
        print(f"\n{'='*60}")
        print(f"Scanning Ports on {ip}")
        print(f"{'='*60}\n")
        
        ports_to_scan = []
        if args.scan_ports:
            ports_to_scan = [int(p.strip()) for p in args.scan_ports.split(',')]
        else:
            # Default common projector ports
            ports_to_scan = [53595, 8080, 80, 23, 554, 8081]
        
        print(f"Scanning {len(ports_to_scan)} ports...\n")
        open_ports = []
        for p in ports_to_scan:
            if check_port(ip, p, 1.0):
                print(f"✓ Port {p} is OPEN")
                open_ports.append(p)
            else:
                print(f"✗ Port {p} is closed")
        
        print(f"\n{'='*60}")
        if open_ports:
            print(f"Found {len(open_ports)} open port(s): {', '.join(map(str, open_ports))}")
            if 80 in open_ports and 53595 not in open_ports:
                print("\n⚠️  Port 80 is open (HTTP web interface)")
                print("   Port 53595 (ADCP control) is closed.")
                print("\n   To enable ADCP control:")
                print("   1. Menu > Setup > Network Management > On")
                print("   2. Menu > Setup > Remote Start > On")
        else:
            print("No open ports found.")
            print("\nMake sure:")
            print("1. Projector is powered on")
            print("2. Network Management is enabled (Menu > Setup > Network Management > On)")
            print("3. Remote Start is enabled (Menu > Setup > Remote Start > On)")
            print("4. Projector is on the same network")
        print(f"{'='*60}\n")
        sys.exit(0 if open_ports else 1)
    
    # Determine command
    if args.command:
        command = args.command
    elif args.action == "on":
        if args.adcp:
            command = ADCP_POWER_ON_CMD
        else:
            command = config["power_on_cmd"] if config and config.get("power_on_cmd") else DEFAULT_POWER_ON_CMD
    elif args.action == "off":
        if args.adcp:
            command = ADCP_POWER_OFF_CMD
        else:
            command = config["power_off_cmd"] if config and config.get("power_off_cmd") else DEFAULT_POWER_OFF_CMD
    else:  # test
        command = "TEST"  # Just a test command
    
    print(f"\n{'='*60}")
    print(f"Testing Sony XW5000 Projector Control")
    print(f"{'='*60}")
    print(f"IP: {ip}")
    print(f"Port: {port}")
    print(f"Action: {args.action}")
    print(f"{'='*60}\n")
    
    success = send_command(ip, port, command, args.timeout)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

