"""
WPA supplicant control interface wrapper.
Author: Farhan

Provides abstraction layer for wpa_supplicant interaction with
dry-run simulation mode for offline testing.
"""

import subprocess
import time
from typing import Optional, List, Dict, Tuple
from dataclasses import dataclass
from enum import Enum


class WPSMessageType(Enum):
    """WPS EAPOL message types."""
    M1 = "M1"
    M2 = "M2"
    M3 = "M3"
    M4 = "M4"
    M5 = "M5"
    M6 = "M6"
    M7 = "M7"
    M8 = "M8"


@dataclass
class WPAResponse:
    """Response from WPA supplicant operation."""
    
    success: bool
    message: str
    data: Optional[Dict[str, str]] = None
    error_code: Optional[str] = None


class WPAController:
    """WPA supplicant control wrapper with simulation support."""
    
    def __init__(self, interface: str = 'wlan0', dry_run: bool = False) -> None:
        """
        Initialize WPA controller.
        
        Args:
            interface: Wireless interface name
            dry_run: Enable simulation mode
        """
        self.interface = interface
        self.dry_run = dry_run
        self.associated = False
        self.current_bssid: Optional[str] = None
    
    def _run_wpa_cli(self, *args: str, timeout: int = 10) -> Tuple[bool, str]:
        """
        Execute wpa_cli command.
        
        Args:
            *args: Command arguments
            timeout: Command timeout in seconds
        
        Returns:
            Tuple of (success, output)
        """
        if self.dry_run:
            return self._simulate_wpa_cli(*args)
        
        cmd = ['wpa_cli', '-i', self.interface] + list(args)
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode == 0, result.stdout
        except subprocess.TimeoutExpired:
            return False, "Command timeout"
        except FileNotFoundError:
            return False, "wpa_cli not found"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def _simulate_wpa_cli(self, *args: str) -> Tuple[bool, str]:
        """
        Simulate wpa_cli command for testing.
        
        Args:
            *args: Command arguments
        
        Returns:
            Tuple of (success, simulated output)
        """
        command = args[0] if args else ''
        
        if command == 'status':
            return True, "wpa_state=COMPLETED\nssid=TestAP\nbssid=00:11:22:33:44:55"
        elif command == 'scan':
            return True, "OK"
        elif command == 'scan_results':
            return True, "bssid / frequency / signal level / flags / ssid\n" \
                        "00:11:22:33:44:55\t2412\t-45\t[WPA2-PSK-CCMP][WPS][ESS]\tTestAP"
        elif command == 'add_network':
            return True, "0"
        elif command == 'set_network':
            return True, "OK"
        elif command == 'select_network':
            return True, "OK"
        elif command == 'wps_reg':
            time.sleep(0.1)
            return True, "OK"
        elif command == 'remove_network':
            return True, "OK"
        else:
            return True, "OK"
    
    def scan_networks(self) -> WPAResponse:
        """
        Trigger network scan.
        
        Returns:
            WPAResponse with scan status
        """
        success, output = self._run_wpa_cli('scan')
        return WPAResponse(
            success=success,
            message=output.strip()
        )
    
    def get_scan_results(self) -> List[Dict[str, str]]:
        """
        Get scan results from wpa_supplicant.
        
        Returns:
            List of dictionaries with AP information
        """
        success, output = self._run_wpa_cli('scan_results')
        
        if not success:
            return []
        
        aps = []
        lines = output.strip().split('\n')[1:]  # Skip header
        
        for line in lines:
            parts = line.split('\t')
            if len(parts) >= 5:
                aps.append({
                    'bssid': parts[0],
                    'frequency': parts[1],
                    'signal': parts[2],
                    'flags': parts[3],
                    'ssid': parts[4] if len(parts) > 4 else ''
                })
        
        return aps
    
    def associate_ap(self, bssid: str, ssid: str) -> WPAResponse:
        """
        Associate with an access point.
        
        Args:
            bssid: AP BSSID
            ssid: AP SSID
        
        Returns:
            WPAResponse with association status
        """
        # Add network
        success, net_id = self._run_wpa_cli('add_network')
        if not success:
            return WPAResponse(
                success=False,
                message="Failed to add network",
                error_code="ADD_NETWORK_FAILED"
            )
        
        net_id = net_id.strip()
        
        # Set SSID
        self._run_wpa_cli('set_network', net_id, 'ssid', f'"{ssid}"')
        
        # Set BSSID
        self._run_wpa_cli('set_network', net_id, 'bssid', bssid)
        
        # Set key management to WPS
        self._run_wpa_cli('set_network', net_id, 'key_mgmt', 'WPS')
        
        # Select network
        success, _ = self._run_wpa_cli('select_network', net_id)
        
        if success:
            self.associated = True
            self.current_bssid = bssid
            return WPAResponse(
                success=True,
                message="Associated successfully",
                data={'network_id': net_id}
            )
        else:
            return WPAResponse(
                success=False,
                message="Association failed",
                error_code="ASSOCIATION_FAILED"
            )
    
    def send_wps_pin(self, bssid: str, pin: str) -> WPAResponse:
        """
        Send WPS PIN to AP.
        
        Args:
            bssid: AP BSSID
            pin: 8-digit WPS PIN
        
        Returns:
            WPAResponse with PIN attempt status
        """
        success, output = self._run_wpa_cli('wps_reg', bssid, pin, timeout=30)
        
        # Check for specific error patterns (backward compatible)
        if 'wrong PIN code' in output.lower() or 'failed' in output.lower():
            return WPAResponse(
                success=False,
                message="[-] Error: wrong PIN code",
                error_code="WRONG_PIN"
            )
        elif success and ('ok' in output.lower() or self.dry_run):
            return WPAResponse(
                success=True,
                message="[+] PIN accepted",
                data={'pin': pin}
            )
        else:
            return WPAResponse(
                success=False,
                message=f"PIN attempt failed: {output}",
                error_code="PIN_FAILED"
            )
    
    def disconnect(self) -> WPAResponse:
        """
        Disconnect from current AP.
        
        Returns:
            WPAResponse with disconnect status
        """
        success, output = self._run_wpa_cli('disconnect')
        self.associated = False
        self.current_bssid = None
        
        return WPAResponse(
            success=success,
            message="Disconnected" if success else "Disconnect failed"
        )
    
    def remove_network(self, network_id: str) -> WPAResponse:
        """
        Remove configured network.
        
        Args:
            network_id: Network ID to remove
        
        Returns:
            WPAResponse with removal status
        """
        success, output = self._run_wpa_cli('remove_network', network_id)
        
        return WPAResponse(
            success=success,
            message="Network removed" if success else "Removal failed"
        )
    
    def get_status(self) -> Dict[str, str]:
        """
        Get current connection status.
        
        Returns:
            Dictionary with status information
        """
        success, output = self._run_wpa_cli('status')
        
        if not success:
            return {}
        
        status = {}
        for line in output.split('\n'):
            if '=' in line:
                key, value = line.split('=', 1)
                status[key.strip()] = value.strip()
        
        return status
