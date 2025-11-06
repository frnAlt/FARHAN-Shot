"""Network scanning functionality"""
import subprocess
import re
import logging
from typing import List, Optional
import time
from ..db.models import NetworkTarget
from ..db.database import VulnerabilityDatabase

logger = logging.getLogger("farhan_shot.scan")


class NetworkScanner:
    """WiFi network scanner"""
    
    def __init__(self, interface: str, vuln_db: VulnerabilityDatabase):
        """Initialize scanner
        
        Args:
            interface: WiFi interface name (e.g., wlan0)
            vuln_db: Vulnerability database instance
        """
        self.interface = interface
        self.vuln_db = vuln_db
        self.targets: List[NetworkTarget] = []
    
    def scan(self, timeout: int = 10) -> List[NetworkTarget]:
        """Scan for WiFi networks
        
        Args:
            timeout: Scan timeout in seconds
            
        Returns:
            List of discovered network targets
        """
        logger.info(f"Scanning for networks on {self.interface}...")
        
        try:
            # Use iw dev <interface> scan for scanning
            result = subprocess.run(
                ['iw', 'dev', self.interface, 'scan'],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode != 0:
                logger.error(f"Scan failed: {result.stderr}")
                return []
            
            # Parse scan results
            targets = self._parse_scan_results(result.stdout)
            
            # Enrich with vulnerability data
            for target in targets:
                self._enrich_target(target)
            
            # Sort by vulnerability score (highest first)
            targets.sort(key=lambda x: x.vulnerability_score, reverse=True)
            
            self.targets = targets
            logger.info(f"Found {len(targets)} networks, {sum(1 for t in targets if t.wps_enabled)} with WPS enabled")
            
            return targets
        
        except subprocess.TimeoutExpired:
            logger.error(f"Scan timed out after {timeout} seconds")
            return []
        except FileNotFoundError:
            logger.error("iw command not found. Please install iw: sudo apt install iw")
            return []
        except Exception as e:
            logger.error(f"Scan failed: {e}")
            return []
    
    def _parse_scan_results(self, output: str) -> List[NetworkTarget]:
        """Parse iw scan output
        
        Args:
            output: Output from iw scan command
            
        Returns:
            List of network targets
        """
        targets = []
        current_bss = {}
        
        for line in output.split('\n'):
            line = line.strip()
            
            # BSS line marks start of new network
            if line.startswith('BSS'):
                if current_bss:
                    target = self._create_target_from_bss(current_bss)
                    if target:
                        targets.append(target)
                current_bss = {}
                
                # Extract BSSID
                match = re.search(r'BSS ([0-9a-fA-F:]+)', line)
                if match:
                    current_bss['bssid'] = match.group(1)
            
            # SSID
            elif line.startswith('SSID:'):
                current_bss['ssid'] = line.split(':', 1)[1].strip()
            
            # Signal strength
            elif 'signal:' in line:
                match = re.search(r'signal: ([-\d.]+)', line)
                if match:
                    current_bss['signal'] = float(match.group(1))
            
            # Channel
            elif 'DS Parameter set: channel' in line:
                match = re.search(r'channel (\d+)', line)
                if match:
                    current_bss['channel'] = int(match.group(1))
            
            # WPS support
            elif 'WPS:' in line or 'Wi-Fi Protected Setup' in line:
                current_bss['wps'] = True
            
            # WPS locked state
            elif 'AP setup locked' in line.lower():
                current_bss['wps_locked'] = True
            
            # Encryption
            elif 'WPA' in line or 'RSN' in line:
                if 'encryption' not in current_bss:
                    current_bss['encryption'] = 'WPA/WPA2'
        
        # Add last BSS
        if current_bss:
            target = self._create_target_from_bss(current_bss)
            if target:
                targets.append(target)
        
        return targets
    
    def _create_target_from_bss(self, bss: dict) -> Optional[NetworkTarget]:
        """Create NetworkTarget from BSS data
        
        Args:
            bss: BSS data dictionary
            
        Returns:
            NetworkTarget or None if invalid
        """
        if 'bssid' not in bss:
            return None
        
        return NetworkTarget(
            ssid=bss.get('ssid', '<Hidden>'),
            bssid=bss['bssid'],
            channel=bss.get('channel', 0),
            signal_strength=int(bss.get('signal', -100)),
            encryption=bss.get('encryption', 'Unknown'),
            wps_enabled=bss.get('wps', False),
            wps_locked=bss.get('wps_locked', False)
        )
    
    def _enrich_target(self, target: NetworkTarget):
        """Enrich target with vulnerability data
        
        Args:
            target: Network target to enrich
        """
        # Look up in vulnerability database
        router = self.vuln_db.lookup(target.bssid)
        if router:
            target.vulnerable_router = router
            target.manufacturer = router.manufacturer
            target.vulnerability_score = self.vuln_db.get_vulnerability_score(target.bssid)
        else:
            # Try to identify manufacturer from OUI
            target.manufacturer = self._identify_manufacturer(target.bssid)
            target.vulnerability_score = 0.1 if target.wps_enabled else 0.0
        
        # Estimate distance from signal strength (rough calculation)
        target.distance_estimate = self._estimate_distance(target.signal_strength)
    
    def _identify_manufacturer(self, bssid: str) -> str:
        """Identify manufacturer from MAC address OUI
        
        Args:
            bssid: MAC address
            
        Returns:
            Manufacturer name or 'Unknown'
        """
        # Simple OUI lookup (could be enhanced with external database)
        oui_map = {
            "001D0F": "TP-Link",
            "001F3C": "TP-Link",
            "000C43": "Ralink",
            "54A050": "ASUS",
            "001B11": "D-Link",
            # Add more as needed
        }
        
        oui = bssid.replace(":", "").replace("-", "").upper()[:6]
        return oui_map.get(oui, "Unknown")
    
    def _estimate_distance(self, signal_dbm: int) -> float:
        """Estimate distance in meters from signal strength
        
        Args:
            signal_dbm: Signal strength in dBm
            
        Returns:
            Estimated distance in meters
        """
        # Simplified path loss model: d = 10^((TxPower - RSSI) / (10 * n))
        # Assuming TxPower = 20 dBm, n = 2.5 (indoor environment)
        tx_power = 20
        path_loss_exp = 2.5
        
        try:
            distance = 10 ** ((tx_power - signal_dbm) / (10 * path_loss_exp))
            return round(distance, 1)
        except:
            return 0.0
    
    def get_wps_enabled_targets(self) -> List[NetworkTarget]:
        """Get all WPS-enabled targets
        
        Returns:
            List of WPS-enabled targets
        """
        return [t for t in self.targets if t.wps_enabled]
    
    def get_vulnerable_targets(self, min_score: float = 0.5) -> List[NetworkTarget]:
        """Get vulnerable targets above threshold
        
        Args:
            min_score: Minimum vulnerability score
            
        Returns:
            List of vulnerable targets
        """
        return [t for t in self.targets if t.vulnerability_score >= min_score]
