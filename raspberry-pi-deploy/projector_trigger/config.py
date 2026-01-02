"""Configuration loading and validation."""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class Config:
    """Configuration manager for projector trigger bridge."""
    
    DEFAULT_CONFIG = {
        'gpio': {
            'pin': 17,
            'debounce_ms': 300,
        },
        'projector': {
            'ip': None,  # Optional: specify IP directly
            'mac': None,  # Optional: specify MAC address for auto-discovery
            'port': 53595,
            'power_on_command': 'power "on"',
            'power_off_command': 'power "off"',
            'timeout_seconds': 1.5,
            'max_retries': 3,
            'retry_backoff_seconds': 0.5,
        },
        'denon': {
            'ip': None,  # Optional: specify IP directly
            'mac': None,  # Optional: specify MAC address for auto-discovery
            'port': 23,
            'poll_interval_off': 5.0,
            'poll_interval_on': 2.0,
        },
        'projector_http': {
            'username': 'root',
            'port': 80,
        },
        'logging': {
            'level': 'INFO',
        }
    }
    
    def __init__(self, config_path: str = None):
        """Initialize configuration.
        
        Args:
            config_path: Path to YAML config file. If None, tries:
                - /opt/projector-trigger/config.yaml
                - ./config.yaml
        """
        if config_path is None:
            # Try standard locations
            if os.path.exists('/opt/projector-trigger/config.yaml'):
                config_path = '/opt/projector-trigger/config.yaml'
            elif os.path.exists('./config.yaml'):
                config_path = './config.yaml'
            else:
                config_path = None
        
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                user_config = yaml.safe_load(f) or {}
        else:
            user_config = {}
        
        # Merge with defaults
        self._config = self._merge_config(self.DEFAULT_CONFIG, user_config)
    
    @staticmethod
    def _merge_config(default: Dict, user: Dict) -> Dict:
        """Recursively merge user config into default."""
        result = default.copy()
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = Config._merge_config(result[key], value)
            else:
                result[key] = value
        return result
    
    @property
    def gpio_pin(self) -> int:
        """GPIO pin number."""
        return self._config['gpio']['pin']
    
    @property
    def debounce_ms(self) -> int:
        """Debounce interval in milliseconds."""
        return self._config['gpio']['debounce_ms']
    
    @property
    def projector_ip(self) -> Optional[str]:
        """Projector IP address (if specified directly)."""
        return self._config['projector'].get('ip')
    
    @property
    def projector_mac(self) -> Optional[str]:
        """Projector MAC address (for auto-discovery)."""
        return self._config['projector'].get('mac')
    
    @property
    def projector_port(self) -> int:
        """Projector TCP port."""
        return self._config['projector']['port']
    
    @property
    def power_on_command(self) -> str:
        """Power on command string."""
        return self._config['projector']['power_on_command']
    
    @property
    def power_off_command(self) -> str:
        """Power off command string."""
        return self._config['projector']['power_off_command']
    
    @property
    def timeout_seconds(self) -> float:
        """TCP timeout per attempt."""
        return self._config['projector']['timeout_seconds']
    
    @property
    def max_retries(self) -> int:
        """Maximum retry attempts."""
        return self._config['projector']['max_retries']
    
    @property
    def retry_backoff_seconds(self) -> float:
        """Base backoff delay between retries."""
        return self._config['projector']['retry_backoff_seconds']
    
    @property
    def log_level(self) -> str:
        """Logging level."""
        return self._config['logging']['level']
    
    @property
    def denon_ip(self) -> Optional[str]:
        """Denon AVR IP address (if specified directly)."""
        return self._config.get('denon', {}).get('ip')
    
    @property
    def denon_mac(self) -> Optional[str]:
        """Denon AVR MAC address (for auto-discovery)."""
        return self._config.get('denon', {}).get('mac')
    
    @property
    def denon_port(self) -> int:
        """Denon AVR telnet port."""
        return self._config.get('denon', {}).get('port', 23)
    
    @property
    def denon_poll_interval_off(self) -> float:
        """Polling interval when Denon is off (seconds)."""
        return self._config.get('denon', {}).get('poll_interval_off', 5.0)
    
    @property
    def denon_poll_interval_on(self) -> float:
        """Polling interval when Denon is on (seconds)."""
        return self._config.get('denon', {}).get('poll_interval_on', 2.0)
    
    @property
    def projector_http_username(self) -> str:
        """HTTP web interface username."""
        return self._config.get('projector_http', {}).get('username', 'root')
    
    @property
    def projector_http_port(self) -> int:
        """HTTP web interface port."""
        return self._config.get('projector_http', {}).get('port', 80)
    
    def get_all(self) -> Dict[str, Any]:
        """Get full configuration dictionary."""
        return self._config.copy()

