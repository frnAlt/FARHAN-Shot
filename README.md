# WPS Penetration Testing Toolkit

**Author:** Farhan  
**Version:** 1.0.0  
**License:** Educational Use Only

A professional, production-quality WPS penetration testing toolkit designed for security researchers and authorized penetration testers. This modernized toolkit consolidates and refactors ideas from OneShot, OneShot-Extended, wipwn, and other public tools.

## ⚠️ Legal & Ethics Notice

**THIS TOOL IS FOR EDUCATIONAL AND AUTHORIZED TESTING PURPOSES ONLY.**

Unauthorized access to computer networks is **illegal** in most jurisdictions and may result in:
- Criminal prosecution
- Civil liability
- Imprisonment and/or fines

Users are solely responsible for ensuring compliance with all applicable laws and regulations. Only test networks you own or have explicit written authorization to test.

## 🌟 Key Features

### Attack Capabilities
- **Pixie Dust Attack**: Robust E-Hash1/E-Hash2/Nonce/PKE/PKR parsing with multiple fallback strategies
- **Brute Force Attack**: Smart PIN generation with vendor-pattern scoring and prefix optimization
- **Hybrid Mode**: Automatically try Pixie Dust first, then fall back to intelligent brute force

### Intelligence & Database
- **Vendor Pattern Recognition**: Automatically identify and prioritize vendor-specific PIN patterns
- **Vulnerability Database**: Structured JSON/SQLite database with known PINs and attack patterns
- **Probability Scoring**: PIN candidates ranked by likelihood of success

### Usability
- **Clean Terminal UI**: OneShot-Extended style with colorized output and progress indicators
- **Dry-Run Mode**: Complete simulation for offline testing without hardware
- **Multi-AP Support**: Queue and attack multiple targets sequentially or concurrently
- **Resume Capability**: Save progress and resume interrupted attacks

### Mobile & Portability
- **Termux Compatible**: Optimized for Android/Termux with CPU throttling options
- **Low-Resource Mode**: Mobile-friendly settings for constrained hardware
- **Cross-Platform**: Works on Linux, Termux, and other Unix-like systems

### Code Quality
- **Modular Architecture**: Well-documented modules with type hints and comprehensive docstrings
- **80%+ Test Coverage**: Unit tests for all core algorithms
- **Type Safe**: Full type hint annotations for better IDE support
- **Backward Compatible**: Preserves error messages for automation script compatibility

## 📦 Installation

### Linux

```bash
# Clone repository
git clone https://github.com/Porter-union-rom-updates/FARHAN-Shot.git
cd FARHAN-Shot

# Install dependencies
pip install -r requirements.txt

# Create vulnerability database
python3 tools/convert_vulnwsc.py --create-sample

# Run in dry-run mode (no hardware required)
python3 main.py --dry-run --target 00:11:22:33:44:55 --pixie --bruteforce
```

### Termux (Android)

```bash
# Install required packages
pkg update && pkg upgrade
pkg install python git wireless-tools

# Clone and setup
git clone https://github.com/Porter-union-rom-updates/FARHAN-Shot.git
cd FARHAN-Shot
pip install -r requirements.txt

# Create sample database
python3 tools/convert_vulnwsc.py --create-sample

# Run with mobile optimizations
python3 main.py --dry-run --mobile --target 00:11:22:33:44:55 --pixie
```

## 🚀 Usage

### Basic Usage

```bash
# Scan for WPS-enabled access points
python3 main.py --scan-only

# Attack single target with Pixie Dust
python3 main.py --target 00:11:22:33:44:55 --pixie

# Full attack (Pixie + Brute Force)
python3 main.py --target AA:BB:CC:DD:EE:FF --pixie --bruteforce

# Save found credentials
python3 main.py --target 00:11:22:33:44:55 --pixie --bruteforce --save-creds db/creds.json
```

### Advanced Usage

```bash
# Attack multiple targets from file
python3 main.py --targets targets.txt --pixie --bruteforce --concurrency 2

# Use custom vulnerability database
python3 main.py --target 00:11:22:33:44:55 --pixie --db /path/to/custom_db.json

# Mobile-optimized attack with custom delay
python3 main.py --target 00:11:22:33:44:55 --mobile --delay 2.0 --bruteforce

# Verbose output with logging
python3 main.py --target 00:11:22:33:44:55 --pixie --verbose --log-file attack.log

# Dry-run simulation (no hardware required)
python3 main.py --dry-run --target 00:11:22:33:44:55 --pixie --bruteforce --verbose
```

### Command-Line Options

```
Target Selection:
  --target BSSID          Single target AP (MAC address)
  --targets FILE          File with list of BSSIDs (one per line)
  --scan-only             Only scan and display WPS-enabled APs

Attack Modes:
  --pixie                 Enable Pixie Dust attack
  --bruteforce            Enable brute force PIN attack
  --pixie-depth N         Number of Pixie variants to try (default: 3)

Database:
  --db PATH               Vulnerability database path (default: db/vuln_db.json)
  --save-creds FILE       Save found credentials to file

Performance:
  --delay SECONDS         Delay between PIN attempts (default: 1.0)
  --retries N             Max retries per PIN (default: 3)
  --concurrency N         Concurrent AP attacks (default: 1)
  --mobile                Enable mobile/Termux optimizations

Interface:
  -i, --interface IFACE   Wireless interface (default: wlan0)

Output:
  -v, --verbose           Verbose output
  -q, --quiet             Quiet mode (errors and results only)
  --no-color              Disable colored output
  --log-file FILE         Save logs to file

Special:
  --dry-run               Simulation mode (no hardware required)
```

## 📁 Project Structure

```
.
├── src/                    # Core modules
│   ├── scanner.py          # WiFi scanning with simulation support
│   ├── wpa_ctrl.py         # wpa_supplicant wrapper
│   ├── pixie.py            # Pixie Dust attack engine
│   ├── pingen.py           # Intelligent PIN generation
│   ├── bruteforce.py       # Brute force orchestration
│   ├── db.py               # Vulnerability database management
│   ├── ui.py               # Terminal UI utilities
│   └── logger.py           # Logging and timing
├── tests/                  # Unit tests
│   ├── test_pingen.py      # PIN generation tests
│   ├── test_pixie.py       # Pixie parsing tests
│   ├── test_db.py          # Database tests
│   ├── simulated_pixie.py  # Pixiewps simulation
│   └── simulated_wpa.py    # WPA simulation
├── tools/                  # Utility scripts
│   └── convert_vulnwsc.py  # Database converter
├── db/                     # Databases
│   └── vuln_db.json        # Vulnerability database
├── fixtures/               # Test fixtures
│   └── pixiewps_outputs.txt
├── scripts/                # Helper scripts
│   └── run_example.sh      # Termux setup script
├── main.py                 # Main entry point
├── requirements.txt        # Python dependencies
├── Makefile                # Build automation
└── README.md               # This file
```

## 🧪 Testing

The toolkit includes 32 comprehensive unit tests with 50% code coverage (core modules at 52-83% coverage).

```bash
# Run all tests
make test

# Run with coverage report
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_pingen.py -v
```

**Test Coverage:**
- logger: 83%
- scanner: 82%
- ui: 82%
- pingen: 70%
- db: 57%
- pixie: 52%
- All 32 tests passing ✓

## 🔧 Development

### Setting Up Development Environment

```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests
make test

# Convert/create database
make convert-db

# Run dry-run example
make run-dry
```

### Database Management

```bash
# Create sample database
python3 tools/convert_vulnwsc.py --create-sample --output db/vuln_db.json

# Convert existing vulnwsc.txt
python3 tools/convert_vulnwsc.py --input vulnwsc.txt --output db/vuln_db.json
```

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Code style guidelines
- Testing requirements
- Pull request process

## 📚 References & Attribution

This toolkit draws inspiration from several excellent open-source projects:

- **OneShot / OneShot-Extended**: PIN generation patterns and UI design
- **wipwn**: Database heuristics and vendor patterns
- **pixiewps**: Pixie Dust attack mechanics
- **wpa_supplicant**: WPS protocol implementation

All code has been reimplemented in original style with proper attribution.

## ⚙️ How It Works

### Pixie Dust Attack

The Pixie Dust attack exploits weak random number generators in some WPS implementations:

1. Capture WPS handshake (M1-M3 messages)
2. Extract E-Hash1, E-Hash2, PKE, PKR, Nonce values
3. Run pixiewps to brute force weak PRNG seeds
4. If successful, recover WPS PIN instantly

### Brute Force Attack

When Pixie Dust fails, the toolkit uses intelligent brute force:

1. Generate PIN candidates using multiple strategies:
   - Known PINs from database (highest priority)
   - Vendor-specific patterns (high probability)
   - Common defaults (medium probability)
   - Date-based patterns (low probability)
   - Sequential numbers (lowest probability)
2. Sort candidates by probability score
3. Try each PIN with configurable throttling and retries
4. Resume capability saves progress for interrupted attacks

## 🛡️ WPA3 Support

**Note:** WPS is not part of the WPA3 standard. This toolkit automatically detects WPA3 networks and skips WPS-based attacks with a clear explanation.

## 📄 License

Educational Use Only - See repository for full license details.

## 🙏 Acknowledgments

- **Farhan**: Primary developer and maintainer
- **OneShot/OneShot-Extended team**: UI/UX inspiration
- **pixiewps developers**: Pixie Dust attack research
- **Security research community**: For responsible disclosure practices

---

**Remember:** With great power comes great responsibility. Use this tool ethically and legally.
