# FARHAN-Shot

FARHAN-Shot is an advanced WPS (Wi-Fi Protected Setup) penetration testing framework built in Python 3. It automates wireless security audits targeting WPS vulnerabilities through Pixie Dust attacks and PIN brute-forcing.

## Important Notice

This tool is designed for **authorized security testing only**. Do not use on networks you do not own or have explicit permission to test.

## Running the Tool

This is a command-line tool. Use the Shell to run it directly:

```bash
sudo python3 main.py --help
```

**Note:** Full functionality requires:
- Root/sudo privileges
- A wireless network interface
- System tools: `wpa_supplicant`, `pixiewps`, `iw`

These hardware and system-level requirements are not available in Replit's environment. The tool can be explored and developed here, but actual attacks must be run on a compatible Linux system (Kali Linux, Termux, etc.).

## Common Usage

| Attack | Command |
|--------|---------|
| Pixie Dust | `sudo python3 main.py -i wlan0 -K` |
| PIN Bruteforce | `sudo python3 main.py -i wlan0 -B` |
| Push-Button Connect | `sudo python3 main.py -i wlan0 --pbc` |
| Show help | `python3 main.py --help` |

## Project Structure

- `main.py` — Core logic (8000+ lines), entry point
- `pins.csv` — Database of known WPS PINs
- `vulnwsc.txt` — Database of vulnerable WPS configurations
- `setup.py` — Installation script (Termux)
- `installer.sh` — One-liner installer for Android/Termux

## Dependencies

- Python 3.6+
- `colorama` (optional, for colored output) — installed via pip
- System: `wpa_supplicant`, `pixiewps`, `iw`, `openssl`

## User Preferences

<!-- Add user preferences here -->
