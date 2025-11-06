# FARHAN-SHOT v2.0 🎯

**Modern WPS WiFi Penetration Testing Tool**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-Educational-yellow.svg)](LICENSE)

A professional-grade WPS (Wi-Fi Protected Setup) penetration testing tool featuring modern attack techniques including Pixie Dust, PIN prediction algorithms, and intelligent bruteforce capabilities.

---

## ⚠️ Legal Disclaimer

**FOR EDUCATIONAL AND AUTHORIZED PENETRATION TESTING ONLY**

This tool is created exclusively for:
- Security research and education
- Authorized penetration testing
- Testing your own networks
- Learning about WPS vulnerabilities

**Unauthorized access to computer networks is illegal.** Always obtain explicit written permission before testing any network you don't own. The developers assume no liability for misuse of this software.

---

## ✨ Features

### 🎯 Advanced Attack Capabilities
- **Pixie Dust Attack**: Modern 2025 implementation targeting weak PRNG
- **PIN Prediction**: Multiple algorithms (ComputePIN, EasyBox, D-Link, ASUS, etc.)
- **Online Bruteforce**: Smart PIN testing with rate limiting
- **Offline Bruteforce**: Crack PINs from captured handshakes
- **No Monitor Mode Required**: Uses wpa_supplicant for compatibility

### 📊 Comprehensive Database
- **290+ Vulnerable Router Entries**: Including 2025 confirmed vulnerabilities
- **Major Vendors**: TP-Link, D-Link, ASUS, Netgear, ZyXEL, Belkin, Huawei, Xiaomi
- **Chipset Coverage**: Realtek, Ralink, Broadcom vulnerabilities
- **Auto-Updated**: MAC/OUI-based vulnerability detection

### 🧠 Intelligent PIN Generation
- **15+ Algorithm Implementations**:
  - ComputePIN (Zaochesung)
  - EasyBox (Vodafone)
  - D-Link algorithm
  - ASUS algorithm
  - 24/28/32/36/40/44/48-bit PINs
  - Vendor-specific PINs
  - Common PIN database
- **Confidence Scoring**: Prioritizes most likely PINs first
- **Integration with wpspin**: Comprehensive PIN generation library

### 🎨 Modern Terminal UI
- **Rich TUI**: Beautiful colored output with progress bars
- **Real-time Progress**: Live attack status and PIN testing
- **Vulnerability Highlighting**: Color-coded threat levels
- **Signal Strength Analysis**: Distance estimation for long-range testing

### 📱 Mobile & Long-Distance Optimization
- **Mobile Hardware Support**: Optimized for Android/Termux
- **Battery Saving Mode**: Adaptive retry logic
- **Long-Distance Mode**: Enhanced signal analysis
- **Distance Estimation**: Calculate AP distance from signal strength

### 💾 Results Management
- **Attack History**: Automatic result logging
- **Success Tracking**: Statistics and success rates
- **JSON Export**: Portable result format

---

## 🚀 Installation

### Prerequisites

**System Requirements:**
- Linux (Kali, Ubuntu, Debian, etc.) or Android (Termux)
- Python 3.11 or higher
- Root/sudo access (for wireless operations)

**Required Packages:**
```bash
# Debian/Ubuntu/Kali
sudo apt update
sudo apt install -y python3 python3-pip wpasupplicant iw pixiewps

# Optional (for advanced features)
sudo apt install -y aircrack-ng reaver
```

### Quick Install

```bash
# Clone repository
git clone https://github.com/Porter-union-rom-updates/FARHAN-Shot.git
cd FARHAN-Shot

# Install Python dependencies
pip install -r requirements.txt

# Or install directly
pip install rich typer wpspin cryptography python-dotenv requests

# Make executable
chmod +x main.py

# Run
python3 main.py --help
```

### Termux (Android) Installation

```bash
# Install required packages
pkg update
pkg install -y python python-pip root-repo
pkg install -y wpasupplicant iw

# Clone and setup
git clone https://github.com/Porter-union-rom-updates/FARHAN-Shot.git
cd FARHAN-Shot
pip install -r requirements.txt

# Requires rooted device
su
python main.py --help
```

---

## 📖 Usage

### Basic Commands

#### 1. Scan for Networks
```bash
# Scan with default interface (wlan0)
python main.py scan

# Specify interface
python main.py scan --interface wlan1

# Verbose output
python main.py scan -v

# Extended scan
python main.py scan --timeout 20
```

**Output Features:**
- Lists all networks with WPS status
- Highlights vulnerable routers (RED = High, YELLOW = Medium)
- Shows signal strength and estimated distance
- Displays manufacturer and vulnerability score

#### 2. Attack Target Network
```bash
# Auto attack (tries best methods)
python main.py attack --bssid AA:BB:CC:DD:EE:FF

# Specify attack type
python main.py attack -b AA:BB:CC:DD:EE:FF --type bruteforce

# Limit PIN attempts
python main.py attack -b AA:BB:CC:DD:EE:FF --max-pins 30

# Verbose attack
python main.py attack -b AA:BB:CC:DD:EE:FF -v
```

**Attack Types:**
- `auto`: Automatically selects best attack method
- `pixie`: Pixie Dust attack (requires setup)
- `bruteforce`: Online PIN bruteforce

#### 3. View Statistics
```bash
# Show database and attack stats
python main.py info
```

#### 4. Version Information
```bash
python main.py version
```

---

## 🎯 Attack Workflow Example

### Complete Attack Session
```bash
# 1. Scan for targets
python main.py scan --interface wlan0

# Output shows:
# #  SSID              BSSID              Ch  Signal   WPS  Vuln  Manufacturer
# 1  TP-Link_Home      AA:BB:CC:DD:EE:FF  6   -45dBm   ✓    HIGH  TP-Link

# 2. Attack the vulnerable target
python main.py attack --bssid AA:BB:CC:DD:EE:FF --verbose

# 3. Tool will:
#    - Generate 20+ PIN candidates
#    - Prioritize by vulnerability/confidence
#    - Test each PIN with smart delays
#    - Display real-time progress
#    - Save results automatically

# 4. On success:
# ╔═══════════════════════════════════╗
# ║           SUCCESS                 ║
# ╚═══════════════════════════════════╝
# WPS PIN: 12345670
# Password: MySecurePassword123
# Duration: 3.2 minutes
```

---

## 🔧 Advanced Configuration

### Environment Variables
```bash
# Set default interface
export WPS_INTERFACE=wlan0

# Set timeout
export WPS_TIMEOUT=30

# Enable verbose mode
export WPS_VERBOSE=true
```

### Long-Distance Mode
For testing long-range WiFi:
```bash
# Enable long-distance optimizations
python main.py attack -b <BSSID> --long-distance
```

### Mobile/Battery Saving
```bash
# Optimize for mobile devices
python main.py attack -b <BSSID> --mobile-mode
```

---

## 📁 Project Structure

```
FARHAN-Shot/
├── wps_tool/                 # Main package
│   ├── core/                 # Core functionality
│   │   ├── config.py         # Configuration management
│   │   ├── logger.py         # Logging setup
│   │   └── wpa_controller.py # WPA supplicant control
│   ├── scan/                 # Network scanning
│   │   └── scanner.py        # WiFi scanner
│   ├── pins/                 # PIN generation
│   │   └── generator.py      # Advanced PIN algorithms
│   ├── attacks/              # Attack modules
│   │   ├── pixie_dust.py     # Pixie Dust attack
│   │   └── bruteforce.py     # Bruteforce attack
│   ├── db/                   # Database management
│   │   ├── models.py         # Data models
│   │   └── database.py       # Database operations
│   ├── ui/                   # User interface
│   │   └── display.py        # Rich terminal UI
│   ├── data/                 # Data files
│   │   └── vulnwsc.txt       # Vulnerability database
│   └── cli.py                # CLI interface
├── main.py                   # Entry point
├── pyproject.toml            # Project configuration
└── README.md                 # This file
```

---

## 🎓 How It Works

### Vulnerability Types

| Type | Description | Success Rate |
|------|-------------|--------------|
| **Pixie Dust (PD)** | Exploits weak PRNG in WPS implementation | 30-40% |
| **ComputePIN (COMP)** | MAC-based PIN calculation | 15-25% |
| **EasyBox (EASY)** | Vodafone router algorithm | 80-90% |
| **D-Link/ASUS** | Vendor-specific algorithms | 20-30% |
| **Known PIN** | Database of default PINs | Variable |

### PIN Generation Process

1. **Vendor Detection**: Identifies manufacturer from MAC OUI
2. **Algorithm Selection**: Chooses best algorithms for target
3. **Confidence Scoring**: Ranks PINs by likelihood of success
4. **Smart Testing**: Tests highest-confidence PINs first

### Attack Flow

```
[Scan] → [Identify Vulnerable Routers] → [Generate PINs]
   ↓
[Pixie Dust Attack] (if supported)
   ↓ (if fails)
[Online Bruteforce] → [Test High-Confidence PINs]
   ↓
[Success!] → [Extract Password] → [Save Results]
```

---

## 🛡️ Known Vulnerable Devices (2025)

### High-Risk Vendors
- **TP-Link**: Archer series, TL-WR series (2025 confirmed)
- **D-Link**: DIR-605L, DIR-615, DIR-809, DIR-819
- **ASUS**: RT-N12, RT-AC51U, RT-AC52U
- **Netgear**: JWNR2000v2, R6220, WN3000RP
- **Xiaomi**: Mi Router (multiple models)

### Chipset Vulnerabilities
- **Realtek**: RTL8188, RTL8192 series
- **Ralink**: RT2860, RT3070, RT5370
- **Broadcom**: BCM4318, BCM4321 (partial)

**Full list**: 290+ entries in `wps_tool/data/vulnwsc.txt`

---

## 🔍 Troubleshooting

### Common Issues

#### "wpa_supplicant not found"
```bash
sudo apt install wpasupplicant
```

#### "Permission denied"
```bash
# Run with sudo
sudo python main.py scan
```

#### "No networks found"
```bash
# Check interface is up
sudo ip link set wlan0 up

# Verify interface name
iw dev

# Try different interface
python main.py scan --interface wlan1
```

#### "pixiewps not installed"
```bash
sudo apt install pixiewps
```

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add your improvements
4. Submit a pull request

**Contribution Ideas:**
- Add more PIN algorithms
- Expand vulnerability database
- Improve UI/UX
- Add new attack vectors
- Mobile optimizations

---

## 📚 References & Credits

### Inspiration & Research
- **OneShot**: Original wpa_supplicant-based WPS attack tool
- **Reaver**: Classic WPS attack tool
- **wpspin**: PIN generation library by drygdryg
- **Pixiewps**: Offline WPS PIN cracker by wiire-a

### Security Research
- Dominique Bongard (Pixie Dust discovery, 2014)
- Stefan Viehböck (EasyBox algorithm)
- Craig Heffner (D-Link algorithm)
- NetRise 2025 Vulnerability Report

### Algorithm Sources
- ComputePIN (Zaochesung/zhaochunsheng)
- 3WiFi database
- SEC Consult advisories

---

## 📜 License

This project is released for **educational purposes only** under an educational license.

**YOU ARE RESPONSIBLE FOR YOUR ACTIONS.**

The developers:
- Do NOT condone illegal use
- Assume NO liability for misuse
- Provide this tool for learning and authorized testing ONLY

---

## 🌟 Features Roadmap

### v2.1 (Upcoming)
- [ ] GPU-accelerated PIN cracking
- [ ] Automated mass scanning
- [ ] Web interface dashboard
- [ ] Docker containerization
- [ ] Automated vulnerability database updates

### v2.2 (Future)
- [ ] Integration with Metasploit
- [ ] Custom wordlist support
- [ ] Network topology mapping
- [ ] Advanced evasion techniques

---

## 📞 Support

**For legitimate security research and educational questions:**
- Open an issue on GitHub
- Follow responsible disclosure practices
- Test only on networks you own or have permission to test

---

## ⭐ Acknowledgments

Special thanks to:
- The information security research community
- All contributors and testers
- Open-source WPS attack tool developers
- Wireless security researchers worldwide

---

<div align="center">

**FARHAN-SHOT v2.0** - Modern WiFi Penetration Testing  
*For Education & Authorized Testing Only*

**Made with ❤️ for the security research community**

</div>
