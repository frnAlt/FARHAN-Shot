#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FARHAN-SHOT v2.0 - Modern WPS WiFi Penetration Testing Tool
By FARHAN MUH TASIM (@Gtajisan)
For Educational and Authorized Penetration Testing Only
"""

import sys
import subprocess
import os
import re
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# ============================================
# ANSI Color Codes (Original FARHAN-Shot Style)
# ============================================
red = "\033[1;31m"
green = "\033[1;32m"
yellow = "\033[1;33m"
blue = "\033[1;34m"
magenta = "\033[1;35m"
cyan = "\033[1;36m"
white = "\033[1;97m"
reset = "\033[0m"
bold = "\033[1m"
underline = "\033[4m"

# Status indicators (Original style)
ok = f'{green}[{white}+{green}]{reset}'
err = f'{red}[{white}-{red}]{reset}'
ask = f'{cyan}[{white}?{cyan}]{reset}'
info = f'{blue}[{white}i{blue}]{reset}'
warn = f'{yellow}[{white}!{yellow}]{reset}'

# ============================================
# Banner
# ============================================
def show_banner():
    banner = f"""
{cyan}╔═══════════════════════════════════════════════════════════╗{reset}
{cyan}║{reset} {bold}{red}FARHAN-SHOT{reset} {bold}{white}v2.0{reset} - {bold}{yellow}WPS Penetration Testing Tool{reset}      {cyan}║{reset}
{cyan}║{reset} {blue}Modern Pixie Dust | PIN Prediction | Bruteforce{reset}   {cyan}║{reset}
{cyan}╚═══════════════════════════════════════════════════════════╝{reset}
{bold}{yellow}⚠️  For Educational & Authorized Penetration Testing Only{reset}
    """
    print(banner)

# ============================================
# WPS PIN Generator (Multiple Algorithms)
# ============================================
class WPSPinGenerator:
    """Advanced WPS PIN generator with multiple algorithms"""
    
    # Common PINs
    COMMON_PINS = [
        "12345670", "00000000", "11111111", "12341234",
        "01234567", "11111117", "22222222", "33333333"
    ]
    
    # Vendor-specific known PINs
    VENDOR_PINS = {
        "94103E": ["20456008", "12345670"],
        "EC1A59": ["20456008", "12345670"],
        "282850": ["28296607", "12345670"],
    }
    
    @staticmethod
    def checksum(pin):
        """Calculate WPS PIN checksum"""
        accum = 0
        while pin:
            accum += 3 * (pin % 10)
            pin //= 10
            accum += pin % 10
            pin //= 10
        return (10 - accum % 10) % 10
    
    @staticmethod
    def generate_all(mac: str) -> List[Dict]:
        """Generate all possible PINs for MAC address"""
        pins = []
        mac_int = int(mac.replace(":", "").replace("-", "")[6:], 16)
        oui = mac.replace(":", "").replace("-", "")[:6].upper()
        
        # Vendor-specific PINs
        if oui in WPSPinGenerator.VENDOR_PINS:
            for pin in WPSPinGenerator.VENDOR_PINS[oui]:
                pins.append({"pin": pin, "name": "Vendor Known", "confidence": 0.95})
        
        # ComputePIN algorithm
        try:
            pin_7 = mac_int % 10000000
            checksum = WPSPinGenerator.checksum(pin_7)
            pins.append({
                "pin": f"{pin_7}{checksum}",
                "name": "ComputePIN",
                "confidence": 0.70
            })
        except:
            pass
        
        # 24/28/32-bit PINs
        for bits in [24, 28, 32]:
            try:
                pin_7 = (mac_int & ((1 << bits) - 1)) % 10000000
                checksum = WPSPinGenerator.checksum(pin_7)
                pins.append({
                    "pin": f"{pin_7}{checksum}",
                    "name": f"{bits}-bit PIN",
                    "confidence": 0.65
                })
            except:
                pass
        
        # Common PINs
        for pin in WPSPinGenerator.COMMON_PINS:
            pins.append({"pin": pin, "name": "Common PIN", "confidence": 0.30})
        
        # Sort by confidence
        pins.sort(key=lambda x: x["confidence"], reverse=True)
        return pins

# ============================================
# Vulnerability Database
# ============================================
VULN_DATABASE = {
    # TP-Link (2025 confirmed vulnerable)
    "00149D": {"vendor": "TP-Link", "vuln": "HIGH"},
    "001F3C": {"vendor": "TP-Link", "vuln": "HIGH"},
    "085700": {"vendor": "TP-Link", "vuln": "HIGH"},
    "14CF92": {"vendor": "TP-Link", "vuln": "HIGH"},
    "1CFA68": {"vendor": "TP-Link", "vuln": "HIGH"},
    "4CEDFB": {"vendor": "TP-Link", "vuln": "HIGH"},
    
    # D-Link
    "001B11": {"vendor": "D-Link", "vuln": "HIGH"},
    "14D64D": {"vendor": "D-Link", "vuln": "HIGH"},
    "1C7EE5": {"vendor": "D-Link", "vuln": "MEDIUM"},
    
    # ASUS
    "04D4C4": {"vendor": "ASUS", "vuln": "HIGH"},
    "08606E": {"vendor": "ASUS", "vuln": "HIGH"},
    "54A050": {"vendor": "ASUS", "vuln": "HIGH"},
    
    # Netgear
    "08BD43": {"vendor": "Netgear", "vuln": "MEDIUM"},
    "200CC8": {"vendor": "Netgear", "vuln": "MEDIUM"},
    
    # Realtek chipset
    "00E04C": {"vendor": "Realtek", "vuln": "HIGH"},
    "521000": {"vendor": "Realtek", "vuln": "HIGH"},
}

def lookup_vulnerability(bssid: str) -> Dict:
    """Look up vulnerability in database"""
    oui = bssid.replace(":", "").replace("-", "")[:6].upper()
    return VULN_DATABASE.get(oui, {"vendor": "Unknown", "vuln": "LOW"})

# ============================================
# Network Scanner
# ============================================
def scan_networks(interface: str) -> List[Dict]:
    """Scan for WiFi networks using iw"""
    print(f"{info} Scanning networks on {cyan}{interface}{reset}...")
    
    try:
        result = subprocess.run(
            ['iw', 'dev', interface, 'scan'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            print(f"{err} Scan failed: {result.stderr}")
            return []
        
        networks = parse_scan_output(result.stdout)
        print(f"{ok} Found {green}{len(networks)}{reset} networks")
        return networks
        
    except subprocess.TimeoutExpired:
        print(f"{err} Scan timed out")
        return []
    except FileNotFoundError:
        print(f"{err} {yellow}iw{reset} not found. Install: {cyan}sudo apt install iw{reset}")
        return []
    except Exception as e:
        print(f"{err} Scan error: {e}")
        return []

def parse_scan_output(output: str) -> List[Dict]:
    """Parse iw scan output"""
    networks = []
    current = {}
    
    for line in output.split('\n'):
        line = line.strip()
        
        if line.startswith('BSS'):
            if current:
                networks.append(current)
            current = {}
            match = re.search(r'BSS ([0-9a-fA-F:]+)', line)
            if match:
                current['bssid'] = match.group(1).upper()
        
        elif line.startswith('SSID:'):
            current['ssid'] = line.split(':', 1)[1].strip() or '<Hidden>'
        
        elif 'signal:' in line:
            match = re.search(r'signal: ([-\d.]+)', line)
            if match:
                current['signal'] = int(float(match.group(1)))
        
        elif 'DS Parameter set: channel' in line:
            match = re.search(r'channel (\d+)', line)
            if match:
                current['channel'] = int(match.group(1))
        
        elif 'WPS:' in line or 'Wi-Fi Protected Setup' in line:
            current['wps'] = True
        
        elif 'AP setup locked' in line.lower():
            current['wps_locked'] = True
    
    if current:
        networks.append(current)
    
    return networks

# ============================================
# Display Functions
# ============================================
def display_networks(networks: List[Dict]):
    """Display networks in a table"""
    if not networks:
        print(f"{warn} No networks found")
        return
    
    # Header
    print(f"\n{cyan}{'='*80}{reset}")
    print(f"{bold}{white}{'#':<4} {'SSID':<25} {'BSSID':<18} {'CH':<4} {'Signal':<8} {'WPS':<6} {'Vuln'}{reset}")
    print(f"{cyan}{'='*80}{reset}")
    
    # Networks
    for i, net in enumerate(networks, 1):
        ssid = net.get('ssid', '<Hidden>')[:24]
        bssid = net.get('bssid', 'N/A')
        channel = net.get('channel', 0)
        signal = net.get('signal', -100)
        wps = net.get('wps', False)
        locked = net.get('wps_locked', False)
        
        # Vulnerability check
        vuln_info = lookup_vulnerability(bssid)
        vendor = vuln_info['vendor']
        vuln_level = vuln_info['vuln']
        
        # Color coding
        if vuln_level == "HIGH":
            bssid_color = red
            vuln_text = f"{red}{bold}HIGH{reset}"
        elif vuln_level == "MEDIUM":
            bssid_color = yellow
            vuln_text = f"{yellow}MED{reset}"
        else:
            bssid_color = white
            vuln_text = f"{white}LOW{reset}"
        
        # WPS status
        if locked:
            wps_status = f"{red}LOCK{reset}"
        elif wps:
            wps_status = f"{green}YES{reset}"
        else:
            wps_status = f"{white}NO{reset}"
        
        # Signal color
        if signal > -60:
            sig_color = green
        elif signal > -75:
            sig_color = yellow
        else:
            sig_color = red
        
        print(f"{cyan}{i:<4}{reset} {white}{ssid:<25}{reset} {bssid_color}{bssid:<18}{reset} "
              f"{white}{channel:<4}{reset} {sig_color}{signal:>3}dBm{reset:5} {wps_status:<12} {vuln_text}")
    
    print(f"{cyan}{'='*80}{reset}\n")

def display_attack_start(target: Dict):
    """Display attack start info"""
    print(f"\n{cyan}{'='*60}{reset}")
    print(f"{bold}{red}STARTING ATTACK{reset}")
    print(f"{cyan}{'='*60}{reset}")
    print(f"{info} Target SSID: {yellow}{target.get('ssid', 'N/A')}{reset}")
    print(f"{info} Target BSSID: {yellow}{target.get('bssid', 'N/A')}{reset}")
    print(f"{info} Channel: {yellow}{target.get('channel', 'N/A')}{reset}")
    print(f"{info} Signal: {yellow}{target.get('signal', 'N/A')} dBm{reset}")
    vuln = lookup_vulnerability(target.get('bssid', ''))
    print(f"{info} Vendor: {yellow}{vuln['vendor']}{reset}")
    print(f"{info} Vulnerability: {yellow}{vuln['vuln']}{reset}")
    print(f"{cyan}{'='*60}{reset}\n")

def display_success(ssid: str, bssid: str, pin: str, password: str, duration: float):
    """Display success message"""
    print(f"\n{green}{'='*60}{reset}")
    print(f"{bold}{green}✓ ATTACK SUCCESSFUL!{reset}")
    print(f"{green}{'='*60}{reset}")
    print(f"{ok} SSID: {white}{ssid}{reset}")
    print(f"{ok} BSSID: {white}{bssid}{reset}")
    print(f"{ok} WPS PIN: {bold}{yellow}{pin}{reset}")
    print(f"{ok} Password: {bold}{yellow}{password}{reset}")
    print(f"{ok} Duration: {white}{duration:.1f}s{reset}")
    print(f"{green}{'='*60}{reset}\n")
    
    # Save to file
    save_result(ssid, bssid, pin, password)

def display_failure(duration: float, pins_tried: int):
    """Display failure message"""
    print(f"\n{red}{'='*60}{reset}")
    print(f"{bold}{red}✗ ATTACK FAILED{reset}")
    print(f"{red}{'='*60}{reset}")
    print(f"{err} No valid PIN found")
    print(f"{info} Duration: {white}{duration:.1f}s{reset}")
    print(f"{info} PINs tried: {white}{pins_tried}{reset}")
    print(f"{red}{'='*60}{reset}\n")

# ============================================
# Attack Functions
# ============================================
def wps_attack(bssid: str, interface: str, max_pins: int = 20):
    """Perform WPS PIN attack"""
    start_time = time.time()
    
    # Generate PINs
    print(f"{info} Generating PIN candidates for {cyan}{bssid}{reset}...")
    pins = WPSPinGenerator.generate_all(bssid)
    pins = pins[:max_pins]
    
    print(f"{ok} Generated {green}{len(pins)}{reset} PIN candidates")
    print(f"{info} Top PINs by confidence:")
    for i, p in enumerate(pins[:5], 1):
        print(f"   {cyan}{i}.{reset} {yellow}{p['pin']}{reset} - {white}{p['name']}{reset} ({p['confidence']:.0%})")
    
    print(f"\n{info} Starting PIN bruteforce attack...\n")
    
    # Try each PIN
    for i, pin_data in enumerate(pins, 1):
        pin = pin_data['pin']
        print(f"{ask} Trying PIN {cyan}{i}/{len(pins)}{reset}: {yellow}{pin}{reset} ({pin_data['name']})...")
        
        # Simulate attack (in real implementation, use wpa_supplicant)
        # This is a placeholder - actual implementation requires root and wpa_supplicant
        time.sleep(0.5)  # Simulate delay
        
        # For demo purposes, we'll simulate success on certain conditions
        # In real implementation, this would call wpa_cli to attempt connection
        
    duration = time.time() - start_time
    display_failure(duration, len(pins))

def save_result(ssid: str, bssid: str, pin: str, password: str):
    """Save successful attack result"""
    results_dir = Path.home() / ".farhan_shot"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "results.txt"
    
    timestamp = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
    
    entry = f"""
➠ TOOL: FARHAN-Shot v2.0 by @Gtajisan
➠ SSID: {ssid}
➠ BSSID: {bssid}
➠ PIN: {pin}
➠ Password: {password}
➠ TIME: {timestamp}
{'─'*60}
"""
    
    try:
        with open(results_file, 'a') as f:
            f.write(entry)
        print(f"{ok} Results saved to: {cyan}{results_file}{reset}")
    except Exception as e:
        print(f"{err} Failed to save results: {e}")

# ============================================
# Info Functions
# ============================================
def show_info():
    """Show tool information"""
    show_banner()
    
    print(f"{info} Vulnerability Database: {green}{len(VULN_DATABASE)}{reset} entries")
    print(f"{info} Supported Vendors: {green}TP-Link, D-Link, ASUS, Netgear, Realtek{reset}")
    print(f"{info} PIN Algorithms: {green}ComputePIN, 24/28/32-bit, Vendor-specific{reset}")
    print(f"{info} Attack Methods: {green}Online Bruteforce, PIN Prediction{reset}")
    
    results_file = Path.home() / ".farhan_shot" / "results.txt"
    if results_file.exists():
        print(f"{info} Results saved in: {cyan}{results_file}{reset}")
    
    print(f"\n{yellow}Requirements:{reset}")
    print(f"  • Root access (sudo)")
    print(f"  • wpa_supplicant, iw, pixiewps")
    print(f"  • Python 3.6+")
    
    print(f"\n{yellow}Usage:{reset}")
    print(f"  {cyan}python main.py scan -i wlan0{reset}          # Scan networks")
    print(f"  {cyan}python main.py attack -b <BSSID> -i wlan0{reset}  # Attack target")
    print(f"  {cyan}python main.py info{reset}                    # Show this info")

# ============================================
# Main CLI
# ============================================
def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='FARHAN-Shot v2.0 - WPS Penetration Testing Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Scan command
    scan_parser = subparsers.add_parser('scan', help='Scan for WiFi networks')
    scan_parser.add_argument('-i', '--interface', required=True, help='WiFi interface (e.g., wlan0)')
    scan_parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    
    # Attack command
    attack_parser = subparsers.add_parser('attack', help='Perform WPS attack')
    attack_parser.add_argument('-i', '--interface', required=True, help='WiFi interface')
    attack_parser.add_argument('-b', '--bssid', required=True, help='Target BSSID')
    attack_parser.add_argument('-m', '--max-pins', type=int, default=20, help='Max PINs to try')
    attack_parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Show tool information')
    
    args = parser.parse_args()
    
    # Show banner
    if args.command != 'info':
        show_banner()
    
    # Execute command
    if args.command == 'scan':
        networks = scan_networks(args.interface)
        display_networks(networks)
        
        # Show vulnerable targets
        wps_networks = [n for n in networks if n.get('wps') and not n.get('wps_locked')]
        if wps_networks:
            print(f"{ok} Found {green}{len(wps_networks)}{reset} WPS-enabled targets!")
            
            vuln_targets = []
            for net in wps_networks:
                vuln = lookup_vulnerability(net.get('bssid', ''))
                if vuln['vuln'] in ['HIGH', 'MEDIUM']:
                    vuln_targets.append(net)
            
            if vuln_targets:
                print(f"{warn} {red}{len(vuln_targets)}{reset} highly vulnerable targets detected!")
    
    elif args.command == 'attack':
        print(f"{warn} {yellow}Root access required for WPS attacks!{reset}")
        print(f"{info} This is a demonstration version")
        
        target = {
            'ssid': 'Target',
            'bssid': args.bssid,
            'channel': 6,
            'signal': -50
        }
        
        display_attack_start(target)
        wps_attack(args.bssid, args.interface, args.max_pins)
    
    elif args.command == 'info':
        show_info()
    
    else:
        show_banner()
        parser.print_help()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{warn} Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n{err} Error: {e}")
        sys.exit(1)
