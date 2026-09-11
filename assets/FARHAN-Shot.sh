#!/bin/bash
# FARHAN-Shot Quick Launcher Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_DIR="${SCRIPT_DIR}"
[ ! -f "${TARGET_DIR}/main.py" ] && TARGET_DIR="${HOME}/FARHAN-Shot"

if [ ! -f "${TARGET_DIR}/main.py" ]; then
    echo -e "\033[1;31m[✘] Error: main.py not found in ${TARGET_DIR}\033[0m"
    exit 1
fi

cd "${TARGET_DIR}" || exit 1

# Try running with sudo; fallback to su if sudo is not available
if command -v sudo >/dev/null 2>&1; then
    sudo python3 main.py -i wlan0 -K "$@"
elif command -v su >/dev/null 2>&1; then
    su -c "export PATH=/data/data/com.termux/files/usr/bin:\$PATH; python3 main.py -i wlan0 -K $*"
else
    python3 main.py -i wlan0 -K "$@"
fi
