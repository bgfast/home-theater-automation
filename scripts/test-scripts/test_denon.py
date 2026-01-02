#!/usr/bin/env python3
"""Test script to check Denon AVR-X6700H network control capabilities."""

import socket
import sys
import argparse
import time

DEFAULT_PORT = 23
DEFAULT_TIMEOUT = 2.0


def test_telnet_connection(ip: str, port: int = DEFAULT_PORT, timeout: float = DEFAULT_TIMEOUT):
    """Test basic telnet connection to Denon AVR."""
    print(f"\n{'='*60}")
    print(f"Testing Denon AVR Network Control")
    print(f"{'='*60}")
    print(f"IP: {ip}")
    print(f"Port: {port}")
    print(f"{'='*60}\n")
    
    try:
        print(f"Connecting to {ip}:{port}...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        
        if result != 0:
            print(f"✗ Connection failed (error code: {result})")
            print("\nPossible causes:")
            print("1. Denon AVR is powered off")
            print("2. Network control is disabled on AVR")
            print("3. Wrong IP address")
            print("4. Firewall blocking port 23")
            return False
        
        print("✓ Connected successfully")
        sock.close()
        return True
        
    except socket.timeout:
        print(f"✗ Connection timeout")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def query_power_state(ip: str, port: int = DEFAULT_PORT, timeout: float = DEFAULT_TIMEOUT):
    """Query Denon AVR power state."""
    try:
        print(f"\nQuerying power state...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((ip, port))
        
        # Send power query command
        sock.sendall(b'PW?\r')
        time.sleep(0.1)
        
        # Read response
        response = sock.recv(1024)
        response_text = response.decode('utf-8', errors='ignore').strip()
        
        print(f"Response: {response_text!r}")
        print(f"Hex: {response.hex()}")
        
        # Parse response
        if 'PWON' in response_text:
            print("✓ AVR is ON")
            return True
        elif 'PWSTANDBY' in response_text:
            print("✓ AVR is STANDBY (OFF)")
            return False
        else:
            print("⚠️  Unknown power state response")
            return None
        
        sock.close()
        
    except Exception as e:
        print(f"✗ Error querying power state: {e}")
        return None


def test_commands(ip: str, port: int = DEFAULT_PORT, timeout: float = DEFAULT_TIMEOUT):
    """Test various Denon commands."""
    commands = [
        b'PW?\r',           # Power query
        b'MV?\r',           # Volume query
        b'SI?\r',          # Input query
        b'ZM?\r',          # Zone 2 query
    ]
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((ip, port))
        
        print(f"\n{'='*60}")
        print("Testing Denon Commands")
        print(f"{'='*60}\n")
        
        for cmd in commands:
            print(f"Sending: {cmd!r}")
            sock.sendall(cmd)
            time.sleep(0.2)
            
            try:
                response = sock.recv(1024)
                response_text = response.decode('utf-8', errors='ignore').strip()
                print(f"Response: {response_text!r}")
            except:
                print("(No response)")
            
            print("-" * 40)
            time.sleep(0.3)
        
        sock.close()
        
    except Exception as e:
        print(f"✗ Error: {e}")


def monitor_power_state(ip: str, port: int = DEFAULT_PORT, interval: float = 2.0):
    """Continuously monitor power state."""
    print(f"\n{'='*60}")
    print("Monitoring Denon AVR Power State")
    print(f"{'='*60}")
    print(f"Polling every {interval} seconds")
    print("Press Ctrl+C to stop\n")
    
    last_state = None
    
    try:
        while True:
            state = query_power_state(ip, port)
            
            if state is not None:
                state_str = "ON" if state else "OFF"
                if state != last_state:
                    print(f"\n🔄 STATE CHANGED: {state_str}")
                    last_state = state
                else:
                    print(f"   Current state: {state_str}")
            
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\n\nStopping monitor...")


def main():
    parser = argparse.ArgumentParser(
        description="Test Denon AVR-X6700H network control"
    )
    parser.add_argument(
        "action",
        choices=["test", "query", "commands", "monitor"],
        help="Action: 'test' (test connection), 'query' (query power), 'commands' (test commands), 'monitor' (continuous monitoring)"
    )
    parser.add_argument(
        "--ip",
        required=True,
        help="Denon AVR IP address"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help=f"Telnet port (default: {DEFAULT_PORT})"
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=2.0,
        help="Polling interval for monitor (default: 2.0 seconds)"
    )
    
    args = parser.parse_args()
    
    if args.action == "test":
        success = test_telnet_connection(args.ip, args.port)
        sys.exit(0 if success else 1)
    elif args.action == "query":
        state = query_power_state(args.ip, args.port)
        sys.exit(0 if state is not None else 1)
    elif args.action == "commands":
        test_commands(args.ip, args.port)
        sys.exit(0)
    elif args.action == "monitor":
        monitor_power_state(args.ip, args.port, args.interval)
        sys.exit(0)


if __name__ == "__main__":
    main()

