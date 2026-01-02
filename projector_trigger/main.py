"""Main service daemon for projector trigger bridge."""

import signal
import sys
import time
import logging
from logging.handlers import SysLogHandler
from projector_trigger.config import Config
from projector_trigger.denon_monitor import DenonMonitor
from projector_trigger.projector_control import ProjectorControl
from projector_trigger.network_discovery import discover_projector_ip

logger = logging.getLogger(__name__)


class ProjectorTriggerService:
    """Main service that monitors Denon AVR power state and controls projector."""
    
    def __init__(self, config_path: str = None):
        """Initialize service.
        
        Args:
            config_path: Optional path to config file
        """
        self.config = Config(config_path)
        self.denon_monitor: DenonMonitor = None
        self.projector_control: ProjectorControl = None
        self.running = False
        self._setup_logging()
        self._setup_components()
        self._setup_signal_handlers()
    
    def _setup_logging(self):
        """Configure logging to journald and console."""
        log_level = getattr(logging, self.config.log_level.upper(), logging.INFO)
        
        # Create logger
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        
        # Remove existing handlers
        root_logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_format)
        root_logger.addHandler(console_handler)
        
        # Try to add syslog handler for journald (may fail if not on systemd system)
        try:
            syslog_handler = SysLogHandler(address='/dev/log')
            syslog_handler.setLevel(log_level)
            syslog_format = logging.Formatter(
                '%(name)s[%(process)d]: %(levelname)s - %(message)s'
            )
            syslog_handler.setFormatter(syslog_format)
            root_logger.addHandler(syslog_handler)
        except Exception as e:
            logger.debug(f"Could not set up syslog handler: {e}")
    
    def _setup_components(self):
        """Initialize Denon monitor and projector control."""
        try:
            # Discover projector IP if needed
            projector_ip = discover_projector_ip(
                mac_address=self.config.projector_mac,
                ip_address=self.config.projector_ip
            )
            
            if not projector_ip:
                error_msg = "Could not determine projector IP address. "
                if self.config.projector_mac:
                    error_msg += f"MAC address configured: {self.config.projector_mac}. "
                if self.config.projector_ip:
                    error_msg += f"IP address configured: {self.config.projector_ip}. "
                error_msg += "Please check network connectivity and configuration."
                raise RuntimeError(error_msg)
            
            # Initialize projector control
            self.projector_control = ProjectorControl(
                ip=projector_ip,
                port=self.config.projector_port,
                power_on_cmd=self.config.power_on_command,
                power_off_cmd=self.config.power_off_command,
                timeout=self.config.timeout_seconds,
                max_retries=self.config.max_retries,
                backoff=self.config.retry_backoff_seconds
            )
            logger.info(f"Projector control initialized: {projector_ip}:{self.config.projector_port}")
            
            # Initialize Denon monitor
            denon_ip = self.config.denon_ip
            denon_mac = self.config.denon_mac
            
            if not denon_ip and not denon_mac:
                raise RuntimeError("Denon AVR configuration required: provide 'denon.ip' or 'denon.mac' in config.yaml")
            
            self.denon_monitor = DenonMonitor(
                ip=denon_ip,
                mac=denon_mac,
                port=self.config.denon_port,
                poll_interval_off=self.config.denon_poll_interval_off,
                poll_interval_on=self.config.denon_poll_interval_on,
                callback=self._on_denon_state_change
            )
            logger.info(f"Denon monitor initialized: polling intervals {self.config.denon_poll_interval_off}s (off) / {self.config.denon_poll_interval_on}s (on)")
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            raise
    
    def _setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown."""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
    
    def _on_denon_state_change(self, is_on: bool):
        """Callback when Denon AVR power state changes.
        
        Args:
            is_on: True if Denon AVR is ON, False if OFF/STANDBY
        """
        logger.info(f"Denon AVR state changed: {'ON' if is_on else 'OFF'}")
        
        if is_on:
            logger.info("Denon AVR powered on - turning projector ON")
            success = self.projector_control.power_on()
            if not success:
                logger.error("Failed to send projector power on command")
            else:
                logger.info("Projector power on command sent successfully")
        else:
            logger.info("Denon AVR powered off - turning projector OFF")
            success = self.projector_control.power_off()
            if not success:
                logger.error("Failed to send projector power off command")
            else:
                logger.info("Projector power off command sent successfully")
    
    def start(self):
        """Start the service."""
        if self.running:
            logger.warning("Service already running")
            return
        
        logger.info("Starting projector trigger bridge service...")
        self.running = True
        
        try:
            self.denon_monitor.start()
            
            # Main loop - just wait for events
            while self.running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        except Exception as e:
            logger.error(f"Service error: {e}", exc_info=True)
        finally:
            self.stop()
    
    def stop(self):
        """Stop the service."""
        if not self.running:
            return
        
        logger.info("Stopping projector trigger bridge service...")
        self.running = False
        
        if self.denon_monitor:
            self.denon_monitor.stop()
        
        logger.info("Service stopped")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Projector Trigger Bridge Service')
    parser.add_argument('--config', type=str, help='Path to config file')
    args = parser.parse_args()
    
    try:
        service = ProjectorTriggerService(config_path=args.config)
        service.start()
    except Exception as e:
        logger.error(f"Failed to start service: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()

