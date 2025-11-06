"""Advanced WPS PIN generation algorithms"""
import wpspin
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger("farhan_shot.pins")


@dataclass
class PinCandidate:
    """Represents a PIN candidate with metadata"""
    pin: str
    algorithm: str
    name: str
    confidence: float  # 0.0 to 1.0
    source: str  # 'algorithm', 'database', 'known'
    
    def __str__(self) -> str:
        return f"{self.pin} ({self.algorithm})"


class WPSPinGenerator:
    """Advanced WPS PIN generator with multiple algorithms"""
    
    # Known common PINs (ordered by likelihood)
    COMMON_PINS = [
        "12345670",  # Most common
        "00000000",
        "11111111",
        "12341234",
        "01234567",
        "11111117",
        "22222222",
        "33333333",
        "44444444",
        "55555555",
        "66666666",
        "77777777",
        "88888888",
        "99999999",
        "12345678",
        "87654321",
    ]
    
    # High-confidence vendor-specific PINs by OUI prefix
    VENDOR_PINS = {
        # Belkin known PINs
        "94:10:3E": ["20456008", "12345670"],
        "EC:1A:59": ["20456008", "12345670"],
        "08:86:3B": ["20456008"],
        
        # Some TP-Link models with known patterns
        "F4:F2:6D": ["12345670"],
        "C0:4A:00": ["12345670"],
        
        # ZyXEL known defaults
        "28:28:5D": ["28296607", "12345670"],
    }
    
    def __init__(self):
        """Initialize PIN generator with wpspin library"""
        self.wpspin_gen = wpspin.WPSpin()
        self.pin_cache: Dict[str, List[PinCandidate]] = {}
    
    def generate_all(self, mac: str, prioritize: bool = True) -> List[PinCandidate]:
        """Generate all possible PINs for a MAC address
        
        Args:
            mac: MAC address in format XX:XX:XX:XX:XX:XX
            prioritize: If True, return prioritized/suggested PINs first
            
        Returns:
            List of PIN candidates ordered by confidence
        """
        mac_normalized = mac.upper().replace(":", "").replace("-", "")
        
        if mac_normalized in self.pin_cache:
            logger.debug(f"Using cached PINs for {mac}")
            return self.pin_cache[mac_normalized]
        
        pins: List[PinCandidate] = []
        seen_pins = set()
        
        # 1. Check vendor-specific known PINs (highest confidence)
        oui = mac_normalized[:6]
        if oui in self.VENDOR_PINS:
            for pin in self.VENDOR_PINS[oui]:
                if pin not in seen_pins:
                    pins.append(PinCandidate(
                        pin=pin,
                        algorithm="vendor_known",
                        name="Vendor Known PIN",
                        confidence=0.95,
                        source="database"
                    ))
                    seen_pins.add(pin)
                    logger.debug(f"Added vendor-specific PIN for {oui}: {pin}")
        
        # 2. Get algorithm-generated PINs using wpspin
        try:
            if prioritize:
                suggested = self.wpspin_gen.getSuggested(mac)
            else:
                suggested = self.wpspin_gen.getAll(mac)
            
            if suggested:
                for pin_data in suggested:
                    pin = pin_data.get('pin', '')
                    if pin and pin not in seen_pins:
                        # Map algorithm IDs to readable names and confidence
                        algo_id = pin_data.get('id', 'unknown')
                        confidence = self._get_algorithm_confidence(algo_id)
                        
                        pins.append(PinCandidate(
                            pin=pin,
                            algorithm=algo_id,
                            name=pin_data.get('name', 'Unknown Algorithm'),
                            confidence=confidence,
                            source="algorithm"
                        ))
                        seen_pins.add(pin)
                        logger.debug(f"Generated PIN via {algo_id}: {pin}")
        except Exception as e:
            logger.warning(f"wpspin generation failed for {mac}: {e}")
        
        # 3. Add common PINs (medium-low confidence)
        for pin in self.COMMON_PINS:
            if pin not in seen_pins:
                pins.append(PinCandidate(
                    pin=pin,
                    algorithm="common",
                    name="Common PIN",
                    confidence=0.3,
                    source="known"
                ))
                seen_pins.add(pin)
        
        # 4. Additional algorithm implementations
        custom_pins = self._generate_custom_algorithms(mac)
        for pin_data in custom_pins:
            if pin_data.pin not in seen_pins:
                pins.append(pin_data)
                seen_pins.add(pin_data.pin)
        
        # Sort by confidence (highest first)
        pins.sort(key=lambda x: x.confidence, reverse=True)
        
        # Cache results
        self.pin_cache[mac_normalized] = pins
        
        logger.info(f"Generated {len(pins)} PIN candidates for {mac}")
        return pins
    
    def _get_algorithm_confidence(self, algo_id: str) -> float:
        """Map algorithm ID to confidence score"""
        confidence_map = {
            # High confidence algorithms (vendor-specific)
            'pinDLink': 0.85,
            'pinDLink1': 0.80,
            'pinASUS': 0.85,
            'pinAirocon': 0.75,
            'pinEasyBox': 0.90,  # Very high for EasyBox
            
            # Medium-high confidence (bit-based)
            'pin24': 0.65,
            'pin28': 0.65,
            'pin32': 0.65,
            'pin36': 0.60,
            'pin40': 0.60,
            'pin44': 0.55,
            'pin48': 0.55,
            
            # Medium confidence (generic algorithms)
            'pinInvNIC': 0.50,
            'pinNIC2': 0.50,
            'pinNIC3': 0.50,
            'pinOUIaddNIC': 0.45,
            'pinOUIsubNIC': 0.45,
            'pinOUIxorNIC': 0.45,
        }
        return confidence_map.get(algo_id, 0.40)
    
    def _generate_custom_algorithms(self, mac: str) -> List[PinCandidate]:
        """Implement additional custom PIN generation algorithms"""
        pins = []
        mac_normalized = mac.upper().replace(":", "").replace("-", "")
        
        try:
            # ComputePIN algorithm (Zaochesung)
            nic = int(mac_normalized[6:], 16)  # Last 6 hex digits
            pin_7digit = nic % 10000000
            checksum = self._wps_checksum(pin_7digit)
            computepin = f"{pin_7digit}{checksum}"
            
            pins.append(PinCandidate(
                pin=computepin,
                algorithm="computepin",
                name="ComputePIN (Zaochesung)",
                confidence=0.70,
                source="algorithm"
            ))
        except Exception as e:
            logger.debug(f"ComputePIN generation failed: {e}")
        
        return pins
    
    @staticmethod
    def _wps_checksum(pin_7digit: int) -> int:
        """Calculate WPS PIN checksum (8th digit)
        
        Based on hostapd/wpa_supplicant implementation
        """
        accum = 0
        pin = pin_7digit
        
        while pin:
            accum += 3 * (pin % 10)
            pin //= 10
            accum += (pin % 10)
            pin //= 10
        
        digit = accum % 10
        return (10 - digit) % 10
    
    def get_suggested_pins(self, mac: str, max_pins: int = 20) -> List[PinCandidate]:
        """Get suggested high-confidence PINs
        
        Args:
            mac: MAC address
            max_pins: Maximum number of PINs to return
            
        Returns:
            Top N PIN candidates by confidence
        """
        all_pins = self.generate_all(mac, prioritize=True)
        return all_pins[:max_pins]
    
    def get_pin_stats(self, mac: str) -> Dict[str, int]:
        """Get statistics about generated PINs
        
        Returns:
            Dictionary with PIN generation statistics
        """
        pins = self.generate_all(mac)
        
        sources = {}
        algorithms = {}
        
        for pin in pins:
            sources[pin.source] = sources.get(pin.source, 0) + 1
            algorithms[pin.algorithm] = algorithms.get(pin.algorithm, 0) + 1
        
        return {
            "total_pins": len(pins),
            "sources": sources,
            "algorithms": algorithms,
            "avg_confidence": sum(p.confidence for p in pins) / len(pins) if pins else 0,
            "max_confidence": max((p.confidence for p in pins), default=0),
        }
