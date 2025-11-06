"""
Logger module for consistent logging and timing utilities.
Author: Farhan

Provides consistent logging functions with timing capabilities
for tracking attack progress and performance metrics.
"""

import time
import sys
from typing import Optional, TextIO
from datetime import datetime


class Timer:
    """Simple timer for tracking operation duration."""
    
    def __init__(self) -> None:
        """Initialize timer."""
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
    
    def start(self) -> None:
        """Start the timer."""
        self.start_time = time.time()
        self.end_time = None
    
    def stop(self) -> None:
        """Stop the timer."""
        if self.start_time is None:
            raise RuntimeError("Timer not started")
        self.end_time = time.time()
    
    def elapsed(self) -> float:
        """
        Get elapsed time in seconds.
        
        Returns:
            Elapsed time in seconds
        """
        if self.start_time is None:
            return 0.0
        end = self.end_time if self.end_time is not None else time.time()
        return end - self.start_time
    
    def elapsed_formatted(self) -> str:
        """
        Get formatted elapsed time string.
        
        Returns:
            Formatted string like "12 s 345 ms"
        """
        elapsed = self.elapsed()
        seconds = int(elapsed)
        milliseconds = int((elapsed - seconds) * 1000)
        return f"{seconds} s {milliseconds} ms"


class Logger:
    """Centralized logger with file and console output support."""
    
    def __init__(self, verbose: bool = False, quiet: bool = False, 
                 log_file: Optional[str] = None) -> None:
        """
        Initialize logger.
        
        Args:
            verbose: Enable verbose output
            quiet: Suppress non-critical messages
            log_file: Optional file path for logging
        """
        self.verbose = verbose
        self.quiet = quiet
        self.log_file = log_file
        self.file_handle: Optional[TextIO] = None
        
        if log_file:
            try:
                self.file_handle = open(log_file, 'a', encoding='utf-8')
            except IOError as e:
                print(f"Warning: Could not open log file {log_file}: {e}", 
                      file=sys.stderr)
    
    def _write(self, message: str, to_stderr: bool = False) -> None:
        """
        Write message to console and/or file.
        
        Args:
            message: Message to write
            to_stderr: Write to stderr instead of stdout
        """
        stream = sys.stderr if to_stderr else sys.stdout
        print(message, file=stream)
        
        if self.file_handle:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.file_handle.write(f"[{timestamp}] {message}\n")
            self.file_handle.flush()
    
    def info(self, message: str) -> None:
        """Log informational message."""
        if not self.quiet:
            self._write(message)
    
    def verbose_info(self, message: str) -> None:
        """Log verbose informational message."""
        if self.verbose and not self.quiet:
            self._write(message)
    
    def error(self, message: str) -> None:
        """Log error message (always shown)."""
        self._write(message, to_stderr=True)
    
    def warning(self, message: str) -> None:
        """Log warning message."""
        if not self.quiet:
            self._write(message, to_stderr=True)
    
    def success(self, message: str) -> None:
        """Log success message."""
        if not self.quiet:
            self._write(message)
    
    def close(self) -> None:
        """Close log file handle."""
        if self.file_handle:
            self.file_handle.close()
            self.file_handle = None
    
    def __del__(self) -> None:
        """Cleanup file handle on deletion."""
        self.close()


# Global logger instance (can be configured by main)
_global_logger: Optional[Logger] = None


def init_logger(verbose: bool = False, quiet: bool = False, 
                log_file: Optional[str] = None) -> Logger:
    """
    Initialize global logger instance.
    
    Args:
        verbose: Enable verbose output
        quiet: Suppress non-critical messages
        log_file: Optional file path for logging
    
    Returns:
        Configured Logger instance
    """
    global _global_logger
    _global_logger = Logger(verbose, quiet, log_file)
    return _global_logger


def get_logger() -> Logger:
    """
    Get global logger instance.
    
    Returns:
        Logger instance (creates default if not initialized)
    """
    global _global_logger
    if _global_logger is None:
        _global_logger = Logger()
    return _global_logger
