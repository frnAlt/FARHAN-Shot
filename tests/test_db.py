"""Unit tests for database module."""

import pytest
import tempfile
import json
from pathlib import Path
from src.db import VulnerabilityDB, APRecord, VendorPattern


class TestVulnerabilityDB:
    """Test vulnerability database functionality."""
    
    def test_json_database_creation(self):
        """Test JSON database creation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.json"
            db = VulnerabilityDB(str(db_path))
            
            # Database is created on first write operation
            ap = APRecord(bssid='00:11:22:33:44:55', ssid='Test')
            db.add_ap(ap)
            
            assert db_path.exists()
            db.close()
    
    def test_add_and_lookup_ap(self):
        """Test adding and looking up AP records."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.json"
            db = VulnerabilityDB(str(db_path))
            
            ap = APRecord(
                bssid='00:11:22:33:44:55',
                ssid='TestAP',
                vendor='TestVendor',
                known_pins=['12345670']
            )
            
            db.add_ap(ap)
            retrieved = db.lookup_ap('00:11:22:33:44:55')
            
            assert retrieved is not None
            assert retrieved.bssid == '00:11:22:33:44:55'
            assert retrieved.ssid == 'TestAP'
            assert '12345670' in retrieved.known_pins
            
            db.close()
    
    def test_vendor_patterns(self):
        """Test vendor pattern management."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.json"
            db = VulnerabilityDB(str(db_path))
            
            pattern = VendorPattern(
                vendor='Cisco',
                prefixes=['1234', '5678'],
                patterns=['1234####'],
                probability_score=8.5
            )
            
            db.add_vendor_pattern(pattern)
            retrieved = db.lookup_vendor_patterns('Cisco')
            
            assert retrieved is not None
            assert retrieved.vendor == 'Cisco'
            assert '1234' in retrieved.prefixes
            assert retrieved.probability_score == 8.5
            
            db.close()
    
    def test_case_insensitive_lookup(self):
        """Test case-insensitive BSSID lookup."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.json"
            db = VulnerabilityDB(str(db_path))
            
            ap = APRecord(bssid='AA:BB:CC:DD:EE:FF', ssid='Test')
            db.add_ap(ap)
            
            retrieved = db.lookup_ap('aa:bb:cc:dd:ee:ff')
            assert retrieved is not None
            assert retrieved.bssid == 'AA:BB:CC:DD:EE:FF'
            
            db.close()
