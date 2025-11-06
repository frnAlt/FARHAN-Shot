"""Unit tests for logger module."""

import pytest
import tempfile
from pathlib import Path
from src.logger import Timer, Logger, init_logger, get_logger


class TestTimer:
    """Test Timer functionality."""
    
    def test_timer_start_stop(self):
        """Test timer start and stop."""
        timer = Timer()
        timer.start()
        timer.stop()
        
        assert timer.elapsed() >= 0
    
    def test_timer_elapsed_running(self):
        """Test elapsed time while timer is running."""
        timer = Timer()
        timer.start()
        
        elapsed = timer.elapsed()
        assert elapsed >= 0
    
    def test_timer_formatted_output(self):
        """Test formatted time output."""
        timer = Timer()
        timer.start()
        timer.stop()
        
        formatted = timer.elapsed_formatted()
        assert 's' in formatted
        assert 'ms' in formatted


class TestLogger:
    """Test Logger functionality."""
    
    def test_logger_initialization(self):
        """Test logger initialization."""
        logger = Logger(verbose=True, quiet=False)
        assert logger.verbose is True
        assert logger.quiet is False
    
    def test_logger_with_file(self):
        """Test logger with file output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            logger = Logger(log_file=str(log_file))
            logger.info("Test message")
            logger.close()
            
            assert log_file.exists()
    
    def test_global_logger(self):
        """Test global logger instance."""
        logger = init_logger(verbose=True)
        assert get_logger() is logger
