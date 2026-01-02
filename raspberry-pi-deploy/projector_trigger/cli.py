"""CLI commands for testing and manual control."""

import sys
import time
import logging
from typing import Optional
from projector_trigger.config import Config
from projector_trigger.gpio_monitor import GPIOMonitor
from projector_trigger.projector_control import ProjectorControl
from projector_trigger.network_discovery import discover_projector_ip

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def cmd_status(config_path: Optional[str] = None):
    """Show GPIO state and last action."""
    try:
        config = Config(config_path)
        
        # Read GPIO state
        gpio_monitor = GPIOMonitor(
            pin=config.gpio_pin,
            debounce_ms=config.debounce_ms,
            callback=lambda x: None  # No callback needed for status
        )
        
        state = gpio_monitor.read_state()
        gpio_monitor.stop()
        
        # Discover projector IP
        projector_ip = discover_projector_ip(
            mac_address=config.projector_mac,
            ip_address=config.projector_ip
        )
        
        if not projector_ip:
            print("=" * 50)
            print("Projector Trigger Bridge Status")
            print("=" * 50)
            print("ERROR: Could not discover projector IP address")
            if config.projector_mac:
                print(f"MAC Address: {config.projector_mac}")
            if config.projector_ip:
                print(f"Configured IP: {config.projector_ip}")
            print("=" * 50)
            sys.exit(1)
        
        # Get projector control info
        projector_control = ProjectorControl(
            ip=projector_ip,
            port=config.projector_port,
            power_on_cmd=config.power_on_command,
            power_off_cmd=config.power_off_command,
            timeout=config.timeout_seconds,
            max_retries=config.max_retries,
            backoff=config.retry_backoff_seconds
        )
        
        print("=" * 50)
        print("Projector Trigger Bridge Status")
        print("=" * 50)
        print(f"GPIO Pin: {config.gpio_pin}")
        if state is not None:
            print(f"GPIO State: {'LOW (Trigger ON)' if state else 'HIGH (Trigger OFF)'}")
        else:
            print("GPIO State: Not available (not on Raspberry Pi?)")
        print(f"Projector: {projector_ip}:{config.projector_port}")
        if config.projector_mac:
            print(f"Projector MAC: {config.projector_mac}")
        print(f"Power On Command: {config.power_on_command}")
        print(f"Power Off Command: {config.power_off_command}")
        last_cmd = projector_control.get_last_command()
        if last_cmd:
            print(f"Last Command: {last_cmd}")
            last_time = projector_control.get_last_success_time()
            if last_time:
                print(f"Last Success: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(last_time))}")
        print("=" * 50)
        
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        sys.exit(1)


def cmd_on(config_path: Optional[str] = None):
    """Send power on command."""
    try:
        config = Config(config_path)
        
        # Discover projector IP
        projector_ip = discover_projector_ip(
            mac_address=config.projector_mac,
            ip_address=config.projector_ip
        )
        
        if not projector_ip:
            print("ERROR: Could not discover projector IP address")
            sys.exit(1)
        
        projector_control = ProjectorControl(
            ip=projector_ip,
            port=config.projector_port,
            power_on_cmd=config.power_on_command,
            power_off_cmd=config.power_off_command,
            timeout=config.timeout_seconds,
            max_retries=config.max_retries,
            backoff=config.retry_backoff_seconds
        )
        
        print(f"Sending power on command to {projector_ip}:{config.projector_port}...")
        success = projector_control.power_on()
        
        if success:
            print("✓ Power on command sent successfully")
            sys.exit(0)
        else:
            print("✗ Failed to send power on command")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Error sending power on: {e}")
        sys.exit(1)


def cmd_off(config_path: Optional[str] = None):
    """Send power off command."""
    try:
        config = Config(config_path)
        
        # Discover projector IP
        projector_ip = discover_projector_ip(
            mac_address=config.projector_mac,
            ip_address=config.projector_ip
        )
        
        if not projector_ip:
            print("ERROR: Could not discover projector IP address")
            sys.exit(1)
        
        projector_control = ProjectorControl(
            ip=projector_ip,
            port=config.projector_port,
            power_on_cmd=config.power_on_command,
            power_off_cmd=config.power_off_command,
            timeout=config.timeout_seconds,
            max_retries=config.max_retries,
            backoff=config.retry_backoff_seconds
        )
        
        print(f"Sending power off command to {projector_ip}:{config.projector_port}...")
        success = projector_control.power_off()
        
        if success:
            print("✓ Power off command sent successfully")
            sys.exit(0)
        else:
            print("✗ Failed to send power off command")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Error sending power off: {e}")
        sys.exit(1)


def cmd_monitor(config_path: Optional[str] = None):
    """Run foreground monitor and print events."""
    try:
        config = Config(config_path)
        
        # Discover projector IP
        projector_ip = discover_projector_ip(
            mac_address=config.projector_mac,
            ip_address=config.projector_ip
        )
        
        if not projector_ip:
            print("ERROR: Could not discover projector IP address")
            sys.exit(1)
        
        gpio_monitor = GPIOMonitor(
            pin=config.gpio_pin,
            debounce_ms=config.debounce_ms,
            callback=lambda is_triggered: print(f"[{time.strftime('%H:%M:%S')}] Trigger: {'ON' if is_triggered else 'OFF'}")
        )
        
        projector_control = ProjectorControl(
            ip=projector_ip,
            port=config.projector_port,
            power_on_cmd=config.power_on_command,
            power_off_cmd=config.power_off_command,
            timeout=config.timeout_seconds,
            max_retries=config.max_retries,
            backoff=config.retry_backoff_seconds
        )
        
        def on_change(is_triggered: bool):
            print(f"[{time.strftime('%H:%M:%S')}] Trigger: {'ON' if is_triggered else 'OFF'}")
            if is_triggered:
                print(f"[{time.strftime('%H:%M:%S')}] Sending power ON...")
                projector_control.power_on()
            else:
                print(f"[{time.strftime('%H:%M:%S')}] Sending power OFF...")
                projector_control.power_off()
        
        gpio_monitor.callback = on_change
        
        print("Monitoring GPIO for trigger changes...")
        print("Press Ctrl+C to stop")
        print("-" * 50)
        
        gpio_monitor.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping monitor...")
        finally:
            gpio_monitor.stop()
            
    except Exception as e:
        logger.error(f"Error in monitor: {e}")
        sys.exit(1)


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Projector Trigger Bridge CLI')
    parser.add_argument('command', choices=['status', 'on', 'off', 'monitor'],
                       help='Command to execute')
    parser.add_argument('--config', type=str, help='Path to config file')
    
    args = parser.parse_args()
    
    if args.command == 'status':
        cmd_status(args.config)
    elif args.command == 'on':
        cmd_on(args.config)
    elif args.command == 'off':
        cmd_off(args.config)
    elif args.command == 'monitor':
        cmd_monitor(args.config)


if __name__ == '__main__':
    main()

