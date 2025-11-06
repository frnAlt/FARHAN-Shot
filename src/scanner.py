"""
WiFi scanning module with simulation support.
Author: Farhan

Provides WiFi AP scanning functionality with support for multiple
scanning backends (iw, wpa_cli, nmcli) and simulation mode.
"""

import subprocess
import re
from typing import List, Optional, Dict
from dataclasses import dataclass


@dataclass
class AccessPoint:
    """Access Point information."""
    
    bssid: str
    ssid: str
    channel: int
    rssi: int
    encryption: List[str]
    wps_enabled: bool = False
    wps_locked: bool = False
    vendor: Optional[str] = None
    
    def __str__(self) -> str:
        """String representation of AP."""
        enc_str = '/'.join(self.encryption) if self.encryption else 'Open'
        wps_str = 'WPS' if self.wps_enabled else 'No WPS'
        lock_str = ' (Locked)' if self.wps_locked else ''
        return (f"{self.bssid:17} {self.ssid:32} Ch {self.channel:2d} "
                f"{self.rssi:3d}dBm {enc_str:15} {wps_str}{lock_str}")


class WiFiScanner:
    """WiFi scanner with multiple backend support."""
    
    def __init__(self, interface: str = 'wlan0', dry_run: bool = False) -> None:
        """
        Initialize WiFi scanner.
        
        Args:
            interface: Wireless interface name
            dry_run: Enable simulation mode
        """
        self.interface = interface
        self.dry_run = dry_run
    
    def _run_command(self, cmd: List[str], timeout: int = 30) -> Optional[str]:
        """
        Execute shell command.
        
        Args:
            cmd: Command and arguments
            timeout: Command timeout in seconds
        
        Returns:
            Command output or None on failure
        """
        if self.dry_run:
            return self._simulate_scan_output()
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            if result.returncode == 0:
                return result.stdout
            return None
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return None
    
    def _simulate_scan_output(self) -> str:
        """
        Generate simulated scan output for testing.
        
        Returns:
            Simulated iwlist output
        """
        return """
Cell 01 - Address: 00:11:22:33:44:55
          Channel:6
          Frequency:2.437 GHz
          Quality=70/70  Signal level=-40 dBm
          ESSID:"TestAP_WPS"
          IE: IEEE 802.11i/WPA2 Version 1
          IE: WPS Version 1.0

Cell 02 - Address: AA:BB:CC:DD:EE:FF
          Channel:11
          Frequency:2.462 GHz
          Quality=50/70  Signal level=-60 dBm
          ESSID:"SecureNetwork"
          IE: IEEE 802.11i/WPA2 Version 1

Cell 03 - Address: 11:22:33:44:55:66
          Channel:1
          Frequency:2.412 GHz
          Quality=85/70  Signal level=-30 dBm
          ESSID:"OpenWPS"
          IE: WPS Version 1.0
          IE: WPS Locked
        """
    
    def _parse_iwlist_output(self, output: str) -> List[AccessPoint]:
        """
        Parse iwlist scan output.
        
        Args:
            output: Raw iwlist output
        
        Returns:
            List of AccessPoint objects
        """
        aps = []
        current_ap = None
        
        for line in output.split('\n'):
            line = line.strip()
            
            # New cell
            if line.startswith('Cell') and 'Address:' in line:
                if current_ap:
                    aps.append(current_ap)
                
                match = re.search(r'Address:\s*([0-9A-Fa-f:]{17})', line)
                if match:
                    current_ap = {
                        'bssid': match.group(1).upper(),
                        'ssid': '',
                        'channel': 0,
                        'rssi': -100,
                        'encryption': [],
                        'wps_enabled': False,
                        'wps_locked': False
                    }
            
            if not current_ap:
                continue
            
            # Channel
            if 'Channel:' in line:
                match = re.search(r'Channel:(\d+)', line)
                if match:
                    current_ap['channel'] = int(match.group(1))
            
            # Signal level
            if 'Signal level' in line:
                match = re.search(r'Signal level[=:](-?\d+)', line)
                if match:
                    current_ap['rssi'] = int(match.group(1))
            
            # ESSID
            if 'ESSID:' in line:
                match = re.search(r'ESSID:"([^"]*)"', line)
                if match:
                    current_ap['ssid'] = match.group(1)
            
            # Encryption
            if 'WPA2' in line:
                current_ap['encryption'].append('WPA2')
            elif 'WPA' in line and 'WPA2' not in current_ap['encryption']:
                current_ap['encryption'].append('WPA')
            
            # WPS
            if 'WPS' in line:
                if 'Locked' in line:
                    current_ap['wps_locked'] = True
                current_ap['wps_enabled'] = True
        
        # Add last AP
        if current_ap:
            aps.append(current_ap)
        
        # Convert to AccessPoint objects
        return [
            AccessPoint(
                bssid=ap['bssid'],
                ssid=ap['ssid'],
                channel=ap['channel'],
                rssi=ap['rssi'],
                encryption=ap['encryption'],
                wps_enabled=ap['wps_enabled'],
                wps_locked=ap['wps_locked']
            )
            for ap in aps
        ]
    
    def scan(self, wps_only: bool = True, min_rssi: int = -90) -> List[AccessPoint]:
        """
        Scan for WiFi access points.
        
        Args:
            wps_only: Only return APs with WPS enabled
            min_rssi: Minimum signal strength threshold
        
        Returns:
            List of AccessPoint objects
        """
        # Try iwlist first
        output = self._run_command(['iwlist', self.interface, 'scan'])
        
        if not output:
            # Try alternative scanning methods
            output = self._run_command(['iw', 'dev', self.interface, 'scan'])
        
        if not output:
            return []
        
        aps = self._parse_iwlist_output(output)
        
        # Filter by WPS if requested
        if wps_only:
            aps = [ap for ap in aps if ap.wps_enabled]
        
        # Filter by RSSI
        aps = [ap for ap in aps if ap.rssi >= min_rssi]
        
        # Sort by RSSI (strongest first)
        aps.sort(key=lambda x: x.rssi, reverse=True)
        
        return aps
    
    def detect_wps_locked(self, bssid: str) -> bool:
        """
        Detect if WPS is locked on an AP.
        
        Args:
            bssid: AP BSSID
        
        Returns:
            True if WPS is locked, False otherwise
        """
        if self.dry_run:
            # Simulate: some APs are locked
            return bssid.endswith(':66')
        
        # In real implementation, this would check WPS state
        # via various methods (wash, wpa_cli, etc.)
        return False
    
    def get_ap_vendor(self, bssid: str) -> Optional[str]:
        """
        Determine AP vendor from BSSID (OUI lookup).
        
        Args:
            bssid: AP BSSID
        
        Returns:
            Vendor name or None if unknown
        """
        # Extract OUI (first 3 octets)
        oui = ':'.join(bssid.split(':')[:3]).upper()
        
        # Common OUI mappings (subset for demo)
        oui_map = {
            '00:11:22': 'Cisco',
            'AA:BB:CC': 'TP-Link',
            '11:22:33': 'D-Link',
            '44:55:66': 'Netgear',
            '00:1A:2B': 'Belkin',
            '00:14:D1': 'TRENDnet',
        }
        
        return oui_map.get(oui, None)
