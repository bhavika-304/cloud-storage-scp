"""
vm_storage.py
-------------
This service handles storing files on a remote VM via SCP/SSH.

In Phase 1-3, we use LOCAL storage (files stay on your computer).
In Phase 4+, we switch to VM storage by setting USE_VM_STORAGE = True
and filling in the VM connection details below.

How it works:
  1. File arrives at our FastAPI backend
  2. We save it to a temp location
  3. We SCP (Secure Copy) it to the primary VM
  4. The VM stores it in /cloud-storage/uploads/

Prerequisites for VM mode (Phase 4):
  - A Linux VM with SSH access
  - SSH key authentication set up (no passwords)
  - The paramiko Python library installed
"""

import os
import shutil
import subprocess
from pathlib import Path

# ============================================================
# CONFIGURATION — Change these when you set up your VM
# ============================================================

# Set to True in Phase 4 when you have a VM ready
USE_VM_STORAGE = True

# Your VM's IP address (e.g., "34.123.45.67" for Google Cloud)
VM_HOST = "localhost"

# VM username (usually "ubuntu" for Ubuntu VMs)
VM_USER = "bhavika"

# Path to your SSH private key file
SSH_KEY_PATH = os.path.expanduser("~/.ssh/cloud_storage_key")

# Where files are stored on the VM
VM_STORAGE_PATH = "/home/bhavika/primary_vm"

# ============================================================
# LOCAL STORAGE (used in Phase 1-3)
# ============================================================

# Local directory for storing files (relative to this file)
LOCAL_STORAGE_PATH = os.path.join(
    os.path.dirname(__file__), "..", "storage", "uploads"
)

def ensure_local_storage():
    """Create the local storage directory if it doesn't exist."""
    os.makedirs(LOCAL_STORAGE_PATH, exist_ok=True)


def save_file_locally(temp_path: str, filename: str) -> str:
    """
    Save a file to local storage.
    Used in Phase 1-3 before we have a VM.
    
    Args:
        temp_path: Where the file currently is (temp location)
        filename: The name to save it as
    
    Returns:
        The final path where the file is stored
    """
    ensure_local_storage()
    destination = os.path.join(LOCAL_STORAGE_PATH, filename)
    shutil.copy2(temp_path, destination)
    print(f"[Storage] Saved locally: {destination}")
    return destination


def save_file_to_vm(local_file_path: str, filename: str) -> bool:
    """
    Upload a file to the primary VM using SCP.
    Used in Phase 4+.
    
    SCP = Secure Copy Protocol
    It's like copying a file, but over SSH to another computer.
    
    Command equivalent:
        scp -i ~/.ssh/key file.txt ubuntu@34.123.45.67:/cloud-storage/uploads/
    
    Args:
        local_file_path: Path to the file on our local machine
        filename: Name of the file
    
    Returns:
        True if upload succeeded, False if failed
    """
    if not USE_VM_STORAGE:
        print("[Storage] VM storage is disabled. Using local storage.")
        return False
    
    try:
        # Build the SCP command
        remote_destination = f"{VM_USER}@{VM_HOST}:{VM_STORAGE_PATH}/{filename}"
        
        scp_command = [
            "scp",
            "-i", SSH_KEY_PATH,          # Use SSH key for auth
             "-P", "22", 
            "-o", "StrictHostKeyChecking=no",  # Don't ask to verify host
            local_file_path,              # Source: local file
            remote_destination            # Destination: VM path
        ]
        
        print(f"[Storage] SCP uploading {filename} to VM...")
        
        # Run the SCP command
        result = subprocess.run(
            scp_command,
            capture_output=True,
            text=True,
            timeout=60  # 60 second timeout
        )
        
        if result.returncode == 0:
            print(f"[Storage] ✅ Successfully uploaded {filename} to VM")
            return True
        else:
            print(f"[Storage] ❌ SCP failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"[Storage] ❌ SCP timed out for {filename}")
        return False
    except Exception as e:
        print(f"[Storage] ❌ Error uploading to VM: {e}")
        return False


def get_file_path(filename: str) -> str:
    """
    Get the full path to a stored file.
    Returns local path in Phase 1-3, VM path info in Phase 4+.
    
    Args:
        filename: Name of the file
    
    Returns:
        Full path to the file
    """
    if USE_VM_STORAGE:
        # For VM mode, we download the file first, then serve it
        return f"vm://{VM_HOST}{VM_STORAGE_PATH}/{filename}"
    else:
        return os.path.join(LOCAL_STORAGE_PATH, filename)


def download_file_from_vm(filename: str, local_destination: str) -> bool:
    """
    Download a file FROM the VM to our local machine.
    Used when serving files to users in VM mode.
    
    Args:
        filename: Name of the file on the VM
        local_destination: Where to save it locally (temp)
    
    Returns:
        True if download succeeded
    """
    if not USE_VM_STORAGE:
        return True  # Already local, nothing to do
    
    try:
        remote_source = f"{VM_USER}@{VM_HOST}:{VM_STORAGE_PATH}/{filename}"
        
        scp_command = [
            "scp",
            "-i", SSH_KEY_PATH,
            "-o", "StrictHostKeyChecking=no",
            remote_source,
            local_destination
        ]
        
        result = subprocess.run(
            scp_command,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"[Storage] ❌ Error downloading from VM: {e}")
        return False


def list_files_on_vm() -> list[str]:
    """
    List all files stored on the primary VM.
    Used to verify what's actually on the VM.
    
    Returns:
        List of filenames on the VM
    """
    if not USE_VM_STORAGE:
        # Return local files
        ensure_local_storage()
        return os.listdir(LOCAL_STORAGE_PATH)
    
    try:
        ssh_command = [
            "ssh",
            "-i", SSH_KEY_PATH,
            "-o", "StrictHostKeyChecking=no",
            f"{VM_USER}@{VM_HOST}",
            f"ls {VM_STORAGE_PATH}"
        ]
        
        result = subprocess.run(
            ssh_command,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            return result.stdout.strip().split("\n")
        return []
        
    except Exception as e:
        print(f"[Storage] ❌ Error listing VM files: {e}")
        return []