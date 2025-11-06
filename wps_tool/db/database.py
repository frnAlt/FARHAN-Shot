"""Database management for vulnerable routers and results"""
import json
from pathlib import Path
from typing import List, Dict, Optional
import logging
from .models import VulnerableRouter, VulnType, AttackResult

logger = logging.getLogger("farhan_shot.db")


class VulnerabilityDatabase:
    """Manages vulnerability database"""
    
    def __init__(self, db_path: Path):
        """Initialize database
        
        Args:
            db_path: Path to vulnwsc.txt file
        """
        self.db_path = db_path
        self.routers: Dict[str, VulnerableRouter] = {}
        self._load_database()
    
    def _load_database(self):
        """Load vulnerability database from file"""
        if not self.db_path.exists():
            logger.warning(f"Vulnerability database not found: {self.db_path}")
            return
        
        try:
            with open(self.db_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    
                    # Skip comments and empty lines
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse line: MAC_PREFIX|MANUFACTURER|MODEL|VULN_TYPE|NOTES
                    parts = line.split('|')
                    if len(parts) < 4:
                        continue
                    
                    mac_prefix = parts[0].strip().replace(":", "").upper()
                    manufacturer = parts[1].strip()
                    model = parts[2].strip()
                    vuln_types_str = parts[3].strip()
                    notes = parts[4].strip() if len(parts) > 4 else ""
                    
                    # Parse vulnerability types
                    vuln_types = []
                    for vtype in vuln_types_str.split(','):
                        vtype = vtype.strip()
                        try:
                            vuln_types.append(VulnType(vtype))
                        except ValueError:
                            logger.debug(f"Unknown vulnerability type: {vtype}")
                    
                    router = VulnerableRouter(
                        mac_prefix=mac_prefix,
                        manufacturer=manufacturer,
                        model=model,
                        vuln_types=vuln_types,
                        notes=notes
                    )
                    
                    self.routers[mac_prefix] = router
            
            logger.info(f"Loaded {len(self.routers)} vulnerable router entries")
        
        except Exception as e:
            logger.error(f"Failed to load vulnerability database: {e}")
    
    def lookup(self, bssid: str) -> Optional[VulnerableRouter]:
        """Look up router by BSSID
        
        Args:
            bssid: MAC address (any format)
            
        Returns:
            VulnerableRouter if found, None otherwise
        """
        # Normalize BSSID to get OUI (first 6 hex digits)
        mac_normalized = bssid.upper().replace(":", "").replace("-", "")
        oui = mac_normalized[:6]
        
        return self.routers.get(oui)
    
    def is_vulnerable(self, bssid: str) -> bool:
        """Check if router is in vulnerability database
        
        Args:
            bssid: MAC address
            
        Returns:
            True if vulnerable, False otherwise
        """
        return self.lookup(bssid) is not None
    
    def get_vulnerability_score(self, bssid: str) -> float:
        """Calculate vulnerability score (0.0 to 1.0)
        
        Args:
            bssid: MAC address
            
        Returns:
            Vulnerability score
        """
        router = self.lookup(bssid)
        if not router:
            return 0.0
        
        # Base score from priority
        priority = router.get_attack_priority()
        max_priority = 10  # Max possible priority
        
        score = min(priority / max_priority, 1.0)
        
        # Boost score for specific vulnerabilities
        if VulnType.PIXIE_DUST in router.vuln_types:
            score = min(score + 0.2, 1.0)
        
        return score
    
    def get_stats(self) -> Dict[str, int]:
        """Get database statistics
        
        Returns:
            Statistics dictionary
        """
        manufacturers = {}
        vuln_types_count = {}
        
        for router in self.routers.values():
            manufacturers[router.manufacturer] = manufacturers.get(router.manufacturer, 0) + 1
            
            for vtype in router.vuln_types:
                vuln_types_count[vtype.value] = vuln_types_count.get(vtype.value, 0) + 1
        
        return {
            "total_entries": len(self.routers),
            "manufacturers": len(manufacturers),
            "top_manufacturers": sorted(
                manufacturers.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10],
            "vulnerability_types": vuln_types_count
        }


class ResultsDatabase:
    """Manages attack results storage"""
    
    def __init__(self, db_dir: Path):
        """Initialize results database
        
        Args:
            db_dir: Directory to store results
        """
        self.db_dir = db_dir
        self.db_dir.mkdir(parents=True, exist_ok=True)
        self.results_file = self.db_dir / "results.json"
        self.results: List[AttackResult] = []
        self._load_results()
    
    def _load_results(self):
        """Load previous results from file"""
        if not self.results_file.exists():
            return
        
        try:
            with open(self.results_file, 'r') as f:
                data = json.load(f)
                # TODO: Convert to AttackResult objects
                logger.info(f"Loaded {len(data)} previous results")
        except Exception as e:
            logger.error(f"Failed to load results: {e}")
    
    def save_result(self, result: AttackResult):
        """Save attack result
        
        Args:
            result: Attack result to save
        """
        self.results.append(result)
        self._persist_results()
    
    def _persist_results(self):
        """Persist results to file"""
        try:
            # Convert results to dict for JSON serialization
            results_data = []
            for result in self.results:
                results_data.append({
                    "target_ssid": result.target_ssid,
                    "target_bssid": result.target_bssid,
                    "attack_type": result.attack_type,
                    "success": result.success,
                    "pin": result.pin,
                    "password": result.password,
                    "duration": result.duration,
                    "timestamp": result.timestamp.isoformat() if result.timestamp else None,
                    "error_message": result.error_message,
                    "pins_tried": result.pins_tried,
                })
            
            with open(self.results_file, 'w') as f:
                json.dump(results_data, f, indent=2)
            
            logger.debug(f"Saved {len(results_data)} results to {self.results_file}")
        
        except Exception as e:
            logger.error(f"Failed to persist results: {e}")
    
    def get_successful_attacks(self) -> List[AttackResult]:
        """Get all successful attacks
        
        Returns:
            List of successful attack results
        """
        return [r for r in self.results if r.success]
    
    def get_stats(self) -> Dict:
        """Get results statistics
        
        Returns:
            Statistics dictionary
        """
        if not self.results:
            return {"total": 0, "successful": 0, "success_rate": 0.0}
        
        successful = len(self.get_successful_attacks())
        
        return {
            "total": len(self.results),
            "successful": successful,
            "success_rate": successful / len(self.results) * 100,
            "avg_duration": sum(r.duration for r in self.results) / len(self.results),
        }
