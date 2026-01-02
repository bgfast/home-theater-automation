"""GPIO monitoring with debouncing."""

import time
import logging
from typing import Callable, Optional

try:
    from gpiozero import DigitalInputDevice
except ImportError:
    # Fallback for non-Pi environments (testing)
    DigitalInputDevice = None

logger = logging.getLogger(__name__)


class GPIOMonitor:
    """Monitor GPIO pin with debouncing.
    
    The trigger is ACTIVE-LOW: GPIO LOW = trigger ON, GPIO HIGH = trigger OFF.
    Uses internal pull-up resistor.
    """
    
    def __init__(self, pin: int, debounce_ms: int, callback: Callable[[bool], None]):
        """Initialize GPIO monitor.
        
        Args:
            pin: GPIO pin number (e.g., 17)
            debounce_ms: Debounce interval in milliseconds
            callback: Function called with (is_triggered: bool) when state changes
        """
        self.pin = pin
        self.debounce_ms = debounce_ms / 1000.0  # Convert to seconds
        self.callback = callback
        self._last_state: Optional[bool] = None
        self._last_change_time = 0.0
        self._pending_state: Optional[bool] = None
        self._device: Optional[DigitalInputDevice] = None
        self._running = False
        
        if DigitalInputDevice is None:
            logger.warning("gpiozero not available - GPIO monitoring disabled (likely not on Raspberry Pi)")
            return
        
        # Create input device with pull-up
        # Note: With pull_up=True, pin is HIGH when idle, LOW when triggered (active-low)
        # We'll invert the logic manually since active_low parameter isn't available in all gpiozero versions
        try:
            self._device = DigitalInputDevice(
                pin=pin,
                pull_up=True
            )
            # Invert the callbacks: when device is deactivated (goes LOW), trigger is ON
            self._device.when_deactivated = self._on_activated  # LOW = trigger ON
            self._device.when_activated = self._on_deactivated   # HIGH = trigger OFF
            logger.info(f"GPIO monitor initialized on pin {pin} (active-low, pull-up enabled)")
        except Exception as e:
            logger.error(f"Failed to initialize GPIO pin {pin}: {e}")
            raise
    
    def _on_activated(self):
        """Called when GPIO goes LOW (trigger ON)."""
        self._handle_state_change(True)
    
    def _on_deactivated(self):
        """Called when GPIO goes HIGH (trigger OFF)."""
        self._handle_state_change(False)
    
    def _handle_state_change(self, new_state: bool):
        """Handle state change with debouncing."""
        current_time = time.time()
        
        if self._pending_state is None:
            # First change, start debounce timer
            self._pending_state = new_state
            self._last_change_time = current_time
            logger.debug(f"GPIO state change detected: {new_state}, starting debounce")
        elif self._pending_state == new_state:
            # Same state, reset timer
            self._last_change_time = current_time
        else:
            # Different state, reset timer
            self._pending_state = new_state
            self._last_change_time = current_time
        
        # Check if debounce period has elapsed
        if current_time - self._last_change_time >= self.debounce_ms:
            if self._last_state != self._pending_state:
                # State has changed
                self._last_state = self._pending_state
                self._pending_state = None
                logger.info(f"GPIO state confirmed: trigger {'ON' if self._last_state else 'OFF'}")
                if self.callback:
                    self.callback(self._last_state)
    
    def read_state(self) -> Optional[bool]:
        """Read current GPIO state (True = trigger ON, False = trigger OFF).
        
        Returns None if GPIO is not available.
        """
        if self._device is None:
            return None
        try:
            # With pull_up=True: is_active=True means HIGH (trigger OFF), is_active=False means LOW (trigger ON)
            # So we invert: LOW (False) = trigger ON (True), HIGH (True) = trigger OFF (False)
            return not self._device.is_active
        except Exception as e:
            logger.error(f"Error reading GPIO state: {e}")
            return None
    
    def start(self):
        """Start monitoring (device is already active, this just marks as running)."""
        self._running = True
        # Read initial state
        initial_state = self.read_state()
        if initial_state is not None:
            self._last_state = initial_state
            logger.info(f"GPIO monitor started, initial state: trigger {'ON' if initial_state else 'OFF'}")
    
    def stop(self):
        """Stop monitoring and close GPIO device."""
        self._running = False
        if self._device:
            try:
                self._device.close()
                logger.info("GPIO monitor stopped")
            except Exception as e:
                logger.error(f"Error closing GPIO device: {e}")
    
    def is_running(self) -> bool:
        """Check if monitor is running."""
        return self._running

