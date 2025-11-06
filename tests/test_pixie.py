"""Unit tests for Pixie Dust module."""

import pytest
from src.pixie import PixieDustAttack, PixieData
from tests.simulated_pixie import PixiewpsSimulator


class TestPixieDustParsing:
    """Test Pixie Dust output parsing."""
    
    def test_parse_successful_attack(self):
        """Test parsing successful pixiewps output."""
        attack = PixieDustAttack(dry_run=True)
        output = PixiewpsSimulator.successful_attack("12345670")
        data = attack.parse_pixiewps_output(output)
        
        assert data.success is True
        assert data.pin == "12345670"
    
    def test_parse_failed_attack(self):
        """Test parsing failed pixiewps output."""
        attack = PixieDustAttack(dry_run=True)
        output = PixiewpsSimulator.failed_attack()
        data = attack.parse_pixiewps_output(output)
        
        assert data.success is False
        assert data.pin is None
        assert data.error_message == "WPS pin not found"
    
    def test_parse_hashes(self):
        """Test parsing E-Hash values."""
        attack = PixieDustAttack(dry_run=True)
        output = PixiewpsSimulator.with_hashes()
        data = attack.parse_pixiewps_output(output)
        
        assert data.e_hash1 is not None
        assert data.e_hash2 is not None
        assert len(data.e_hash1) > 0
        assert len(data.e_hash2) > 0
    
    def test_dry_run_simulation(self):
        """Test dry-run simulation mode."""
        attack = PixieDustAttack(dry_run=True)
        data = attack._simulate_pixiewps()
        
        assert data.success is True
        assert data.pin is not None
        assert data.e_hash1 is not None
        assert data.e_hash2 is not None
    
    def test_validate_pixie_data(self):
        """Test Pixie data validation."""
        attack = PixieDustAttack(dry_run=True)
        
        valid_data = PixieData(
            pke='aabbcc',
            pkr='ddeeff',
            e_hash1='112233',
            e_hash2='445566'
        )
        is_valid, missing = attack.validate_pixie_data(valid_data)
        assert is_valid is True
        assert len(missing) == 0
        
        invalid_data = PixieData(pke='aabbcc')
        is_valid, missing = attack.validate_pixie_data(invalid_data)
        assert is_valid is False
        assert len(missing) > 0
