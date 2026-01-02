"""CLI commands for testing and manual control."""

import sys
import time
import logging
from typing import Optional
from projector_trigger.config import Config
from projector_trigger.denon_monitor import DenonMonitor
from projector_trigger.projector_control import ProjectorControl
from projector_trigger.network_discovery import discover_projector_ip

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def cmd_status(config_path: Optional[str] = None):
    """Show Denon AVR state and projector status."""
    try:
        config = Config(config_path)
        
        # Query Denon AVR state
        denon_monitor = DenonMonitor(
            ip=config.denon_ip,
            mac=config.denon_mac,
            port=config.denon_port,
            poll_interval_off=config.denon_poll_interval_off,
            poll_interval_on=config.denon_poll_interval_on
        )
        
        denon_state = denon_monitor.get_current_state()
        
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
        print("Denon AVR:")
        if config.denon_ip:
            print(f"  IP: {config.denon_ip}")
        if config.denon_mac:
            print(f"  MAC: {config.denon_mac}")
        print(f"  Port: {config.denon_port}")
        if denon_state is not None:
            print(f"  State: {'ON' if denon_state else 'OFF/STANDBY'}")
        else:
            print("  State: Unknown (connection error)")
        print(f"  Poll Intervals: {config.denon_poll_interval_off}s (off) / {config.denon_poll_interval_on}s (on)")
        print()
        print("Projector:")
        print(f"  IP: {projector_ip}:{config.projector_port}")
        if config.projector_mac:
            print(f"  MAC: {config.projector_mac}")
        print(f"  Power On Command: {config.power_on_command}")
        print(f"  Power Off Command: {config.power_off_command}")
        last_cmd = projector_control.get_last_command()
        if last_cmd:
            print(f"  Last Command: {last_cmd}")
            last_time = projector_control.get_last_success_time()
            if last_time:
                print(f"  Last Success: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(last_time))}")
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
        
        projector_control = ProjectorControl(
            ip=projector_ip,
            port=config.projector_port,
            power_on_cmd=config.power_on_command,
            power_off_cmd=config.power_off_command,
            timeout=config.timeout_seconds,
            max_retries=config.max_retries,
            backoff=config.retry_backoff_seconds
        )
        
        def on_change(is_on: bool):
            state_str = "ON" if is_on else "OFF"
            print(f"[{time.strftime('%H:%M:%S')}] Denon AVR: {state_str}")
            if is_on:
                print(f"[{time.strftime('%H:%M:%S')}] Sending projector power ON...")
                success = projector_control.power_on()
                if success:
                    print(f"[{time.strftime('%H:%M:%S')}] ✓ Projector power ON sent")
                else:
                    print(f"[{time.strftime('%H:%M:%S')}] ✗ Failed to send projector power ON")
            else:
                print(f"[{time.strftime('%H:%M:%S')}] Sending projector power OFF...")
                success = projector_control.power_off()
                if success:
                    print(f"[{time.strftime('%H:%M:%S')}] ✓ Projector power OFF sent")
                else:
                    print(f"[{time.strftime('%H:%M:%S')}] ✗ Failed to send projector power OFF")
        
        denon_monitor = DenonMonitor(
            ip=config.denon_ip,
            mac=config.denon_mac,
            port=config.denon_port,
            poll_interval_off=config.denon_poll_interval_off,
            poll_interval_on=config.denon_poll_interval_on,
            callback=on_change
        )
        
        print("Monitoring Denon AVR power state...")
        print("Press Ctrl+C to stop")
        print("-" * 50)
        
        denon_monitor.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping monitor...")
        finally:
            denon_monitor.stop()
            
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

