# WPS Penetration Testing Toolkit

**Developer:** Farhan  
**Project:** Porter-union-rom-updates/FARHAN-Shot.git  
**Created:** November 6, 2025

## Overview

A professional, production-quality WPS penetration testing toolkit designed for security researchers and penetration testers. This modernized toolkit consolidates and refactors ideas from OneShot, OneShot-Extended, wipwn, and other public tools with focus on:

- **Reliability & Correctness**: Robust PIN algorithms, enhanced Pixie Dust handling
- **Usability**: Clean terminal UI with colorized output, clear progress indicators
- **Database Integration**: Offline + online hybrid vulnerability database with vendor patterns
- **Modularity**: Well-documented modules with type hints and comprehensive tests
- **Mobile Support**: Termux/Android adaptation with hardware constraint handling
- **Safety**: Dry-run simulation mode for offline testing without root access

## Project Architecture

### Core Modules (`src/`)
- `scanner.py` - WiFi scanning and AP detection with simulation stubs
- `wpa_ctrl.py` - wpa_supplicant interaction wrapper with dry-run mode
- `pixie.py` - Pixie Dust attack engine with robust output parsing
- `pingen.py` - Intelligent PIN generation with vendor-pattern scoring
- `bruteforce.py` - Online/offline brute force orchestration
- `db.py` - Vulnerability database management (JSON/SQLite)
- `ui.py` - Terminal UI utilities with OneShot-Extended style colors
- `logger.py` - Consistent logging and timing utilities

### Testing (`tests/`)
- `simulated_pixie.py` - Pixiewps output simulation harness
- `simulated_wpa.py` - wpa_supplicant output simulation harness
- `test_*.py` - Unit tests with 80%+ coverage target

### Tools & Scripts
- `tools/convert_vulnwsc.py` - Convert vulnwsc.txt to structured DB
- `scripts/run_example.sh` - Termux setup with ethics warnings
- `Makefile` - Common development tasks

## Recent Changes

**2025-11-06: Initial project setup**
- Created modular architecture with src/ packages
- Set up testing infrastructure with simulation harnesses
- Added comprehensive documentation and contribution guidelines

## User Preferences

- Keep [?] markers in UI where appropriate
- Maintain backward compatibility for error messages (automation scripts)
- Preserve OneShot-Extended color style
- Focus on offline/simulation testing (no live hardware required)

## Key Features

1. **Enhanced Pixie Dust Engine**: Robust E-Hash1/E-Hash2/Nonce/PKE/PKR parsing with fallback strategies
2. **Smart PIN Generation**: Vendor-pattern scoring, prefix optimization, probability ranking
3. **Multi-AP Support**: Queue multiple targets with concurrent attack modes
4. **Mobile Optimized**: Termux-compatible with CPU throttling and low-RSSI handling
5. **WPA3 Detection**: Graceful handling with clear messaging about WPS limitations
6. **Dry-Run Mode**: Complete simulation for offline development and testing

## Development Guidelines

- Python 3.9+ with type hints and docstrings
- Single responsibility functions (<80 lines)
- Comprehensive exception handling
- Unit tests for all core algorithms
- Clear inline comments for complex logic

## Ethics & Legal Notice

**Educational purposes only.** This toolkit is designed for authorized security testing and research. Unauthorized access to computer networks is illegal. Users are solely responsible for ensuring compliance with all applicable laws and regulations.

## Attribution

Inspired by and references:
- OneShot / OneShot-Extended (PIN generation patterns)
- wipwn (database heuristics)
- pixiewps (Pixie Dust mechanics)
- wpa_supplicant documentation

All code reimplemented in original style with proper attribution.
