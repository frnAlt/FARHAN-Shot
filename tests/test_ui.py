"""Unit tests for UI module."""

import pytest
from src.ui import UI, Colors, init_ui, get_ui


class TestUI:
    """Test UI functionality."""
    
    def test_ui_initialization(self):
        """Test UI initialization."""
        ui = UI(no_color=False)
        assert ui.no_color is False
    
    def test_no_color_mode(self):
        """Test no-color mode."""
        ui = UI(no_color=True)
        text = ui.success("test")
        assert text == "test"
    
    def test_color_markers(self):
        """Test colored markers."""
        ui = UI(no_color=False)
        
        assert '[i]' in ui.marker_info()
        assert '[+]' in ui.marker_success()
        assert '[-]' in ui.marker_error()
        assert '[!]' in ui.marker_warning()
        assert '[*]' in ui.marker_progress()
        assert '[?]' in ui.marker_question()
    
    def test_status_messages(self):
        """Test status message formatting."""
        ui = UI(no_color=False)
        
        assert 'vulnerable' in ui.status_vulnerable().lower()
        assert 'locked' in ui.status_locked().lower()
        assert 'stored' in ui.status_stored().lower()
    
    def test_progress_bar(self):
        """Test progress bar generation."""
        ui = UI(no_color=False)
        bar = ui.progress_bar(50, 100, width=20)
        
        assert '50%' in bar
        assert '50/100' in bar
    
    def test_global_ui(self):
        """Test global UI instance."""
        ui = init_ui(no_color=False)
        assert get_ui() is ui
