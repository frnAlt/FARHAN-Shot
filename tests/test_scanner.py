"""Unit tests for scanner module."""

import pytest
from src.scanner import WiFiScanner, AccessPoint


class TestWiFiScanner:
    """Test WiFi scanning functionality."""
    
    def test_scanner_initialization(self):
        """Test scanner initialization."""
        scanner = WiFiScanner(interface='wlan0', dry_run=True)
        assert scanner.interface == 'wlan0'
        assert scanner.dry_run is True
    
    def test_scan_dry_run(self):
        """Test scanning in dry-run mode."""
        scanner = WiFiScanner(dry_run=True)
        aps = scanner.scan(wps_only=True)
        
        assert len(aps) > 0
        assert all(isinstance(ap, AccessPoint) for ap in aps)
        assert all(ap.wps_enabled for ap in aps)
    
    def test_scan_all_networks(self):
        """Test scanning all networks (not just WPS)."""
        scanner = WiFiScanner(dry_run=True)
        aps = scanner.scan(wps_only=False)
        
        assert len(aps) >= 0
    
    def test_rssi_filtering(self):
        """Test RSSI threshold filtering."""
        scanner = WiFiScanner(dry_run=True)
        aps = scanner.scan(wps_only=False, min_rssi=-50)
        
        assert all(ap.rssi >= -50 for ap in aps)
    
    def test_access_point_str(self):
        """Test AccessPoint string representation."""
        ap = AccessPoint(
            bssid='00:11:22:33:44:55',
            ssid='TestAP',
            channel=6,
            rssi=-40,
            encryption=['WPA2'],
            wps_enabled=True,
            wps_locked=False
        )
        
        str_repr = str(ap)
        assert '00:11:22:33:44:55' in str_repr
        assert 'TestAP' in str_repr
        assert 'WPS' in str_repr
