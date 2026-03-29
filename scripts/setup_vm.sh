#!/bin/bash
# =======================================================
# setup_vm.sh — Set Up a Linux VM for Cloud Storage
# =======================================================
# Run this script ON THE VM after SSH-ing in.
#
# What it does:
#   1. Updates the system
#   2. Creates storage directories
#   3. Sets permissions
#   4. Installs Python (if needed for future use)
#
# Usage:
#   chmod +x setup_vm.sh
#   ./setup_vm.sh
# =======================================================

echo "======================================"
echo "☁️  Setting up Cloud Storage VM"
echo "======================================"

# Update package lists
echo "[1/5] Updating system..."
sudo apt-get update -y

# Install Python 3 and pip (for future scripts on VM)
echo "[2/5] Installing Python..."
sudo apt-get install -y python3 python3-pip

# Create the storage directories
echo "[3/5] Creating storage directories..."
sudo mkdir -p /cloud-storage/uploads
sudo mkdir -p /cloud-storage/backup
sudo mkdir -p /cloud-storage/temp

# Set ownership to current user (so we can write files via SCP)
echo "[4/5] Setting permissions..."
sudo chown -R $USER:$USER /cloud-storage
chmod -R 755 /cloud-storage

# Verify the directories were created
echo "[5/5] Verifying setup..."
ls -la /cloud-storage/

echo ""
echo "======================================"
echo "✅ VM Setup Complete!"
echo "======================================"
echo ""
echo "Directories created:"
echo "  /cloud-storage/uploads  ← Primary file storage"
echo "  /cloud-storage/backup   ← Backup storage (on backup VM)"
echo "  /cloud-storage/temp     ← Temporary files"
echo ""
echo "Next step: Set up SSH keys (run setup_ssh_keys.sh)"