"""Unit tests for PIN generation module."""

import pytest
from src.pingen import PINGenerator, PINCandidate


class TestPINGenerator:
    """Test PIN generation functionality."""
    
    def test_checksum_calculation(self):
        """Test WPS PIN checksum calculation."""
        assert PINGenerator.compute_checksum('1234567') == '12345670'
        assert PINGenerator.compute_checksum('0000000') == '00000000'
        assert PINGenerator.compute_checksum('8765432') == '87654325'
    
    def test_pin_validation(self):
        """Test PIN validation."""
        assert PINGenerator.validate_pin('12345670') is True
        assert PINGenerator.validate_pin('00000000') is True
        assert PINGenerator.validate_pin('12345678') is False
        assert PINGenerator.validate_pin('1234567') is False
        assert PINGenerator.validate_pin('abcdefgh') is False
    
    def test_common_pins_generation(self):
        """Test common PIN generation."""
        gen = PINGenerator()
        pins = gen.generate_common_pins()
        
        assert len(pins) > 0
        assert all(isinstance(p, PINCandidate) for p in pins)
        assert all(PINGenerator.validate_pin(p.pin) for p in pins)
        assert pins[0].score > pins[-1].score
    
    def test_prefix_generation(self):
        """Test PIN generation from prefix."""
        gen = PINGenerator()
        pins = gen.generate_from_prefix('1234', probability=5.0)
        
        assert len(pins) > 0
        assert all(p.pin.startswith('1234') for p in pins)
        assert all(PINGenerator.validate_pin(p.pin) for p in pins)
    
    def test_no_duplicate_pins(self):
        """Test that no duplicate PINs are generated."""
        gen = PINGenerator()
        pins = gen.generate_all()
        
        pin_values = [p.pin for p in pins]
        assert len(pin_values) == len(set(pin_values))
    
    def test_known_pins_priority(self):
        """Test that known PINs get highest priority."""
        gen = PINGenerator()
        known = ['12345670', '87654325']
        pins = gen.generate_all(known_pins=known)
        
        top_pins = [p.pin for p in pins[:2]]
        assert '12345670' in top_pins
        assert '87654325' in top_pins
        assert pins[0].score == 100.0 or pins[1].score == 100.0
