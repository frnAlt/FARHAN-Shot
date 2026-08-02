<div align="center">

```
  ___  _   ____  _  _   __   _  _     ____  _  _   __  ____
 / __)( ) (  _ \( )( ) / _\ ( \( )   / ___)( )( ) /  \(_  _)
( (__  )(  ) __/ )() (/    \ )  (    \___ \ )__(  (  O ) )(
 \___)(__)(__)  \____/ \_/\_/(_)\_)   (____/(_)(_) \__/ (__)
```

**FARHAN-Shot** — WPS Penetration Testing Tool

[![Version](https://img.shields.io/badge/version-2.3.0-brightgreen)](https://github.com/Gtajisan/FARHAN-Shot)
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Kali%20%7C%20Termux-blue)](https://termux.com)
[![License](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)
[![Author](https://img.shields.io/badge/author-Gtajisan-informational)](https://github.com/Gtajisan)

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

## Installation

**Linux / Kali**
```bash
sudo apt install -y wpasupplicant pixiewps iw python3
git clone --depth 1 https://github.com/Gtajisan/FARHAN-Shot.git
cd FARHAN-Shot
sudo python3 main.py --help
```

**Android / Termux — One-liner**
```bash
curl -sSf https://raw.githubusercontent.com/Gtajisan/FARHAN-Shot_Termux_installer/master/installer.sh | bash
```

**Android / Termux — Manual**
```bash
pkg update && pkg upgrade -y
pkg install root-repo git tsu python wpa-supplicant pixiewps iw openssl -y
termux-setup-storage
git clone --depth 1 https://github.com/Gtajisan/FARHAN-Shot.git
cd FARHAN-Shot
sudo python3 main.py -i wlan0 -K
```

**Update / Uninstall**
```bash
cd FARHAN-Shot && git pull          # update
sudo rm -rf FARHAN-Shot             # uninstall
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
| **Gtajisan** | FARHAN-Shot — all enhancements |

---

<div align="center">

<a href="https://youtu.be/5janYQg1-Yw?si=jua2TI2c_k9slAkC">YouTube</a> &nbsp;·&nbsp;
<a href="https://github.com/Gtajisan/FARHAN-Shot">GitHub</a>

![](https://img.shields.io/github/stars/Gtajisan/FARHAN-Shot?style=social)
&nbsp;
![](https://img.shields.io/github/forks/Gtajisan/FARHAN-Shot?style=social)

<sub>Built for security professionals. Use responsibly.</sub>

</div>
