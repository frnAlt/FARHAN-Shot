#!/bin/bash
# 
# Root Matrix Installer & Scanner
# Enhanced & Cleaned Version
# 

# Colors and Styles
B="\e[1m"
R="\e[0m"
C_B_GRN="\e[1;32m"
C_D_GRN="\e[0;32m"
C_B_YLW="\e[1;33m"
C_B_RED="\e[1;31m"
C_B_CYN="\e[1;36m"

# Trap for clean interruption
trap 'echo -e "\n${C_B_YLW}[ ! ] Script interrupted by user. Exiting...${R}"; exit 1' SIGINT

clear

echo -e "${C_B_GRN}${B}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                Root Matrix Scanner & Setup                   ║"
echo "╚══════════════════════════════════════════════════════════════╝${R}"
echo ""

# Logging functions
success() { echo -e "${C_B_GRN}[ D ]${R} ${C_D_GRN}${1}${R}"; }
warn()    { echo -e "${C_B_YLW}[ ! ]${R} ${C_B_YLW}${1}${R}"; }
error()   { echo -e "${C_B_RED}[ ✘ ]${R} ${C_B_RED}${1}${R}"; }
info()    { echo -e "${C_B_CYN}[ * ]${R} ${C_B_CYN}${1}${R}"; }

# Spinner function (Improved)
run_with_spinner() {
    local msg="$1"
    shift
    local pid

    "$@" > /dev/null 2>&1 &
    pid=$!

    local spinstr='⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'
    local i=0

    printf "\r${C_B_GRN}[ ${spinstr:0:1} ]${R} ${C_B_YLW}%s...${R}" "$msg"

    while kill -0 "$pid" 2>/dev/null; do
        i=$(( (i + 1) % 10 ))
        printf "\r${C_B_GRN}[ ${spinstr:$i:1} ]${R} ${C_B_YLW}%s...${R}" "$msg"
        sleep 0.08
    done

    wait "$pid"
    local status=$?

    printf "\r\033[K"  # Clear spinner line

    return $status
}

#  Main Operations 

info "Starting Root Matrix Environment Setup..."

# 1. Remove conflicting tsu
if run_with_spinner "Purging conflicting tsu binary" pkg uninstall tsu -y; then
    success "tsu completely removed from system."
else
    warn "No conflicting tsu found or already removed. Continuing..."
fi

# 2. Update & Upgrade
if run_with_spinner "Syncing repositories and upgrading core packages" bash -c "pkg update -y && pkg upgrade -y"; then
    success "Core packages are now up to date."
else
    warn "Some packages could not be updated. Continuing anyway..."
fi

# 3. Install root-repo & sudo
if run_with_spinner "Injecting root repository & sudo environment" bash -c "pkg install root-repo -y && pkg install sudo -y"; then
    success "Sudo framework successfully installed."
else
    error "Failed to install sudo. Please check your internet connection or storage."
    exit 1
fi

echo ""
info "Initiating Root Matrix Scan..."

# Known su binary paths (including Magisk, KernelSU, and APatch)
SU_PATHS=(
    /system/bin/su
    /system/xbin/su
    /data/adb/ksu/bin/su
    /data/adb/ksu/su
    /data/adb/ap/bin/su
    /data/adb/apatch/su
    /data/adb/magisk/su
    /magisk/.core/bin/su
    /sbin/su
    /sbin/bin/su
    /system/sbin/su
    /su/xbin/su
    /su/bin/su
    /system/product/bin/su
    /debug_ramdisk/su
)

root_matrix() {
    # Check if already root
    if [[ "$(id -u 2>/dev/null)" == "0" ]]; then
        success "System is already running as ROOT (uid 0)."
        return 0
    fi

    # Check if su command in PATH grants root access
    if command -v su >/dev/null 2>&1; then
        local su_cmd
        su_cmd="$(command -v su)"
        if "$su_cmd" -c "id -u" 2>/dev/null | grep -q "^0$"; then
            success "Valid root binary verified via PATH at: ${su_cmd}"
            return 0
        fi
    fi

    # Check sudo access
    if command -v sudo >/dev/null 2>&1 && sudo -n true 2>/dev/null; then
        local whoami_out
        whoami_out="$(sudo whoami 2>/dev/null || echo "root")"
        success "Sudo access granted. Identity: ${whoami_out}"
        return 0
    fi

    info "Scanning known root directories for su binary..."

    for path in "${SU_PATHS[@]}"; do
        if [[ -x "$path" ]]; then
            echo -e "      ${C_B_YLW}→ Target acquired:${R} ${path}"

            # Test if the binary actually works as root
            if "$path" -c "id -u" 2>/dev/null | grep -q "^0$"; then
                success "Valid root binary verified at: ${path}"

                echo ""
                echo -ne "${C_B_GRN}[?] Initialize root terminal now? [Y/n]: ${R}"
                read -r ans
                ans="${ans:-y}"  # Default to yes now (more user-friendly)

                if [[ "$ans" =~ ^[Yy]$ ]]; then
                    echo -e "${C_B_GRN}Entering Root Matrix...${R}"
                    exec "$path" -c "export PATH=/data/data/com.termux/files/usr/bin:\$PATH; exec sh"   # Preserves Termux PATH
                else
                    echo ""
                    success "You can manually enter root later using:"
                    echo -e "   ${C_B_CYN}${path} -c sh${R}"
                fi
                return 0
            else
                warn "Found ${path} but it doesn't grant root access."
            fi
        fi
    done

    error "No working root binary found in the matrix."
    warn "Make sure Magisk, KernelSU, or APatch is properly installed and active."
    warn "Try rebooting your device and run this script again."
    return 1
}

# Run the scanner
root_matrix
echo ""

# Final message
if [[ "$(id -u)" -eq 0 ]]; then
    success "Root Matrix successfully activated!"
else
    info "Setup completed. You may need to enable root in your rooting solution."
fi

echo -e "\n${C_B_CYN}Thank you for using Root Matrix Scanner.${R}"
