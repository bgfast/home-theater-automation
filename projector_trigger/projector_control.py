"""Projector control via TCP/IP."""

import socket
import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class ProjectorControl:
    """Send TCP commands to projector with retries and timeouts."""
    
    def __init__(self, ip: str, port: int, power_on_cmd: str, power_off_cmd: str,
                 timeout: float, max_retries: int, backoff: float):
        """Initialize projector control.
        
        Args:
            ip: Projector IP address
            port: TCP port
            power_on_cmd: Command string for power on
            power_off_cmd: Command string for power off
            timeout: Timeout per attempt in seconds
            max_retries: Maximum retry attempts
            backoff: Base backoff delay in seconds (increases with each retry)
        """
        self.ip = ip
        self.port = port
        self.power_on_cmd = power_on_cmd
        self.power_off_cmd = power_off_cmd
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff = backoff
        self._last_command: Optional[str] = None
        self._last_success_time: Optional[float] = None
    
    def _send_command(self, command: str) -> bool:
        """Send a single command attempt.
        
        Returns True if successful, False otherwise.
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            sock.connect((self.ip, self.port))
            
            # Send command (add newline if not present, as many projectors expect it)
            cmd_bytes = command.encode('utf-8')
            if not command.endswith('\n') and not command.endswith('\r'):
                cmd_bytes += b'\r\n'
            
            sock.sendall(cmd_bytes)
            logger.debug(f"Sent command to {self.ip}:{self.port}: {command.strip()}")
            
            # Optionally read response (some projectors send ACK)
            try:
                sock.settimeout(0.5)  # Short timeout for response
                response = sock.recv(1024)
                if response:
                    logger.debug(f"Response: {response.decode('utf-8', errors='ignore').strip()}")
            except socket.timeout:
                # No response is OK
                pass
            
            sock.close()
            return True
            
        except socket.timeout:
            logger.warning(f"Timeout connecting to projector {self.ip}:{self.port}")
            return False
        except socket.error as e:
            logger.warning(f"Socket error connecting to projector {self.ip}:{self.port}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending command: {e}")
            return False
    
    def power_on(self) -> bool:
        """Send power on command with retries.
        
        Returns True if command was successfully sent, False otherwise.
        """
        return self._send_with_retries(self.power_on_cmd, "power on")
    
    def power_off(self) -> bool:
        """Send power off command with retries.
        
        Returns True if command was successfully sent, False otherwise.
        """
        return self._send_with_retries(self.power_off_cmd, "power off")
    
    def _send_with_retries(self, command: str, description: str) -> bool:
        """Send command with retry logic.
        
        Args:
            command: Command string to send
            description: Human-readable description for logging
            
        Returns True if successful, False if all retries failed.
        """
        for attempt in range(self.max_retries):
            if attempt > 0:
                # Exponential backoff: 0.5s, 1.0s, 1.5s, etc.
                delay = self.backoff * attempt
                logger.info(f"Retrying {description} (attempt {attempt + 1}/{self.max_retries}) after {delay:.1f}s...")
                time.sleep(delay)
            
            logger.info(f"Sending {description} command to {self.ip}:{self.port}...")
            if self._send_command(command):
                self._last_command = command
                self._last_success_time = time.time()
                logger.info(f"Successfully sent {description} command")
                return True
        
        logger.error(f"Failed to send {description} command after {self.max_retries} attempts")
        return False
    
    def get_last_command(self) -> Optional[str]:
        """Get the last successfully sent command."""
        return self._last_command
    
    def get_last_success_time(self) -> Optional[float]:
        """Get timestamp of last successful command."""
        return self._last_success_time

