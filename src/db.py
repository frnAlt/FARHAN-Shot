"""
Vulnerability database management module.
Author: Farhan

Manages vulnerability database for WPS PIN patterns, vendor information,
and known vulnerable access points. Supports both JSON and SQLite formats.
"""

import json
import sqlite3
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict, field
from pathlib import Path


@dataclass
class APRecord:
    """Access Point record in vulnerability database."""
    
    bssid: str
    ssid: Optional[str] = None
    vendor: Optional[str] = None
    model: Optional[str] = None
    known_pins: List[str] = field(default_factory=list)
    pin_patterns: List[str] = field(default_factory=list)
    wps_version: Optional[str] = None
    last_seen: Optional[str] = None
    flags: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VendorPattern:
    """Vendor-specific PIN pattern information."""
    
    vendor: str
    prefixes: List[str]
    patterns: List[str]
    probability_score: float = 1.0
    notes: Optional[str] = None
    
    def __post_init__(self) -> None:
        """Initialize default values."""
        if self.prefixes is None:
            self.prefixes = []
        if self.patterns is None:
            self.patterns = []


class VulnerabilityDB:
    """Vulnerability database manager."""
    
    def __init__(self, db_path: str) -> None:
        """
        Initialize database.
        
        Args:
            db_path: Path to database file (JSON or SQLite)
        """
        self.db_path = Path(db_path)
        self.is_sqlite = db_path.endswith('.db') or db_path.endswith('.sqlite')
        self.connection: Optional[sqlite3.Connection] = None
        self.data: Dict[str, Any] = {'aps': [], 'vendors': []}
        
        if self.is_sqlite:
            self._init_sqlite()
        else:
            self._load_json()
    
    def _init_sqlite(self) -> None:
        """Initialize SQLite database with schema."""
        self.connection = sqlite3.connect(str(self.db_path))
        self.connection.row_factory = sqlite3.Row
        cursor = self.connection.cursor()
        
        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS access_points (
                bssid TEXT PRIMARY KEY,
                ssid TEXT,
                vendor TEXT,
                model TEXT,
                wps_version TEXT,
                last_seen TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS known_pins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bssid TEXT,
                pin TEXT,
                FOREIGN KEY (bssid) REFERENCES access_points(bssid)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pin_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bssid TEXT,
                pattern TEXT,
                FOREIGN KEY (bssid) REFERENCES access_points(bssid)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vendor_patterns (
                vendor TEXT PRIMARY KEY,
                prefixes TEXT,
                patterns TEXT,
                probability_score REAL,
                notes TEXT
            )
        """)
        
        self.connection.commit()
    
    def _load_json(self) -> None:
        """Load data from JSON file."""
        if self.db_path.exists():
            with open(self.db_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        else:
            # Initialize empty database
            self.data = {'aps': [], 'vendors': []}
    
    def _save_json(self) -> None:
        """Save data to JSON file."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2)
    
    def lookup_ap(self, bssid: str) -> Optional[APRecord]:
        """
        Look up access point by BSSID.
        
        Args:
            bssid: MAC address of AP
        
        Returns:
            APRecord if found, None otherwise
        """
        bssid = bssid.upper()
        
        if self.is_sqlite and self.connection:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT * FROM access_points WHERE bssid = ?", 
                (bssid,)
            )
            row = cursor.fetchone()
            
            if row:
                # Fetch associated pins and patterns
                cursor.execute(
                    "SELECT pin FROM known_pins WHERE bssid = ?", 
                    (bssid,)
                )
                pins = [r[0] for r in cursor.fetchall()]
                
                cursor.execute(
                    "SELECT pattern FROM pin_patterns WHERE bssid = ?", 
                    (bssid,)
                )
                patterns = [r[0] for r in cursor.fetchall()]
                
                return APRecord(
                    bssid=row['bssid'],
                    ssid=row['ssid'],
                    vendor=row['vendor'],
                    model=row['model'],
                    known_pins=pins,
                    pin_patterns=patterns,
                    wps_version=row['wps_version'],
                    last_seen=row['last_seen']
                )
        else:
            # JSON lookup
            for ap_data in self.data.get('aps', []):
                if ap_data.get('bssid', '').upper() == bssid:
                    return APRecord(**ap_data)
        
        return None
    
    def lookup_vendor_patterns(self, vendor: str) -> Optional[VendorPattern]:
        """
        Look up vendor PIN patterns.
        
        Args:
            vendor: Vendor name
        
        Returns:
            VendorPattern if found, None otherwise
        """
        if self.is_sqlite and self.connection:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT * FROM vendor_patterns WHERE vendor = ?", 
                (vendor,)
            )
            row = cursor.fetchone()
            
            if row:
                return VendorPattern(
                    vendor=row['vendor'],
                    prefixes=json.loads(row['prefixes']),
                    patterns=json.loads(row['patterns']),
                    probability_score=row['probability_score'],
                    notes=row['notes']
                )
        else:
            # JSON lookup
            for vp_data in self.data.get('vendors', []):
                if vp_data.get('vendor') == vendor:
                    return VendorPattern(**vp_data)
        
        return None
    
    def add_ap(self, ap: APRecord) -> None:
        """
        Add or update AP record.
        
        Args:
            ap: APRecord to add/update
        """
        if self.is_sqlite and self.connection:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO access_points 
                (bssid, ssid, vendor, model, wps_version, last_seen)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (ap.bssid, ap.ssid, ap.vendor, ap.model, 
                  ap.wps_version, ap.last_seen))
            
            # Delete old pins and patterns
            cursor.execute("DELETE FROM known_pins WHERE bssid = ?", (ap.bssid,))
            cursor.execute("DELETE FROM pin_patterns WHERE bssid = ?", (ap.bssid,))
            
            # Insert new pins
            for pin in ap.known_pins:
                cursor.execute(
                    "INSERT INTO known_pins (bssid, pin) VALUES (?, ?)",
                    (ap.bssid, pin)
                )
            
            # Insert new patterns
            for pattern in ap.pin_patterns:
                cursor.execute(
                    "INSERT INTO pin_patterns (bssid, pattern) VALUES (?, ?)",
                    (ap.bssid, pattern)
                )
            
            self.connection.commit()
        else:
            # JSON update
            ap_dict = asdict(ap)
            # Remove existing entry
            self.data['aps'] = [
                a for a in self.data['aps'] 
                if a.get('bssid') != ap.bssid
            ]
            # Add new entry
            self.data['aps'].append(ap_dict)
            self._save_json()
    
    def add_vendor_pattern(self, pattern: VendorPattern) -> None:
        """
        Add or update vendor pattern.
        
        Args:
            pattern: VendorPattern to add/update
        """
        if self.is_sqlite and self.connection:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO vendor_patterns 
                (vendor, prefixes, patterns, probability_score, notes)
                VALUES (?, ?, ?, ?, ?)
            """, (pattern.vendor, 
                  json.dumps(pattern.prefixes),
                  json.dumps(pattern.patterns),
                  pattern.probability_score,
                  pattern.notes))
            self.connection.commit()
        else:
            # JSON update
            pattern_dict = asdict(pattern)
            # Remove existing entry
            self.data['vendors'] = [
                v for v in self.data['vendors'] 
                if v.get('vendor') != pattern.vendor
            ]
            # Add new entry
            self.data['vendors'].append(pattern_dict)
            self._save_json()
    
    def get_all_vendor_patterns(self) -> List[VendorPattern]:
        """
        Get all vendor patterns.
        
        Returns:
            List of all VendorPattern objects
        """
        patterns = []
        
        if self.is_sqlite and self.connection:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM vendor_patterns")
            for row in cursor.fetchall():
                patterns.append(VendorPattern(
                    vendor=row['vendor'],
                    prefixes=json.loads(row['prefixes']),
                    patterns=json.loads(row['patterns']),
                    probability_score=row['probability_score'],
                    notes=row['notes']
                ))
        else:
            for vp_data in self.data.get('vendors', []):
                patterns.append(VendorPattern(**vp_data))
        
        return patterns
    
    def close(self) -> None:
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
