"""Rich Terminal UI for FARHAN-Shot"""
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.live import Live
from rich.layout import Layout
from rich import box
from typing import List
from ..db.models import NetworkTarget, AttackResult

console = Console()


class FarhanShotUI:
    """Modern terminal UI for WPS tool"""
    
    @staticmethod
    def show_banner():
        """Display tool banner"""
        banner = """
[bold cyan]╔═══════════════════════════════════════════════════════════╗[/]
[bold cyan]║[/] [bold red]FARHAN-SHOT[/] [bold white]v2.0[/] - [bold yellow]WPS Penetration Testing Tool[/]      [bold cyan]║[/]
[bold cyan]║[/] [dim]Modern Pixie Dust | PIN Prediction | Bruteforce[/]   [bold cyan]║[/]
[bold cyan]╚═══════════════════════════════════════════════════════════╝[/]
        """
        console.print(banner)
        console.print("[bold yellow]⚠️  For Educational & Authorized Penetration Testing Only[/]\n")
    
    @staticmethod
    def show_targets(targets: List[NetworkTarget]):
        """Display scanned network targets
        
        Args:
            targets: List of network targets
        """
        if not targets:
            console.print("[yellow]No networks found[/]")
            return
        
        table = Table(
            title="[bold cyan]Discovered Networks[/]",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold magenta"
        )
        
        table.add_column("#", style="dim", width=3)
        table.add_column("SSID", style="cyan", width=25)
        table.add_column("BSSID", style="white", width=17)
        table.add_column("Ch", justify="center", width=3)
        table.add_column("Signal", justify="right", width=7)
        table.add_column("Distance", justify="right", width=8)
        table.add_column("WPS", justify="center", width=5)
        table.add_column("Vuln", justify="center", width=5)
        table.add_column("Manufacturer", style="green", width=15)
        
        for i, target in enumerate(targets, 1):
            # Color code based on vulnerability
            vuln_color = "red" if target.vulnerability_score > 0.7 else "yellow" if target.vulnerability_score > 0.3 else "dim"
            wps_status = "[green]✓[/]" if target.wps_enabled else "[dim]✗[/]"
            wps_locked = "[red]LOCKED[/]" if target.wps_locked else wps_status
            
            # Vulnerability indicator
            if target.vulnerability_score > 0.7:
                vuln_indicator = "[bold red]HIGH[/]"
            elif target.vulnerability_score > 0.3:
                vuln_indicator = "[yellow]MED[/]"
            elif target.vulnerability_score > 0:
                vuln_indicator = "[dim]LOW[/]"
            else:
                vuln_indicator = "[dim]—[/]"
            
            # Signal strength color
            signal_color = "green" if target.signal_strength > -60 else "yellow" if target.signal_strength > -75 else "red"
            
            table.add_row(
                str(i),
                target.ssid if len(target.ssid) <= 25 else target.ssid[:22] + "...",
                f"[{vuln_color}]{target.bssid}[/]",
                str(target.channel),
                f"[{signal_color}]{target.signal_strength}dBm[/]",
                f"{target.distance_estimate:.0f}m" if target.distance_estimate else "—",
                wps_locked,
                vuln_indicator,
                target.manufacturer or "Unknown"
            )
        
        console.print(table)
        console.print(f"\n[bold]Total:[/] {len(targets)} networks | [green]WPS Enabled:[/] {sum(1 for t in targets if t.wps_enabled)}")
    
    @staticmethod
    def show_attack_start(target: NetworkTarget, attack_type: str):
        """Show attack start message
        
        Args:
            target: Network target
            attack_type: Type of attack
        """
        panel = Panel(
            f"[bold cyan]Target:[/] {target.ssid} ({target.bssid})\n"
            f"[bold cyan]Channel:[/] {target.channel}\n"
            f"[bold cyan]Signal:[/] {target.signal_strength} dBm\n"
            f"[bold cyan]Manufacturer:[/] {target.manufacturer or 'Unknown'}\n"
            f"[bold cyan]Attack Type:[/] {attack_type}",
            title=f"[bold red]Starting Attack[/]",
            border_style="red"
        )
        console.print(panel)
    
    @staticmethod
    def show_success(result: AttackResult):
        """Show successful attack result
        
        Args:
            result: Attack result
        """
        panel = Panel(
            f"[bold green]✓ Attack Successful![/]\n\n"
            f"[bold]SSID:[/] {result.target_ssid}\n"
            f"[bold]BSSID:[/] {result.target_bssid}\n"
            f"[bold yellow]WPS PIN:[/] {result.pin}\n"
            f"[bold yellow]Password:[/] {result.password}\n"
            f"[bold]Duration:[/] {result.duration:.1f}s\n"
            f"[bold]PINs Tried:[/] {result.pins_tried}",
            title="[bold green]SUCCESS[/]",
            border_style="green",
            box=box.DOUBLE
        )
        console.print(panel)
    
    @staticmethod
    def show_failure(result: AttackResult):
        """Show failed attack result
        
        Args:
            result: Attack result
        """
        panel = Panel(
            f"[bold red]✗ Attack Failed[/]\n\n"
            f"[bold]Target:[/] {result.target_ssid} ({result.target_bssid})\n"
            f"[bold]Duration:[/] {result.duration:.1f}s\n"
            f"[bold]PINs Tried:[/] {result.pins_tried}\n"
            f"[bold]Error:[/] {result.error_message or 'Unknown error'}",
            title="[bold red]FAILED[/]",
            border_style="red"
        )
        console.print(panel)
    
    @staticmethod
    def create_progress():
        """Create progress bar
        
        Returns:
            Progress instance
        """
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        )
    
    @staticmethod
    def show_error(message: str):
        """Show error message
        
        Args:
            message: Error message
        """
        console.print(f"[bold red]ERROR:[/] {message}")
    
    @staticmethod
    def show_warning(message: str):
        """Show warning message
        
        Args:
            message: Warning message
        """
        console.print(f"[bold yellow]WARNING:[/] {message}")
    
    @staticmethod
    def show_info(message: str):
        """Show info message
        
        Args:
            message: Info message
        """
        console.print(f"[bold cyan]INFO:[/] {message}")
