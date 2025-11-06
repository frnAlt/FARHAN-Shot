"""
PIN generation module with intelligent vendor-pattern scoring.
Author: Farhan

Implements smart PIN generation using vendor patterns, prefix optimization,
and probability-based ranking for efficient WPS PIN discovery.
"""

import re
from typing import List, Tuple, Optional, Set, Dict, Any
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class PINCandidate:
    """PIN candidate with metadata."""
    
    pin: str
    score: float
    source: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class PINGenerator:
    """Intelligent PIN generator with vendor pattern support."""
    
    # Common PIN patterns (OneShot/OneShot-Extended inspired)
    COMMON_PINS = [
        '12345670',  # Most common default
        '00000000',
        '11111111',
        '12345678',
        '87654321',
        '01234567',
        '76543210',
    ]
    
    # Checksum calculation for WPS PINs
    @staticmethod
    def compute_checksum(pin: str) -> str:
        """
        Compute WPS PIN checksum digit.
        
        Args:
            pin: 7-digit PIN string
        
        Returns:
            Complete 8-digit PIN with checksum
        """
        if len(pin) != 7:
            raise ValueError("PIN must be 7 digits for checksum calculation")
        
        accum = 0
        for i, digit in enumerate(pin):
            accum += int(digit) * (3 if i % 2 == 0 else 1)
        
        checksum = (10 - (accum % 10)) % 10
        return pin + str(checksum)
    
    @staticmethod
    def validate_pin(pin: str) -> bool:
        """
        Validate WPS PIN format and checksum.
        
        Args:
            pin: 8-digit PIN string
        
        Returns:
            True if valid, False otherwise
        """
        if not re.match(r'^\d{8}$', pin):
            return False
        
        try:
            computed = PINGenerator.compute_checksum(pin[:7])
            return computed == pin
        except ValueError:
            return False
    
    def __init__(self) -> None:
        """Initialize PIN generator."""
        self.generated_pins: Set[str] = set()
    
    def generate_common_pins(self) -> List[PINCandidate]:
        """
        Generate list of common default PINs.
        
        Returns:
            List of PINCandidate objects with high scores
        """
        candidates = []
        for i, pin in enumerate(self.COMMON_PINS):
            if self.validate_pin(pin):
                score = 10.0 - (i * 0.5)  # Higher score for more common
                candidates.append(PINCandidate(
                    pin=pin,
                    score=score,
                    source='common_default',
                    metadata={'index': i}
                ))
                self.generated_pins.add(pin)
        return candidates
    
    def generate_from_prefix(self, prefix: str, 
                            probability: float = 5.0) -> List[PINCandidate]:
        """
        Generate PINs from vendor prefix pattern.
        
        Args:
            prefix: PIN prefix (e.g., '1234' for vendor pattern)
            probability: Base score for this prefix
        
        Returns:
            List of PINCandidate objects
        """
        candidates = []
        prefix = prefix.strip()
        
        # Generate all possible completions
        if len(prefix) >= 7:
            # Just add checksum
            try:
                pin = self.compute_checksum(prefix[:7])
                if pin not in self.generated_pins:
                    candidates.append(PINCandidate(
                        pin=pin,
                        score=probability,
                        source='prefix_exact',
                        metadata={'prefix': prefix}
                    ))
                    self.generated_pins.add(pin)
            except ValueError:
                pass
        elif len(prefix) < 7:
            # Generate common patterns to complete
            suffix_patterns = ['000', '123', '999', '111', '012', '321']
            
            for suffix in suffix_patterns:
                base = (prefix + suffix + '0000000')[:7]
                try:
                    pin = self.compute_checksum(base)
                    if pin not in self.generated_pins:
                        candidates.append(PINCandidate(
                            pin=pin,
                            score=probability * 0.8,
                            source='prefix_pattern',
                            metadata={'prefix': prefix, 'suffix': suffix}
                        ))
                        self.generated_pins.add(pin)
                except ValueError:
                    pass
        
        return candidates
    
    def generate_date_based(self, year_range: Tuple[int, int] = (2010, 2025),
                           probability: float = 3.0) -> List[PINCandidate]:
        """
        Generate date-based PINs (YYYYMMDD pattern).
        
        Args:
            year_range: Tuple of (start_year, end_year)
            probability: Base score for date patterns
        
        Returns:
            List of PINCandidate objects
        """
        candidates = []
        current_year = datetime.now().year
        
        # Focus on recent years (more likely to be default)
        for year in range(max(year_range[0], current_year - 5), 
                         min(year_range[1], current_year) + 1):
            for month in [1, 6, 12]:  # Sample months
                for day in [1, 15]:  # Sample days
                    date_str = f"{year:04d}{month:02d}{day:02d}"[:7]
                    try:
                        pin = self.compute_checksum(date_str)
                        if pin not in self.generated_pins:
                            candidates.append(PINCandidate(
                                pin=pin,
                                score=probability,
                                source='date_pattern',
                                metadata={'date': date_str}
                            ))
                            self.generated_pins.add(pin)
                    except ValueError:
                        pass
        
        return candidates
    
    def generate_sequential(self, probability: float = 2.0) -> List[PINCandidate]:
        """
        Generate sequential number patterns.
        
        Args:
            probability: Base score for sequential patterns
        
        Returns:
            List of PINCandidate objects
        """
        candidates = []
        
        # Ascending/descending sequences
        patterns = [
            '0123456', '1234567', '2345678', '3456789',
            '9876543', '8765432', '7654321', '6543210',
        ]
        
        for pattern in patterns:
            try:
                pin = self.compute_checksum(pattern)
                if pin not in self.generated_pins:
                    candidates.append(PINCandidate(
                        pin=pin,
                        score=probability,
                        source='sequential',
                        metadata={'pattern': pattern}
                    ))
                    self.generated_pins.add(pin)
            except ValueError:
                pass
        
        return candidates
    
    def generate_from_vendor_pattern(self, vendor: str, 
                                     pattern_data: dict,
                                     probability: float = 7.0) -> List[PINCandidate]:
        """
        Generate PINs based on vendor-specific patterns.
        
        Args:
            vendor: Vendor name
            pattern_data: Dictionary with 'prefixes' and 'patterns' keys
            probability: Base score for vendor patterns
        
        Returns:
            List of PINCandidate objects
        """
        candidates = []
        
        # Generate from prefixes
        for prefix in pattern_data.get('prefixes', []):
            prefix_candidates = self.generate_from_prefix(prefix, probability)
            for candidate in prefix_candidates:
                candidate.metadata['vendor'] = vendor
                candidates.append(candidate)
        
        # Generate from pattern templates
        for pattern in pattern_data.get('patterns', []):
            # Pattern might be like "MODEL####" where # = digits
            if '#' in pattern:
                # Replace # with common digit sequences
                digit_sequences = ['0000', '1234', '9999', '0123']
                base_pattern = pattern.replace('#', '')
                
                for seq in digit_sequences:
                    pin_base = (base_pattern + seq + '0000000')[:7]
                    try:
                        pin = self.compute_checksum(pin_base)
                        if pin not in self.generated_pins:
                            candidates.append(PINCandidate(
                                pin=pin,
                                score=probability * 0.9,
                                source='vendor_pattern',
                                metadata={'vendor': vendor, 'pattern': pattern}
                            ))
                            self.generated_pins.add(pin)
                    except ValueError:
                        pass
        
        return candidates
    
    def generate_all(self, vendor: Optional[str] = None,
                    vendor_patterns: Optional[dict] = None,
                    known_pins: Optional[List[str]] = None,
                    max_candidates: int = 10000) -> List[PINCandidate]:
        """
        Generate comprehensive list of PIN candidates ordered by probability.
        
        Args:
            vendor: Vendor name if known
            vendor_patterns: Vendor pattern data
            known_pins: List of known working PINs for this AP
            max_candidates: Maximum number of candidates to generate
        
        Returns:
            List of PINCandidate objects sorted by score (descending)
        """
        all_candidates = []
        
        # Known PINs get highest priority
        if known_pins:
            for pin in known_pins:
                if self.validate_pin(pin) and pin not in self.generated_pins:
                    all_candidates.append(PINCandidate(
                        pin=pin,
                        score=100.0,
                        source='known_pin',
                        metadata={'known': True}
                    ))
                    self.generated_pins.add(pin)
        
        # Vendor-specific patterns (high priority)
        if vendor and vendor_patterns:
            all_candidates.extend(
                self.generate_from_vendor_pattern(vendor, vendor_patterns, 15.0)
            )
        
        # Common default PINs
        all_candidates.extend(self.generate_common_pins())
        
        # Date-based patterns
        all_candidates.extend(self.generate_date_based(probability=3.0))
        
        # Sequential patterns
        all_candidates.extend(self.generate_sequential(probability=2.0))
        
        # Sort by score (descending) and limit
        all_candidates.sort(key=lambda x: x.score, reverse=True)
        return all_candidates[:max_candidates]
    
    def reset(self) -> None:
        """Reset generated PIN tracking."""
        self.generated_pins.clear()
