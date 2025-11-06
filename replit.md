# FARHAN-SHOT v2.0

## Overview

FARHAN-SHOT v2.0 is a modern WPS (Wi-Fi Protected Setup) penetration testing tool designed for educational purposes and authorized security testing. The application implements advanced attack techniques including Pixie Dust attacks, intelligent PIN prediction algorithms, and bruteforce capabilities. It features a comprehensive vulnerability database of 290+ router entries covering major vendors like TP-Link, D-Link, ASUS, Netgear, and others.

The tool operates without requiring monitor mode by leveraging wpa_supplicant, making it more compatible across different systems and use cases. It provides a rich terminal UI for an enhanced user experience and implements multiple PIN generation algorithms with confidence scoring to prioritize the most likely successful attacks.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Application Structure
The application follows a modular Python architecture organized into distinct functional components:

- **CLI Layer** (`wps_tool/cli.py`): Built using Typer for command-line interface management, providing user-facing commands and argument parsing
- **Core Layer** (`wps_tool/core/`): Contains configuration management, logging setup with Rich integration, and WPA supplicant controller
- **Attack Layer** (`wps_tool/attacks/`): Implements attack strategies including Pixie Dust and PIN bruteforce attacks
- **Scanning Layer** (`wps_tool/scan/`): Network discovery using `iw` command-line tools
- **PIN Generation Layer** (`wps_tool/pins/`): Advanced PIN generation algorithms utilizing the wpspin library
- **Database Layer** (`wps_tool/db/`): Vulnerability database management and data models
- **UI Layer** (`wps_tool/ui/`): Rich terminal UI components for enhanced user experience

### Design Patterns
**Command Pattern**: The CLI uses Typer to implement command-based interaction, allowing extensible subcommand architecture for different operations (scan, attack, etc.)

**Controller Pattern**: WPASupplicantController acts as a facade for managing wpa_supplicant processes, abstracting system-level WiFi operations from attack logic

**Strategy Pattern**: Multiple attack strategies (Pixie Dust, online bruteforce, offline bruteforce) can be selected and executed based on target vulnerability assessment

**Database Pattern**: Separation of vulnerability data (read-only router database) from results data (attack outcomes and history)

### Data Flow
1. User initiates scan via CLI command
2. NetworkScanner uses system tools (`iw dev`) to discover WiFi networks
3. Discovered networks are matched against VulnerabilityDatabase to identify vulnerable targets
4. WPSPinGenerator creates prioritized PIN candidates based on target characteristics
5. Attack strategies are executed via WPASupplicantController
6. Results are stored in ResultsDatabase and displayed via Rich UI

### Configuration Management
Centralized configuration through the Config dataclass provides:
- Interface settings (WiFi adapter selection)
- Attack parameters (timeouts, retries, delays)
- Feature flags (Pixie Dust enable/disable, bruteforce modes)
- Optimization modes (mobile mode, long-distance mode, battery saving)
- Database paths (vulnerability DB, results DB)

This approach allows easy testing and parameter tuning without code changes.

### Logging Architecture
Multi-level logging using Python's logging module enhanced with Rich handlers:
- Console output uses RichHandler for formatted, colorized logs
- Optional file logging for persistent records
- Verbose mode for detailed debugging
- Structured logger hierarchy (`farhan_shot.*`) for component-specific logging

## External Dependencies

### Core Libraries
- **rich** (>=13.7.0): Terminal UI framework providing tables, progress bars, panels, and formatted console output
- **typer** (>=0.12.0): Modern CLI framework built on Click, used for command parsing and help generation
- **wpspin** (>=0.2.0): WPS PIN generation library implementing ComputePIN and other vendor-specific algorithms
- **cryptography** (>=42.0.0): Cryptographic operations potentially used in PIN validation and attack implementations
- **python-dotenv** (>=1.0.0): Environment variable management for configuration
- **requests** (>=2.31.0): HTTP client for potential online database updates or integrations

### System Dependencies
- **wpa_supplicant**: Critical system dependency for WPS authentication attempts without monitor mode
- **iw**: Linux wireless configuration tool used for network scanning
- **pixiewps**: Optional system tool for Pixie Dust attack execution (checked at runtime)

### Data Dependencies
- **vulnwsc.txt**: Flat-file vulnerability database containing MAC prefixes, manufacturers, models, and vulnerability types for 290+ router entries
- Format: `MAC_PREFIX|MANUFACTURER|MODEL|VULN_TYPE|NOTES`
- Database supports multiple vulnerability classifications (Pixie Dust, ComputePIN, EasyBox, D-Link, ASUS algorithms)

### Runtime Requirements
- Python 3.11+ (indicated by badge in README)
- Linux-based operating system (for iw and wpa_supplicant)
- Root/sudo access required for WiFi operations
- Compatible WiFi interface supporting WPS