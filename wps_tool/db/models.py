"""Database models for FARHAN-Shot"""
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum
from datetime import datetime


class VulnType(Enum):
    """Vulnerability types"""
    PIXIE_DUST = "PD"
    COMPUTEPIN = "COMP"
    EASYBOX = "EASY"
    DLINK = "DLINK"
    ASUS = "ASUS"
    KNOWN_PIN = "KNOWN"
    WEAK_RANDOM = "WEAK"


@dataclass
class VulnerableRouter:
    """Represents a vulnerable router from database"""
    mac_prefix: str  # First 6 characters (OUI)
    manufacturer: str
    model: str
    vuln_types: List[VulnType]
    notes: str
    
    def is_vulnerable_to(self, vuln_type: VulnType) -> bool:
        """Check if router is vulnerable to specific attack"""
        return vuln_type in self.vuln_types
    
    def get_attack_priority(self) -> int:
        """Get attack priority (higher = more vulnerable)"""
        priority = 0
        if VulnType.PIXIE_DUST in self.vuln_types:
            priority += 10
        if VulnType.EASYBOX in self.vuln_types:
            priority += 5
        if VulnType.DLINK in self.vuln_types:
            priority += 4
        if VulnType.ASUS in self.vuln_types:
            priority += 4
        if VulnType.COMPUTEPIN in self.vuln_types:
            priority += 3
        return priority


@dataclass
class NetworkTarget:
    """Represents a WiFi network target"""
    ssid: str
    bssid: str  # MAC address
    channel: int
    signal_strength: int  # dBm
    encryption: str
    wps_enabled: bool
    wps_locked: bool
    manufacturer: Optional[str] = None
    vulnerability_score: float = 0.0
    vulnerable_router: Optional[VulnerableRouter] = None
    distance_estimate: Optional[float] = None  # meters
    
    def is_viable_target(self, signal_threshold: int = -80) -> bool:
        """Check if target is viable for attack"""
        return (
            self.wps_enabled and
            not self.wps_locked and
            self.signal_strength >= signal_threshold
        )


@dataclass
class AttackResult:
    """Represents an attack result"""
    target_ssid: str
    target_bssid: str
    attack_type: str
    success: bool
    pin: Optional[str] = None
    password: Optional[str] = None
    duration: float = 0.0  # seconds
    timestamp: Optional[datetime] = None
    error_message: Optional[str] = None
    pins_tried: int = 0
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
