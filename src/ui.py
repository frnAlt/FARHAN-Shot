"""
Terminal UI module with colorized output matching OneShot-Extended style.
Author: Farhan

Provides consistent color schemes, markers, and progress indicators
for terminal-based user interaction.
"""

from typing import Optional
from colorama import Fore, Back, Style, init as colorama_init


# Initialize colorama
colorama_init(autoreset=True)


class Colors:
    """Color definitions matching OneShot-Extended style."""
    
    # Main colors
    RED = Fore.RED
    GREEN = Fore.GREEN
    YELLOW = Fore.YELLOW
    BLUE = Fore.BLUE
    MAGENTA = Fore.MAGENTA
    CYAN = Fore.CYAN
    WHITE = Fore.WHITE
    GRAY = Fore.LIGHTBLACK_EX
    
    # Backgrounds
    BG_RED = Back.RED
    BG_GREEN = Back.GREEN
    BG_YELLOW = Back.YELLOW
    
    # Styles
    BOLD = Style.BRIGHT
    DIM = Style.DIM
    RESET = Style.RESET_ALL


class UI:
    """Terminal UI helper with color support."""
    
    def __init__(self, no_color: bool = False) -> None:
        """
        Initialize UI helper.
        
        Args:
            no_color: Disable colored output
        """
        self.no_color = no_color
    
    def _colorize(self, text: str, color: str) -> str:
        """
        Apply color to text if colors enabled.
        
        Args:
            text: Text to colorize
            color: Color code from Colors class
        
        Returns:
            Colorized text or plain text if colors disabled
        """
        if self.no_color:
            return text
        return f"{color}{text}{Colors.RESET}"
    
    def success(self, text: str) -> str:
        """Format success message (green)."""
        return self._colorize(text, Colors.GREEN)
    
    def error(self, text: str) -> str:
        """Format error message (red)."""
        return self._colorize(text, Colors.RED)
    
    def warning(self, text: str) -> str:
        """Format warning message (yellow)."""
        return self._colorize(text, Colors.YELLOW)
    
    def info(self, text: str) -> str:
        """Format info message (cyan)."""
        return self._colorize(text, Colors.CYAN)
    
    def highlight(self, text: str) -> str:
        """Format highlighted text (bold white)."""
        return self._colorize(text, Colors.BOLD + Colors.WHITE)
    
    def dim(self, text: str) -> str:
        """Format dimmed text (gray)."""
        return self._colorize(text, Colors.GRAY)
    
    def bssid(self, text: str) -> str:
        """Format BSSID (cyan)."""
        return self._colorize(text, Colors.CYAN)
    
    def ssid(self, text: str) -> str:
        """Format SSID (white bold)."""
        return self._colorize(text, Colors.BOLD + Colors.WHITE)
    
    def marker_info(self) -> str:
        """Get info marker [i]."""
        return self._colorize("[i]", Colors.BLUE)
    
    def marker_success(self) -> str:
        """Get success marker [+]."""
        return self._colorize("[+]", Colors.GREEN)
    
    def marker_error(self) -> str:
        """Get error marker [-]."""
        return self._colorize("[-]", Colors.RED)
    
    def marker_warning(self) -> str:
        """Get warning marker [!]."""
        return self._colorize("[!]", Colors.YELLOW)
    
    def marker_progress(self) -> str:
        """Get progress marker [*]."""
        return self._colorize("[*]", Colors.CYAN)
    
    def marker_question(self) -> str:
        """Get question marker [?]."""
        return self._colorize("[?]", Colors.MAGENTA)
    
    def header(self, text: str, width: int = 60) -> str:
        """
        Create a formatted header.
        
        Args:
            text: Header text
            width: Total width of header
        
        Returns:
            Formatted header string
        """
        separator = "=" * width
        padded_text = text.center(width)
        return (
            f"{self._colorize(separator, Colors.CYAN)}\n"
            f"{self._colorize(padded_text, Colors.BOLD + Colors.WHITE)}\n"
            f"{self._colorize(separator, Colors.CYAN)}"
        )
    
    def section(self, text: str) -> str:
        """
        Create a section header.
        
        Args:
            text: Section text
        
        Returns:
            Formatted section header
        """
        return self._colorize(f"\n{'─' * 50}\n{text}\n{'─' * 50}", 
                             Colors.YELLOW)
    
    def status_vulnerable(self) -> str:
        """Get 'Possibly vulnerable' status."""
        return self._colorize("Possibly vulnerable", Colors.GREEN)
    
    def status_locked(self) -> str:
        """Get 'WPS locked' status."""
        return self._colorize("WPS locked", Colors.RED)
    
    def status_stored(self) -> str:
        """Get 'Already stored' status."""
        return self._colorize("Already stored", Colors.YELLOW)
    
    def progress_bar(self, current: int, total: int, width: int = 40) -> str:
        """
        Create a simple text-based progress bar.
        
        Args:
            current: Current progress value
            total: Total value
            width: Width of progress bar in characters
        
        Returns:
            Formatted progress bar string
        """
        if total == 0:
            percentage = 0
        else:
            percentage = int((current / total) * 100)
        
        filled = int((current / total) * width) if total > 0 else 0
        bar = "█" * filled + "░" * (width - filled)
        
        return (
            f"{self._colorize(bar, Colors.CYAN)} "
            f"{percentage}% ({current}/{total})"
        )
    
    def banner(self) -> str:
        """
        Get application banner.
        
        Returns:
            Formatted banner string
        """
        banner_text = """
╔══════════════════════════════════════════════════════════╗
║              WPS Penetration Testing Toolkit            ║
║                     by Farhan                            ║
║          Professional WPS PIN Recovery Tool              ║
╚══════════════════════════════════════════════════════════╝
        """
        return self._colorize(banner_text, Colors.CYAN + Colors.BOLD)


# Global UI instance
_global_ui: Optional[UI] = None


def init_ui(no_color: bool = False) -> UI:
    """
    Initialize global UI instance.
    
    Args:
        no_color: Disable colored output
    
    Returns:
        Configured UI instance
    """
    global _global_ui
    _global_ui = UI(no_color)
    return _global_ui


def get_ui() -> UI:
    """
    Get global UI instance.
    
    Returns:
        UI instance (creates default if not initialized)
    """
    global _global_ui
    if _global_ui is None:
        _global_ui = UI()
    return _global_ui
