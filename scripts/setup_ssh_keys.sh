#!/bin/bash
# =======================================================
# setup_ssh_keys.sh — Set Up SSH Keys for VM Access
# =======================================================
# Run this script on YOUR LOCAL MACHINE (not the VM).
#
# What is SSH key authentication?
# --------------------------------
# Normally SSH needs a password. But our Python scripts
# run automatically — we can't type a password each time.
#
# SSH keys solve this:
#   - You generate a KEY PAIR (two files):
#       private key: kept SECRET on your machine (~/.ssh/cloud_storage_key)
#       public key:  copied to the VM          (~/.ssh/authorized_keys)
#   - When connecting, SSH uses math to prove identity without passwords
#
# Usage:
#   chmod +x setup_ssh_keys.sh
#   ./setup_ssh_keys.sh
#
# Then follow the prompts to copy the key to your VMs.
# =======================================================

echo "======================================"
echo "🔐 Setting Up SSH Keys for Cloud Storage"
echo "======================================"

KEY_NAME="cloud_storage_key"
KEY_PATH="$HOME/.ssh/$KEY_NAME"

# Step 1: Generate SSH key pair
if [ -f "$KEY_PATH" ]; then
    echo "⚠️  SSH key already exists at $KEY_PATH"
    read -p "Generate a new one? (y/n): " REGEN
    if [ "$REGEN" != "y" ]; then
        echo "Using existing key."
    else
        ssh-keygen -t ed25519 -f "$KEY_PATH" -N "" -C "cloud-storage-key"
        echo "✅ New SSH key generated"
    fi
else
    echo "[1/3] Generating SSH key pair..."
    ssh-keygen -t ed25519 -f "$KEY_PATH" -N "" -C "cloud-storage-key"
    echo "✅ Key generated at: $KEY_PATH"
fi

# Step 2: Display the public key
echo ""
echo "======================================"
echo "📋 Your PUBLIC KEY (copy this to your VMs):"
echo "======================================"
cat "$KEY_PATH.pub"
echo ""
echo "======================================"

# Step 3: Instructions to copy to VM
echo ""
echo "Now copy your key to your VMs using ONE of these methods:"
echo ""
echo "METHOD 1 (Easiest) — Use ssh-copy-id:"
echo "  ssh-copy-id -i $KEY_PATH.pub ubuntu@YOUR_PRIMARY_VM_IP"
echo "  ssh-copy-id -i $KEY_PATH.pub ubuntu@YOUR_BACKUP_VM_IP"
echo ""
echo "METHOD 2 (Manual) — Copy key content and paste on VM:"
echo "  1. SSH into your VM with password:  ssh ubuntu@YOUR_VM_IP"
echo "  2. Run: mkdir -p ~/.ssh && nano ~/.ssh/authorized_keys"
echo "  3. Paste the public key above and save (Ctrl+X, Y, Enter)"
echo "  4. Run: chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys"
echo ""
echo "METHOD 3 — For Google Cloud VMs:"
echo "  Go to: GCP Console → Compute Engine → Metadata → SSH Keys"
echo "  Click 'Add SSH Key' and paste your public key"
echo ""

# Step 4: Test the connection
echo "After copying the key, TEST it:"
echo ""
echo "  ssh -i $KEY_PATH ubuntu@YOUR_PRIMARY_VM_IP 'echo Connected to Primary VM!'"
echo "  ssh -i $KEY_PATH ubuntu@YOUR_BACKUP_VM_IP  'echo Connected to Backup VM!'"
echo ""
echo "If you see 'Connected to VM!' — setup is complete! 🎉"
echo ""
echo "======================================"
echo "✅ SSH Key Setup Instructions Done"
echo "======================================"