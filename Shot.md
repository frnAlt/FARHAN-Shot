# FARHAN-Shot

## Overview

FARHAN-Shot is an advanced WPS (Wi-Fi Protected Setup) penetration testing tool for **authorized security testing only**. It performs Pixie Dust attacks, WPS PIN bruteforce, and Wi-Fi scanning.

**Important:** This tool requires root access, physical WiFi hardware, and Linux system tools (wpa_supplicant, pixiewps, iw). It is designed for use on Linux, Kali, or Android/Termux environments — not a browser-based tool.

## Usage

Run from the shell:

```bash
sudo python3 main.py --help
sudo python3 main.py -i wlan0 -K
sudo python3 main.py -i wlan0 -b <BSSID> -K
```

## Requirements

- Python 3.6+
- wpa_supplicant
- pixiewps
- iw
- Root access

## Legal Disclaimer

For educational and authorized penetration testing only. Do NOT use on networks you do not own or have explicit permission to test.

## User Preferences

- CLI-only tool, no web interface
