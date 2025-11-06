# Changelog

All notable changes to the WPS Penetration Testing Toolkit will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-06

### Added
- **Core Architecture**: Complete modular restructure with `src/` packages
  - `scanner.py`: WiFi scanning with simulation support
  - `wpa_ctrl.py`: wpa_supplicant wrapper with dry-run mode
  - `pixie.py`: Enhanced Pixie Dust attack engine
  - `pingen.py`: Intelligent PIN generation with vendor patterns
  - `bruteforce.py`: Brute force orchestration with resume capability
  - `db.py`: Vulnerability database management (JSON/SQLite)
  - `ui.py`: Terminal UI matching OneShot-Extended style
  - `logger.py`: Consistent logging and timing utilities

- **Pixie Dust Enhancements**:
  - Robust E-Hash1/E-Hash2/Nonce/PKE/PKR parsing with regex
  - Multiple pixiewps variant attempts with fallback strategies
  - Configurable attack depth (`--pixie-depth`)
  - Comprehensive error reporting for missing values
  - Backward-compatible output formatting

- **PIN Generation Intelligence**:
  - Vendor-pattern scoring system with probability rankings
  - Prefix optimization for manufacturer defaults
  - Known PIN prioritization (score: 100.0)
  - Date-based pattern generation (YYYYMMDD)
  - Sequential number patterns
  - Deterministic fallbacks and randomization
  - No duplicate PIN generation

- **Database System**:
  - Structured JSON/SQLite vulnerability database
  - Vendor pattern management with prefixes and templates
  - AP record tracking (BSSID, vendor, model, known PINs, patterns)
  - Database converter tool (`tools/convert_vulnwsc.py`)
  - Sample database with 5 vendor patterns and 3 AP examples

- **User Interface**:
  - Colorized terminal output with colorama
  - OneShot-Extended color scheme
  - `[?]` markers for questions/choices
  - `[i]`, `[+]`, `[-]`, `[!]`, `[*]` status markers
  - Clear sections: selection, scan, attack, results
  - Progress bars and ETA calculations
  - `--no-color`, `--quiet`, `--verbose` flags

- **Multi-AP & Resume**:
  - Multi-target queue from file (`--targets`)
  - Concurrent attack support (`--concurrency`)
  - Progress saving to JSON file
  - Resume interrupted attacks from last PIN
  - Per-AP attack summaries

- **Mobile Support**:
  - Termux/Android compatibility
  - `--mobile` flag for optimized settings
  - CPU throttling options
  - Reduced candidate generation for constrained hardware
  - Adaptive retry/backoff for low RSSI

- **Testing Infrastructure**:
  - Dry-run simulation mode (`--dry-run`)
  - Simulated pixiewps output harness
  - Simulated wpa_supplicant harness
  - 32 unit tests covering core modules
  - 50% overall coverage (core modules: logger 83%, scanner 82%, ui 82%, pingen 70%, db 57%, pixie 52%)
  - Test fixtures with sanitized real-world outputs
  - All tests passing with pytest

- **Documentation**:
  - Professional README with installation, usage, examples
  - Ethics and legal warnings
  - Termux setup instructions
  - Contributing guidelines
  - Code style requirements
  - API documentation with type hints and docstrings

- **Development Tools**:
  - Makefile with common tasks (install, test, run-dry, convert-db)
  - `requirements.txt` with pinned dependencies
  - `pyproject.toml` for modern Python packaging
  - Example Termux setup script
  - Comprehensive `.gitignore`

### Changed
- **Backward Compatibility**: Preserved all error message patterns for automation scripts
  - `[-] Error: wrong PIN code`
  - `[i] Running Pixiewps...`
  - `E-Hash1:`, `E-Hash2:`
  - `[-] WPS pin not found!`
  - `[*] Time taken: X s Y ms`

### Security
- Added comprehensive ethics and legal warnings
- Dry-run mode for safe offline testing
- No dangerous operations committed to repository
- Clear educational-only licensing

### Technical
- Python 3.9+ with full type hints
- Modular functions (<80 lines, single responsibility)
- Comprehensive exception handling
- No uncaught broad exceptions
- Type-safe dataclasses with `field(default_factory=...)`

## [Unreleased]

### Planned
- Web-based monitoring dashboard
- Advanced pixiewps variant exploration
- Plugin system for custom PIN algorithms
- Real-time network state monitoring
- Distributed attack coordination

---

## Version History

- **1.0.0** (2025-11-06): Initial production release
