"""
Simulated wpa_supplicant/wpa_cli output generator for testing.
Author: Farhan

Provides realistic wpa_supplicant interaction simulation for offline
testing of WPA control logic without actual hardware.
"""

from typing import Optional


class WPASimulator:
    """Simulate wpa_cli command outputs."""
    
    @staticmethod
    def scan_results() -> str:
        """Generate scan results output."""
        return """bssid / frequency / signal level / flags / ssid
00:11:22:33:44:55\t2412\t-45\t[WPA2-PSK-CCMP][WPS][ESS]\tTestAP_WPS
AA:BB:CC:DD:EE:FF\t2437\t-60\t[WPA2-PSK-CCMP][ESS]\tSecureNetwork
11:22:33:44:55:66\t2462\t-30\t[WPA2-PSK-CCMP][WPS][ESS]\tOpenWPS
"""
    
    @staticmethod
    def status_connected() -> str:
        """Generate connected status output."""
        return """wpa_state=COMPLETED
ssid=TestAP_WPS
bssid=00:11:22:33:44:55
freq=2412
key_mgmt=WPA2-PSK
ip_address=192.168.1.100
"""
    
    @staticmethod
    def status_disconnected() -> str:
        """Generate disconnected status output."""
        return """wpa_state=DISCONNECTED
"""
    
    @staticmethod
    def wps_success() -> str:
        """Generate successful WPS PIN attempt output."""
        return """OK
WPS-SUCCESS
CTRL-EVENT-CONNECTED - Connection to 00:11:22:33:44:55 completed
"""
    
    @staticmethod
    def wps_wrong_pin() -> str:
        """Generate wrong PIN output."""
        return """OK
WPS-FAIL msg=18 config_error=18
CTRL-EVENT-DISCONNECTED bssid=00:11:22:33:44:55 reason=3
"""
    
    @staticmethod
    def wps_locked() -> str:
        """Generate WPS locked output."""
        return """OK
WPS-AP-LOCKED
CTRL-EVENT-DISCONNECTED bssid=00:11:22:33:44:55 reason=3
"""
    
    @staticmethod
    def add_network() -> str:
        """Generate add network response."""
        return "0"
    
    @staticmethod
    def generic_ok() -> str:
        """Generate generic OK response."""
        return "OK"
    
    @staticmethod
    def generic_fail() -> str:
        """Generate generic FAIL response."""
        return "FAIL"


class WPSMessageSimulator:
    """Simulate WPS EAPOL message exchange."""
    
    @staticmethod
    def m2_message() -> bytes:
        """Generate simulated M2 message with sample data."""
        return b"\x02\x00\x00\x00" + b"WPS_M2_DATA" + b"\x00" * 100
    
    @staticmethod
    def m4_message() -> bytes:
        """Generate simulated M4 message."""
        return b"\x04\x00\x00\x00" + b"WPS_M4_DATA" + b"\x00" * 100
    
    @staticmethod
    def m6_message() -> bytes:
        """Generate simulated M6 message."""
        return b"\x06\x00\x00\x00" + b"WPS_M6_DATA" + b"\x00" * 100
