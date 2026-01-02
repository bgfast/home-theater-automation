"""Network discovery to find projector by MAC address."""

import subprocess
import re
import logging
import socket
from typing import Optional

logger = logging.getLogger(__name__)


def normalize_mac(mac: str) -> str:
    """Normalize MAC address to lowercase with colons.
    
    Args:
        mac: MAC address in any format (e.g., "F8-4E-17-B8-E0-9E" or "f84e17b8e09e")
    
    Returns:
        Normalized MAC address (e.g., "f8:4e:17:b8:e0:9e")
    """
    # Remove all separators and convert to lowercase
    mac_clean = re.sub(r'[-:.\s]', '', mac.lower())
    # Add colons every 2 characters
    return ':'.join(mac_clean[i:i+2] for i in range(0, len(mac_clean), 2))


def get_local_network() -> Optional[str]:
    """Get local network CIDR (e.g., '192.168.1.0/24').
    
    Returns:
        Network CIDR string or None if unable to determine
    """
    try:
        # Get default gateway interface
        result = subprocess.run(
            ['ip', 'route', 'show', 'default'],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0:
            # Parse output like "default via 192.168.1.1 dev eth0"
            match = re.search(r'dev\s+(\w+)', result.stdout)
            if match:
                interface = match.group(1)
                # Get IP and netmask for this interface
                result = subprocess.run(
                    ['ip', 'addr', 'show', interface],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                if result.returncode == 0:
                    # Parse "inet 192.168.1.100/24"
                    match = re.search(r'inet\s+(\d+\.\d+\.\d+\.\d+)/(\d+)', result.stdout)
                    if match:
                        ip = match.group(1)
                        prefix = match.group(2)
                        # Convert to network address
                        ip_parts = ip.split('.')
                        if prefix == '24':
                            return f"{'.'.join(ip_parts[:3])}.0/24"
                        elif prefix == '16':
                            return f"{'.'.join(ip_parts[:2])}.0.0/16"
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
        logger.debug(f"Could not determine network via 'ip' command: {e}")
    
    # Fallback: try arp table to guess network
    try:
        result = subprocess.run(
            ['arp', '-a'],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0:
            # Find first IP in arp table
            match = re.search(r'\((\d+\.\d+\.\d+\.\d+)\)', result.stdout)
            if match:
                ip = match.group(1)
                ip_parts = ip.split('.')
                return f"{'.'.join(ip_parts[:3])}.0/24"
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
        logger.debug(f"Could not determine network via 'arp' command: {e}")
    
    return None


def find_ip_by_mac(mac_address: str, network: Optional[str] = None) -> Optional[str]:
    """Find IP address of a device by its MAC address.
    
    Args:
        mac_address: MAC address to search for (any format)
        network: Optional network CIDR (e.g., '192.168.1.0/24'). If None, auto-detects.
    
    Returns:
        IP address if found, None otherwise
    """
    mac_normalized = normalize_mac(mac_address)
    logger.info(f"Searching for device with MAC address: {mac_normalized}")
    
    # Try ARP table first (fastest)
    try:
        result = subprocess.run(
            ['arp', '-a'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            # Search for MAC in ARP output
            # Format: "hostname (192.168.1.100) at f8:4e:17:b8:e0:9e [ether] on eth0"
            pattern = rf'\((\d+\.\d+\.\d+\.\d+)\)\s+at\s+{re.escape(mac_normalized)}'
            match = re.search(pattern, result.stdout, re.IGNORECASE)
            if match:
                ip = match.group(1)
                logger.info(f"Found device at {ip} in ARP table")
                return ip
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
        logger.debug(f"ARP lookup failed: {e}")
    
    # If not in ARP table, try scanning network
    if network is None:
        network = get_local_network()
    
    if network:
        logger.info(f"Scanning network {network} for device...")
        return _scan_network_for_mac(network, mac_normalized)
    else:
        logger.warning("Could not determine network to scan")
        return None


def _scan_network_for_mac(network: str, mac: str) -> Optional[str]:
    """Scan network for device with given MAC address.
    
    Args:
        network: Network CIDR (e.g., '192.168.1.0/24')
        mac: Normalized MAC address
    
    Returns:
        IP address if found, None otherwise
    """
    # Extract network base (e.g., '192.168.1' from '192.168.1.0/24')
    match = re.match(r'(\d+\.\d+\.\d+)\.\d+/\d+', network)
    if not match:
        return None
    
    network_base = match.group(1)
    logger.info(f"Scanning {network_base}.0/24 for MAC {mac}...")
    
    # Use nmap if available (most reliable)
    try:
        result = subprocess.run(
            ['nmap', '-sn', network],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            # Parse nmap output for MAC addresses
            lines = result.stdout.split('\n')
            current_ip = None
            for line in lines:
                # Look for IP address
                ip_match = re.search(r'Nmap scan report for (\d+\.\d+\.\d+\.\d+)', line)
                if ip_match:
                    current_ip = ip_match.group(1)
                # Look for MAC address
                mac_match = re.search(r'MAC Address:\s+([0-9A-Fa-f:]{17})', line)
                if mac_match and current_ip:
                    found_mac = mac_match.group(1).lower()
                    if found_mac == mac.lower():
                        logger.info(f"Found device at {current_ip} via nmap scan")
                        return current_ip
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
        logger.debug(f"nmap scan failed: {e}")
    
    # Fallback: try arp-scan if available
    try:
        result = subprocess.run(
            ['arp-scan', '--local'],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                # Format: "192.168.1.100    f8:4e:17:b8:e0:9e    Manufacturer"
                parts = line.split()
                if len(parts) >= 2:
                    ip = parts[0]
                    found_mac = normalize_mac(parts[1])
                    if found_mac == mac:
                        logger.info(f"Found device at {ip} via arp-scan")
                        return ip
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
        logger.debug(f"arp-scan failed: {e}")
    
    logger.warning(f"Could not find device with MAC {mac} on network {network}")
    return None


def discover_device_ip(mac_address: Optional[str] = None, ip_address: Optional[str] = None, device_name: str = "device") -> Optional[str]:
    """Discover device IP address by MAC address or validate provided IP.
    
    Generic function that works for any device (projector, Denon AVR, etc.).
    
    Args:
        mac_address: Optional MAC address to search for
        ip_address: Optional IP address to validate
        device_name: Name of device for logging (e.g., "projector", "Denon AVR")
    
    Returns:
        IP address if found/valid, None otherwise
    """
    # If IP is provided, validate it
    if ip_address:
        try:
            # Try to resolve and ping
            socket.gethostbyname(ip_address)
            logger.info(f"Using provided {device_name} IP address: {ip_address}")
            return ip_address
        except socket.gaierror:
            logger.warning(f"Invalid {device_name} IP address: {ip_address}")
    
    # If MAC is provided, search for it
    if mac_address:
        ip = find_ip_by_mac(mac_address)
        if ip:
            logger.info(f"Found {device_name} at {ip} via MAC address discovery")
            return ip
        else:
            logger.error(f"Could not find {device_name} with MAC address: {mac_address}")
    
    return None


def discover_projector_ip(mac_address: Optional[str] = None, ip_address: Optional[str] = None) -> Optional[str]:
    """Discover projector IP address.
    
    If IP address is provided, validates it's reachable.
    If MAC address is provided, searches for it on the network.
    
    Args:
        mac_address: Optional MAC address to search for
        ip_address: Optional IP address to validate
    
    Returns:
        IP address if found/valid, None otherwise
    """
    return discover_device_ip(mac_address, ip_address, "projector")


def discover_denon_ip(mac_address: Optional[str] = None, ip_address: Optional[str] = None) -> Optional[str]:
    """Discover Denon AVR IP address.
    
    If IP address is provided, validates it's reachable.
    If MAC address is provided, searches for it on the network.
    
    Args:
        mac_address: Optional MAC address to search for
        ip_address: Optional IP address to validate
    
    Returns:
        IP address if found/valid, None otherwise
    """
    return discover_device_ip(mac_address, ip_address, "Denon AVR")

