#!/data/data/com.termux/files/usr/bin/bash
# WPS Toolkit - Termux Setup and Example Script
# Author: Farhan
#
# WARNING: This script is for EDUCATIONAL PURPOSES ONLY
# Unauthorized access to computer networks is ILLEGAL

set -e

echo "╔══════════════════════════════════════════════════════════╗"
echo "║       WPS Toolkit - Termux Setup & Demo Script          ║"
echo "║                    by Farhan                             ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Ethics and legal warning
echo "⚠️  LEGAL & ETHICS WARNING ⚠️"
echo ""
echo "This tool is for EDUCATIONAL and AUTHORIZED TESTING ONLY."
echo ""
echo "Unauthorized access to computer networks is ILLEGAL and may result in:"
echo "  • Criminal prosecution"
echo "  • Civil liability"
echo "  • Imprisonment and fines"
echo ""
echo "By continuing, you agree that:"
echo "  1. You will ONLY test networks you own or have written permission to test"
echo "  2. You understand the legal consequences of unauthorized access"
echo "  3. You accept full responsibility for your actions"
echo ""
read -p "Do you understand and agree? (yes/no): " agreement

if [ "$agreement" != "yes" ]; then
    echo "Setup cancelled. Exiting."
    exit 1
fi

echo ""
echo "─────────────────────────────────────────────────────────"
echo "Step 1: Checking Termux Environment"
echo "─────────────────────────────────────────────────────────"

# Check if running in Termux
if [ ! -d "/data/data/com.termux" ]; then
    echo "⚠️  Warning: This script is designed for Termux"
    echo "   It may not work correctly in other environments"
fi

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    echo "   Install with: pkg install python"
    exit 1
fi

python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python $python_version detected"

echo ""
echo "─────────────────────────────────────────────────────────"
echo "Step 2: Installing Required Packages"
echo "─────────────────────────────────────────────────────────"

# Update package list
echo "Updating package list..."
pkg update -y

# Install required packages
echo "Installing required packages..."
pkg install -y python git

# Optional: wireless tools (may not work on all devices)
echo ""
echo "Note: Wireless tools may require rooted device"
echo "      The toolkit works in dry-run mode without root"

echo ""
echo "─────────────────────────────────────────────────────────"
echo "Step 3: Installing Python Dependencies"
echo "─────────────────────────────────────────────────────────"

# Install Python packages
pip install --upgrade pip
pip install colorama pytest pytest-cov

echo ""
echo "─────────────────────────────────────────────────────────"
echo "Step 4: Setting Up Database"
echo "─────────────────────────────────────────────────────────"

# Create sample database
if [ -f "tools/convert_vulnwsc.py" ]; then
    python3 tools/convert_vulnwsc.py --create-sample
    echo "✓ Sample database created"
else
    echo "⚠️  Database converter not found, skipping..."
fi

echo ""
echo "─────────────────────────────────────────────────────────"
echo "Step 5: Running Dry-Run Demo"
echo "─────────────────────────────────────────────────────────"
echo ""
echo "This will demonstrate the toolkit in simulation mode"
echo "(no actual wireless hardware required)"
echo ""
read -p "Press Enter to continue..."

# Run dry-run demo
python3 main.py --dry-run --target 00:11:22:33:44:55 --pixie --bruteforce --verbose

echo ""
echo "─────────────────────────────────────────────────────────"
echo "Setup Complete!"
echo "─────────────────────────────────────────────────────────"
echo ""
echo "✓ All dependencies installed"
echo "✓ Dry-run demo completed successfully"
echo ""
echo "Next steps:"
echo "  1. Review the README.md for full documentation"
echo "  2. Always use dry-run mode for testing: --dry-run"
echo "  3. Only test networks you own or have permission for"
echo ""
echo "Example commands:"
echo "  # Scan for WPS APs (requires root/hardware)"
echo "  python3 main.py --scan-only"
echo ""
echo "  # Dry-run simulation (safe, no hardware)"
echo "  python3 main.py --dry-run --target XX:XX:XX:XX:XX:XX --pixie"
echo ""
echo "  # Mobile-optimized attack"
echo "  python3 main.py --mobile --target XX:XX:XX:XX:XX:XX --pixie --bruteforce"
echo ""
echo "Remember: Educational purposes only! 🎓"
echo ""
