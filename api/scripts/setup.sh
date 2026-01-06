#!/bin/bash
# Kalembang Setup Script (for Orange Pi 5)

set -e

echo "========================================"
echo "  Kalembang Setup"
echo "========================================"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (sudo)"
    exit 1
fi

# Detect installation directory
INSTALL_DIR="${KALEMBANG_INSTALL_DIR:-/home/orangepi/kalembang}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

echo "Repository: $REPO_DIR"
echo "Install to: $INSTALL_DIR"
echo ""

# Install system dependencies
echo "Installing system dependencies..."
apt-get update
apt-get install -y python3 python3-venv python3-pip

# Check for wiringOP
if ! command -v gpio &> /dev/null; then
    echo ""
    echo "⚠️  wiringOP not found. Please install it for GPIO support."
    echo "   See: https://github.com/orangepi-xunlong/wiringOP"
    echo ""
fi

# Copy files to installation directory
echo "Copying files to $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR"
cp -r "$REPO_DIR/api" "$INSTALL_DIR/"

# Create virtual environment
echo "Creating Python virtual environment..."
cd "$INSTALL_DIR/api"
python3 -m venv .venv

# Install Python dependencies
echo "Installing Python dependencies..."
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt

# Install systemd service
echo "Installing systemd service..."
cp "$INSTALL_DIR/api/systemd/kalembang.service" /etc/systemd/system/

# Reload systemd
systemctl daemon-reload

# Enable and start service
echo "Enabling Kalembang service..."
systemctl enable kalembang.service

echo ""
echo "========================================"
echo "  Setup Complete!"
echo "========================================"
echo ""
echo "Commands:"
echo "  Start:   sudo systemctl start kalembang"
echo "  Stop:    sudo systemctl stop kalembang"
echo "  Status:  sudo systemctl status kalembang"
echo "  Logs:    sudo journalctl -u kalembang -f"
echo ""
echo "API will be available at http://$(hostname -I | awk '{print $1}'):8088"
echo ""

# Ask to start now
read -p "Start Kalembang now? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    systemctl start kalembang
    echo "Kalembang started!"
fi
