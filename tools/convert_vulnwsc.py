#!/usr/bin/env python3
"""
Convert vulnwsc.txt to structured vulnerability database.
Author: Farhan

Converts legacy vulnwsc.txt format to modern JSON/SQLite database
with vendor patterns, known PINs, and metadata.
"""

import json
import argparse
import sys
from pathlib import Path
from typing import List, Dict, Any


def parse_vulnwsc_line(line: str) -> Dict[str, Any]:
    """
    Parse a single line from vulnwsc.txt.
    
    Args:
        line: Line from vulnwsc.txt
    
    Returns:
        Dictionary with AP information
    """
    parts = line.strip().split('|')
    
    if len(parts) < 3:
        return None
    
    return {
        'bssid': parts[0].strip(),
        'ssid': parts[1].strip() if len(parts) > 1 else '',
        'known_pins': [p.strip() for p in parts[2].split(',') if p.strip()] if len(parts) > 2 else [],
        'vendor': parts[3].strip() if len(parts) > 3 else None,
        'model': parts[4].strip() if len(parts) > 4 else None,
        'pin_patterns': [],
        'wps_version': None,
        'last_seen': None,
        'flags': {}
    }


def create_sample_database() -> Dict[str, Any]:
    """
    Create sample vulnerability database with example data.
    
    Returns:
        Database dictionary structure
    """
    return {
        'aps': [
            {
                'bssid': '00:11:22:33:44:55',
                'ssid': 'TestAP_WPS',
                'vendor': 'Cisco',
                'model': 'E1200',
                'known_pins': ['12345670', '56789012'],
                'pin_patterns': ['1234****', '5678****'],
                'wps_version': '1.0',
                'last_seen': '2025-11-06',
                'flags': {'vulnerable': True}
            },
            {
                'bssid': 'AA:BB:CC:DD:EE:FF',
                'ssid': 'TPLink_Vulnerable',
                'vendor': 'TP-Link',
                'model': 'TL-WR841N',
                'known_pins': ['28296607'],
                'pin_patterns': ['2829****'],
                'wps_version': '1.0',
                'last_seen': '2025-11-05',
                'flags': {'vulnerable': True}
            },
            {
                'bssid': '11:22:33:44:55:66',
                'ssid': 'DLink_OpenWPS',
                'vendor': 'D-Link',
                'model': 'DIR-600',
                'known_pins': ['76229909', '65432100'],
                'pin_patterns': ['7622****', '6543****'],
                'wps_version': '2.0',
                'last_seen': '2025-11-04',
                'flags': {'vulnerable': True, 'wps_locked': False}
            }
        ],
        'vendors': [
            {
                'vendor': 'Cisco',
                'prefixes': ['1234', '5678', '9012'],
                'patterns': ['1234####', '5678####'],
                'probability_score': 8.5,
                'notes': 'Cisco routers often use predictable PIN patterns'
            },
            {
                'vendor': 'TP-Link',
                'prefixes': ['2829', '1020'],
                'patterns': ['2829####', 'MODEL###'],
                'probability_score': 9.0,
                'notes': 'TP-Link known for weak default PINs'
            },
            {
                'vendor': 'D-Link',
                'prefixes': ['7622', '6543', '0000'],
                'patterns': ['7622####', '0000####'],
                'probability_score': 7.5,
                'notes': 'D-Link routers with common default patterns'
            },
            {
                'vendor': 'Belkin',
                'prefixes': ['1111', '2222'],
                'patterns': ['1111####', '2222####'],
                'probability_score': 6.0,
                'notes': 'Belkin routers with simple default PINs'
            },
            {
                'vendor': 'Netgear',
                'prefixes': ['3333', '4444', '5555'],
                'patterns': ['3333####', '4444####'],
                'probability_score': 7.0,
                'notes': 'Netgear routers with manufacturer patterns'
            }
        ],
        'metadata': {
            'version': '1.0',
            'created': '2025-11-06',
            'description': 'WPS vulnerability database with vendor patterns and known PINs',
            'author': 'Farhan'
        }
    }


def convert_vulnwsc(input_file: str, output_file: str) -> None:
    """
    Convert vulnwsc.txt to JSON database.
    
    Args:
        input_file: Path to vulnwsc.txt
        output_file: Path to output JSON file
    """
    input_path = Path(input_file)
    
    if not input_path.exists():
        print(f"Error: Input file {input_file} not found", file=sys.stderr)
        sys.exit(1)
    
    aps = []
    with open(input_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            ap_data = parse_vulnwsc_line(line)
            if ap_data:
                aps.append(ap_data)
            else:
                print(f"Warning: Could not parse line {line_num}: {line}", file=sys.stderr)
    
    # Create database structure
    db = {
        'aps': aps,
        'vendors': [],
        'metadata': {
            'version': '1.0',
            'source': str(input_file),
            'converted': True
        }
    }
    
    # Write output
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=2)
    
    print(f"Converted {len(aps)} access points to {output_file}")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Convert vulnwsc.txt to structured vulnerability database'
    )
    parser.add_argument(
        '--input',
        help='Input vulnwsc.txt file'
    )
    parser.add_argument(
        '--output',
        default='db/vuln_db.json',
        help='Output JSON database file (default: db/vuln_db.json)'
    )
    parser.add_argument(
        '--create-sample',
        action='store_true',
        help='Create sample database instead of converting'
    )
    
    args = parser.parse_args()
    
    if args.create_sample:
        # Create sample database
        db = create_sample_database()
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(db, f, indent=2)
        
        print(f"Created sample database: {args.output}")
        print(f"  - {len(db['aps'])} access points")
        print(f"  - {len(db['vendors'])} vendor patterns")
        return 0
    
    if not args.input:
        print("Error: --input required (or use --create-sample)", file=sys.stderr)
        return 1
    
    convert_vulnwsc(args.input, args.output)
    return 0


if __name__ == '__main__':
    sys.exit(main())
