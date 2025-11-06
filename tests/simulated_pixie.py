"""
Simulated pixiewps output generator for testing.
Author: Farhan

Provides realistic pixiewps output simulation for offline testing
of Pixie Dust attack parsing and handling logic.
"""

from typing import Optional


class PixiewpsSimulator:
    """Simulate pixiewps command outputs."""
    
    @staticmethod
    def successful_attack(pin: str = "12345670") -> str:
        """Generate successful pixiewps output."""
        return f"""
 Pixiewps 1.4

 [?] Mode:     3 (RTL819x)
 [*] Seed N1:  0x5a7d4b3c
 [*] Seed ES1: 0x1122aabb
 [*] Seed ES2: 0x3344ccdd
 [*] PSK1:     11:22:33:44:55:66:77:88:99:aa:bb:cc:dd:ee:ff:00
 [*] PSK2:     aa:bb:cc:dd:ee:ff:00:11:22:33:44:55:66:77:88:99
 [*] E-S1:     11:22:33:44:55:66:77:88:99:aa:bb:cc:dd:ee:ff:00
 [*] E-S2:     aa:bb:cc:dd:ee:ff:00:11:22:33:44:55:66:77:88:99
 [+] WPS pin:  {pin}

 [*] Time taken: 0 s 123 ms
        """
    
    @staticmethod
    def failed_attack() -> str:
        """Generate failed pixiewps output."""
        return """
 Pixiewps 1.4

 [?] Mode:     3 (RTL819x)
 [*] Seed N1:  0x5a7d4b3c
 [*] Seed ES1: 0x1122aabb
 [*] Seed ES2: 0x3344ccdd
 [-] WPS pin not found!

 [*] Time taken: 1 s 456 ms
        """
    
    @staticmethod
    def with_hashes(e_hash1: Optional[str] = None, 
                    e_hash2: Optional[str] = None) -> str:
        """Generate output with E-Hash values."""
        eh1 = e_hash1 or "aabbccdd11223344556677889900aabbccdd1122"
        eh2 = e_hash2 or "11223344556677889900aabbccddeeef11223344"
        
        return f"""
 Pixiewps 1.4

 [*] PKE:      aabbccddeeff00112233445566778899aabbccddeeff00112233445566778899
 [*] PKR:      112233445566778899aabbccddeeff00112233445566778899aabbccddeeff
 [*] E-Hash1:  {eh1}
 [*] E-Hash2:  {eh2}
 [*] E-Nonce:  99887766554433221100ffeeddccbbaa99887766
 [-] WPS pin not found!

 [*] Time taken: 2 s 789 ms
        """
    
    @staticmethod
    def partial_data() -> str:
        """Generate output with partial data (missing some required fields)."""
        return """
 Pixiewps 1.4

 [*] E-Hash1:  aabbccdd11223344556677889900aabbccdd1122
 [-] Error: Missing required parameter PKR

 [*] Time taken: 0 s 50 ms
        """
