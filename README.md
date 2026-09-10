<div align="center">

```
  ___  _   ____  _  _   __   _  _     ____  _  _   __  ____
 / __)( ) (  _ \( )( ) / _\ ( \( )   / ___)( )( ) /  \(_  _)
( (__  )(  ) __/ )() (/    \ )  (    \___ \ )__(  (  O ) )(
 \___)(__)(__)  \____/ \_/\_/(_)\_)   (____/(_)(_) \__/ (__)
```

**FARHAN-Shot** — WPS Penetration Testing Tool

[![Version](https://img.shields.io/badge/version-2.3.0-brightgreen)](https://github.com/frnAlt/FARHAN-Shot)
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Kali%20%7C%20Termux-blue)](https://termux.com)
[![License](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)
[![Author](https://img.shields.io/badge/author-frnAlt-informational)](https://github.com/frnAlt)

> For authorized security testing only. Do not use on networks you don't own.

</div>

---

## What It Does

FARHAN-Shot automates WPS attacks against Wi-Fi routers. No monitor mode needed — runs in managed mode via `wpa_supplicant`.

| Attack | Flag | Speed |
|---|---|---|
| Pixie Dust — offline PIN crack | `-K` | Fast |
| PIN Bruteforce — ~11k combinations | `-B` | Slow |
| Push-Button Connect — no PIN | `--pbc` | Instant |

---

## Requirements

```
Python 3.6+   wpa_supplicant   pixiewps   iw   Root/sudo
```

---

## Installation & Setup

### 🐧 Linux / Kali Linux
```bash
# 1. Install system dependencies
sudo apt update && sudo apt install -y wpasupplicant pixiewps iw python3 git

# 2. Clone repository & run
git clone --depth 1 https://github.com/frnAlt/FARHAN-Shot.git
cd FARHAN-Shot
sudo python3 main.py -i wlan0 -K
```

---

### 📱 Android / Termux (Rooted)

> **Note:** Root access (`sudo` via Magisk / KernelSU / APatch) is required for Termux Wi-Fi hardware control.

**Option A: One-Liner Installer**
```bash
curl -sSf https://raw.githubusercontent.com/frnAlt/FARHAN-Shot/core/installer.sh | bash
```

**Option B: Manual Setup**
```bash
# 1. Update packages & install dependencies (use 'sudo' instead of obsolete 'tsu')
pkg update && pkg upgrade -y
pkg install root-repo -y
pkg install git python wpa-supplicant pixiewps iw openssl -y
pkg install sudo

# 2. Grant storage permissions
termux-setup-storage

# 3. Clone & run
git clone --depth 1 https://github.com/frnAlt/FARHAN-Shot.git
cd FARHAN-Shot
sudo python3 main.py -i wlan0 -K
```

**Option C: Quick Shortcut & Helper Scripts**
```bash
# Set up Root Matrix & verify su/sudo environment (Termux):
bash assets/su.sh

# Install FARHAN-Shot binary system-wide in Termux:
python3 assets/setup.py install

# Or launch directly with runner script:
bash assets/FARHAN-Shot.sh
```

> **📱 Android Termux Quick Checklist:**
> 1. Turn Wi-Fi OFF in Android settings (prevents Android OS from controlling the Wi-Fi card).
> 2. Enable Android Location (GPS) services (required by Android kernel to expose Wi-Fi scan results).
> 3. Turn ON Mobile Hotspot (forces kernel to keep `wlan0` interface powered and active).
> 4. Run `sudo python3 main.py -i wlan0 -K` in Termux.

---

### 🔄 Auto-Update / Uninstall
```bash
# Update to latest version
cd FARHAN-Shot && git pull

# Uninstall via setup script (Termux)
python3 assets/setup.py uninstall

# Or remove repository directory
sudo rm -rf FARHAN-Shot
```

---

## Usage

```bash
sudo python3 main.py [OPTIONS]
```

```bash
# Scan nearby networks and attack
sudo python3 main.py -K

# Specify interface
sudo python3 main.py -i wlan0 -K

# Target a specific router
sudo python3 main.py -i wlan0 -b AA:BB:CC:DD:EE:FF -K

# Bruteforce
sudo python3 main.py -i wlan0 -b AA:BB:CC:DD:EE:FF -B

# Scan only — no attack
sudo python3 main.py --scan-only

# Save results
sudo python3 main.py -i wlan0 -b AA:BB:CC:DD:EE:FF -K -w -o results.json
```

> **Android tip:** Turn Wi-Fi off → enable Hotspot → enable Location → run as root.

---

## Options

| Flag | What it does |
|---|---|
| `-i` | Wireless interface (auto-detected if omitted) |
| `-b` | Target BSSID — skips scan |
| `-K` | Pixie Dust attack |
| `-B` | PIN Bruteforce |
| `--pbc` | Push-Button Connect |
| `-p` | Use a specific PIN |
| `--all-pins` | Try all 108+ algorithm PINs |
| `--scan-only` | Scan and exit |
| `--channel` | Limit scan to one channel |
| `-F` | Force full PIN range in Pixie Dust |
| `-w` | Save credentials to file |
| `-o` | Export results to JSON |
| `-d` | Delay between attempts (seconds) |
| `--timeout` | WPS timeout per attempt (default: 30s) |
| `-l` | Loop back to scan after each attack |
| `-v` | Verbose wpa_supplicant output |
| `--no-color` | Strip colors (good for logging) |
| `--vuln-list` | Custom vulnerable device list file (default: `assets/vulnwsc.txt`) |
| `--mtk-wifi` | MediaTek driver fix (Android) |
| `--iface-down` | Bring interface down on exit |

---

## Troubleshooting

| Problem | Fix |
|---|---|
| RF-kill blocked | `sudo rfkill unblock wifi` |
| Interface busy | `sudo systemctl stop NetworkManager` |
| wpa_supplicant socket error | `sudo pkill wpa_supplicant` then retry |
| pixiewps not found | `sudo apt install pixiewps` or `pkg install pixiewps` |
| Interface disappears (MediaTek) | Add `--mtk-wifi` |
| Pixie Dust fails to find PIN | Try `-F` or `--timeout 60` |
| WPS locked | Use `-K` — needs only one handshake |
| No networks found | Retry: `sudo python3 main.py --scan-only` |

---

## 📁 Repository Structure & Assets

| Path | Description |
|---|---|
| `main.py` | Main WPS penetration testing engine and CLI entry point |
| `installer.sh` | One-liner Termux installer script |
| `assets/pins.csv` | Static WPS PIN database (3,336+ entries) |
| `assets/vulnwsc.txt` | Known vulnerable WPS router model database |
| `assets/vulnwsc_original.txt` | Original WPS vulnerability database archive |
| `assets/su.sh` | Termux root matrix scanner and sudo environment setup script |
| `assets/setup.py` | Termux installation and launcher setup script |
| `assets/FARHAN-Shot.sh` | Quick launcher runner script |

---

## Screenshots

<p align="center">
<img width="48%" src="https://i.postimg.cc/fbzJnQL6/Screenshot-20231026-084714-Termux.png"/>
&nbsp;
<img width="48%" src="https://i.postimg.cc/MKhWpDTR/Screenshot-20231029-202035-Termux.png"/>
</p>

---

## Credits

| | |
|---|---|
| [DRYGDRYG](https://github.com/drygdryg) | Core OneShot architecture |
| [rofl0r](https://github.com/rofl0r) | Initial OneShot implementation |
| [Wiire](https://github.com/wiire-a) | pixiewps |
| [fr0stb1rd](https://github.com/fr0stb1rd) | WPS PIN algorithms |
| **Gtajisan** | FARHAN-Shot — all enhancements main lead  |

---

<div align="center">

<a href="https://youtu.be/5janYQg1-Yw?si=jua2TI2c_k9slAkC">YouTube</a> &nbsp;·&nbsp;
<a href="https://github.com/frnAlt/FARHAN-Shot">GitHub</a>

![](https://img.shields.io/github/stars/frnAlt/FARHAN-Shot?style=social)
&nbsp;
![](https://img.shields.io/github/forks/frnAlt/FARHAN-Shot?style=social)

<sub>Built for security professionals. Use responsibly.</sub>

</div>
