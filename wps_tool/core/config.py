"""Configuration management for FARHAN-Shot WPS Tool"""
import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class Config:
    """Main configuration for WPS tool"""
    
    # Interface settings
    interface: Optional[str] = None
    monitor_mode: bool = False  # Not required for this tool
    
    # Attack settings
    timeout: int = 30  # Attack timeout in seconds
    max_retries: int = 3
    retry_delay: int = 5  # Delay between retries in seconds
    
    # PIN generation
    use_suggested_pins: bool = True
    use_all_pins: bool = False
    max_pin_attempts: int = 50
    
    # Pixie Dust settings
    pixie_dust_enabled: bool = True
    pixie_dust_timeout: int = 60
    
    # Bruteforce settings
    online_bruteforce: bool = True
    offline_bruteforce: bool = True
    bruteforce_delay: float = 1.5  # Delay between PIN attempts
    
    # Long distance optimization
    tx_power_boost: bool = False  # Requires root
    long_distance_mode: bool = False
    signal_threshold: int = -80  # Minimum signal strength in dBm
    
    # Mobile optimization
    mobile_mode: bool = False
    battery_saving: bool = False
    adaptive_retry: bool = True
    
    # Database
    db_path: Path = field(default_factory=lambda: Path.home() / ".farhan_shot" / "wps.db")
    vuln_db_path: Path = field(default_factory=lambda: Path(__file__).parent.parent / "data" / "vulnwsc.txt")
    
    # Logging
    log_level: str = "INFO"
    log_file: Optional[Path] = None
    verbose: bool = False
    
    # Output
    output_file: Optional[Path] = None
    save_results: bool = True
    results_dir: Path = field(default_factory=lambda: Path.home() / ".farhan_shot" / "results")
    
    def __post_init__(self):
        """Create necessary directories"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        if self.log_file:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables"""
        return cls(
            interface=os.getenv("WPS_INTERFACE"),
            timeout=int(os.getenv("WPS_TIMEOUT", "30")),
            verbose=os.getenv("WPS_VERBOSE", "false").lower() == "true",
        )


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get global configuration instance"""
    global _config
    if _config is None:
        _config = Config()
    return _config


def set_config(config: Config):
    """Set global configuration instance"""
    global _config
    _config = config
