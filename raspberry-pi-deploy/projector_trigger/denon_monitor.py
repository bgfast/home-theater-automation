"""Network-based Denon AVR power state monitor using telnet polling."""

import socket
import time
import threading
import logging
from typing import Optional, Callable
from projector_trigger.network_discovery import discover_denon_ip

logger = logging.getLogger(__name__)


class DenonMonitor:
    """Monitor Denon AVR power state via telnet polling."""
    
    def __init__(
        self,
        ip: Optional[str] = None,
        mac: Optional[str] = None,
        port: int = 23,
        poll_interval_off: float = 5.0,
        poll_interval_on: float = 2.0,
        callback: Optional[Callable[[bool], None]] = None,
        timeout: float = 2.0
    ):
        """Initialize Denon monitor.
        
        Args:
            ip: Denon AVR IP address (optional if MAC provided)
            mac: Denon AVR MAC address for auto-discovery (optional if IP provided)
            port: Telnet port (default: 23)
            poll_interval_off: Polling interval when AVR is off (seconds)
            poll_interval_on: Polling interval when AVR is on (seconds)
            callback: Callback function(state: bool) called on state changes
            timeout: Socket timeout for telnet connections (seconds)
        """
        self.mac = mac
        self.ip = ip
        self.port = port
        self.poll_interval_off = poll_interval_off
        self.poll_interval_on = poll_interval_on
        self.callback = callback
        self.timeout = timeout
        
        self.last_state: Optional[bool] = None
        self.running = False
        self.monitor_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        
        # Discover IP if MAC provided
        if not self.ip and self.mac:
            logger.info(f"Discovering Denon AVR IP via MAC address: {self.mac}")
            self.ip = discover_denon_ip(mac_address=self.mac)
            if self.ip:
                logger.info(f"Found Denon AVR at {self.ip}")
            else:
                logger.warning(f"Could not discover Denon AVR IP from MAC {self.mac}")
        
        if not self.ip:
            raise ValueError("Denon AVR IP address required (provide ip or mac)")
        
        logger.info(f"Denon monitor initialized: {self.ip}:{self.port}, "
                   f"poll intervals: {self.poll_interval_off}s (off) / {self.poll_interval_on}s (on)")
    
    def query_power_state(self) -> Optional[bool]:
        """Query Denon AVR power state via telnet.
        
        Returns:
            True if AVR is ON, False if OFF/STANDBY, None on error
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            sock.connect((self.ip, self.port))
            
            # Send power query command
            sock.sendall(b'PW?\r')
            time.sleep(0.1)  # Brief delay for response
            
            # Read response
            response = sock.recv(1024)
            sock.close()
            
            response_text = response.decode('utf-8', errors='ignore').strip()
            logger.debug(f"Denon response: {response_text!r}")
            
            # Parse response
            if 'PWON' in response_text:
                return True
            elif 'PWSTANDBY' in response_text:
                return False
            else:
                logger.warning(f"Unexpected Denon response: {response_text!r}")
                return None
                
        except socket.timeout:
            logger.debug(f"Timeout querying Denon AVR at {self.ip}:{self.port}")
            return None
        except socket.error as e:
            logger.debug(f"Connection error querying Denon AVR: {e}")
            return None
        except Exception as e:
            logger.error(f"Error querying Denon AVR power state: {e}")
            return None
    
    def _monitor_loop(self):
        """Internal monitoring loop (runs in separate thread)."""
        logger.info("Denon monitor started")
        
        # Initial state query
        initial_state = self.query_power_state()
        if initial_state is not None:
            self.last_state = initial_state
            state_str = "ON" if initial_state else "OFF"
            logger.info(f"Initial Denon AVR state: {state_str}")
        else:
            logger.warning("Could not determine initial Denon AVR state")
        
        while self.running:
            try:
                current_state = self.query_power_state()
                
                if current_state is not None:
                    # Check for state change
                    if current_state != self.last_state:
                        state_str = "ON" if current_state else "OFF"
                        logger.info(f"Denon AVR state changed: {state_str}")
                        
                        # Call callback if provided
                        if self.callback:
                            try:
                                self.callback(current_state)
                            except Exception as e:
                                logger.error(f"Error in Denon monitor callback: {e}")
                        
                        self.last_state = current_state
                    
                    # Use adaptive polling interval
                    interval = self.poll_interval_on if current_state else self.poll_interval_off
                else:
                    # Error querying - use longer interval
                    interval = self.poll_interval_off
                    logger.debug(f"Error querying Denon AVR, retrying in {interval}s")
                
                # Sleep for polling interval
                time.sleep(interval)
                
            except Exception as e:
                logger.error(f"Error in Denon monitor loop: {e}")
                time.sleep(self.poll_interval_off)
        
        logger.info("Denon monitor stopped")
    
    def start(self):
        """Start monitoring in background thread."""
        if self.running:
            logger.warning("Denon monitor already running")
            return
        
        with self._lock:
            self.running = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
    
    def stop(self):
        """Stop monitoring."""
        if not self.running:
            return
        
        logger.info("Stopping Denon monitor...")
        with self._lock:
            self.running = False
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
        
        logger.info("Denon monitor stopped")
    
    def get_current_state(self) -> Optional[bool]:
        """Get current power state (synchronous query).
        
        Returns:
            True if ON, False if OFF, None on error
        """
        return self.query_power_state()

