#!/usr/bin/env python3
"""Test MAC address auto-discovery on different networks.

This script simulates the "new homeowner" scenario where:
- Network subnet is unknown (could be 192.168.1.x, 10.0.0.x, 172.16.x.x, etc.)
- Only MAC addresses are known
- System must auto-discover device IPs
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from projector_trigger.network_discovery import (
    discover_projector_ip,
    discover_denon_ip,
    get_local_network,
    normalize_mac
)
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_network_detection():
    """Test that the system can detect the current network."""
    print("\n" + "="*60)
    print("Test 1: Network Auto-Detection")
    print("="*60)
    
    network = get_local_network()
    if network:
        print(f"✓ Detected local network: {network}")
        print(f"  The system will scan this network for devices")
        return True
    else:
        print("✗ Could not detect local network")
        print("  This might happen if network tools are not available")
        return False


def test_projector_discovery(projector_mac: str):
    """Test projector discovery by MAC address only."""
    print("\n" + "="*60)
    print("Test 2: Projector Discovery (MAC Only)")
    print("="*60)
    print(f"MAC Address: {projector_mac}")
    print(f"Normalized: {normalize_mac(projector_mac)}")
    print("\nAttempting discovery (this may take 30-60 seconds)...")
    
    # Discover using MAC only (no IP)
    projector_ip = discover_projector_ip(mac_address=projector_mac, ip_address=None)
    
    if projector_ip:
        print(f"\n✓ SUCCESS: Found projector at {projector_ip}")
        print(f"  This works regardless of network subnet!")
        return True
    else:
        print(f"\n✗ FAILED: Could not find projector with MAC {projector_mac}")
        print("\nPossible reasons:")
        print("  1. Projector is not on the same network")
        print("  2. Projector is powered off")
        print("  3. Network scanning tools (nmap) not available")
        print("  4. Firewall blocking network scans")
        return False


def test_denon_discovery(denon_mac: str):
    """Test Denon AVR discovery by MAC address only."""
    print("\n" + "="*60)
    print("Test 3: Denon AVR Discovery (MAC Only)")
    print("="*60)
    print(f"MAC Address: {denon_mac}")
    print(f"Normalized: {normalize_mac(denon_mac)}")
    print("\nAttempting discovery (this may take 30-60 seconds)...")
    
    # Discover using MAC only (no IP)
    denon_ip = discover_denon_ip(mac_address=denon_mac, ip_address=None)
    
    if denon_ip:
        print(f"\n✓ SUCCESS: Found Denon AVR at {denon_ip}")
        print(f"  This works regardless of network subnet!")
        return True
    else:
        print(f"\n✗ FAILED: Could not find Denon AVR with MAC {denon_mac}")
        print("\nPossible reasons:")
        print("  1. Denon AVR is not on the same network")
        print("  2. Denon AVR is powered off")
        print("  3. Network scanning tools (nmap) not available")
        print("  4. Firewall blocking network scans")
        return False


def test_config_without_ips():
    """Test that config works with only MAC addresses (no IPs)."""
    print("\n" + "="*60)
    print("Test 4: Configuration with MAC Addresses Only")
    print("="*60)
    print("\nTo test the 'new homeowner' scenario:")
    print("1. Edit config.yaml and:")
    print("   - Keep projector.mac (remove or comment projector.ip)")
    print("   - Keep denon.mac (remove or comment denon.ip)")
    print("2. Restart the service")
    print("3. The system will auto-discover IPs on any network")
    print("\nExample config.yaml:")
    print("-" * 60)
    print("""
projector:
  mac: "F8-4E-17-B8-E0-9E"  # Only MAC - no IP!
  # ip: "192.168.50.182"     # Commented out or removed

denon:
  mac: "00:06:78:97:0F:48"   # Only MAC - no IP!
  # ip: "192.168.50.148"     # Commented out or removed
""")
    print("-" * 60)


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("MAC Address Auto-Discovery Test")
    print("Simulating 'New Homeowner' Scenario")
    print("="*60)
    
    # Get MAC addresses from config or use defaults
    try:
        from projector_trigger.config import Config
        config = Config()
        projector_mac = config.projector_mac
        denon_mac = config.denon_mac
    except Exception as e:
        print(f"Warning: Could not load config: {e}")
        print("Using default MAC addresses from your config.yaml")
        projector_mac = "F8-4E-17-B8-E0-9E"
        denon_mac = "00:06:78:97:0F:48"
    
    results = []
    
    # Test 1: Network detection
    results.append(("Network Detection", test_network_detection()))
    
    # Test 2: Projector discovery
    if projector_mac:
        results.append(("Projector Discovery", test_projector_discovery(projector_mac)))
    else:
        print("\n⚠ Skipping projector test - no MAC address configured")
    
    # Test 3: Denon discovery
    if denon_mac:
        results.append(("Denon Discovery", test_denon_discovery(denon_mac)))
    else:
        print("\n⚠ Skipping Denon test - no MAC address configured")
    
    # Test 4: Configuration guidance
    test_config_without_ips()
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print("\n" + "="*60)
    print("How It Works:")
    print("="*60)
    print("1. System auto-detects local network (e.g., 192.168.1.0/24)")
    print("2. Scans the network using nmap to find all devices")
    print("3. Matches MAC addresses to find your devices")
    print("4. Works on ANY network subnet (192.168.x.x, 10.x.x.x, 172.16.x.x, etc.)")
    print("\nThis means:")
    print("  ✓ No network configuration needed for new homeowners")
    print("  ✓ Works with DHCP (IPs can change)")
    print("  ✓ Only MAC addresses need to be configured")
    print("="*60)


if __name__ == "__main__":
    main()

