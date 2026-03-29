# # """
# # backup_service.py
# # -----------------
# # This service handles backing up files from the Primary VM to the Backup VM.

# # Architecture:
# #     User → Backend → Primary VM → [SCP] → Backup VM

# # How backup works:
# #     1. Backend SSHes into the Primary VM
# #     2. From the Primary VM, it SCPs the file to the Backup VM
# #     3. We update the metadata to mark the file as backed up

# # Think of it like:
# #     - Primary VM = your main hard drive
# #     - Backup VM = an external drive in a different room
# #     - SCP = the cable connecting them

# # Configuration:
# #     Set these values in Phase 5 when you have both VMs running.
# # """

# # import subprocess
# # import os
# # from datetime import datetime
# # from backend.services import metadata as meta_service
# # from backend.services.classifier import get_backup_priority

# # # ============================================================
# # # BACKUP VM CONFIGURATION — Fill in Phase 5
# # # ============================================================

# # # Set to True in Phase 5
# # # BACKUP_ENABLED = False

# # # # Primary VM details (same as vm_storage.py)
# # # PRIMARY_VM_HOST = "YOUR_PRIMARY_VM_IP"
# # # PRIMARY_VM_USER = "ubuntu"

# # # # Backup VM details
# # # BACKUP_VM_HOST = "YOUR_BACKUP_VM_IP"
# # # BACKUP_VM_USER = "ubuntu"

# # # # SSH key path (same key works for both VMs)
# # # SSH_KEY_PATH = os.path.expanduser("~/.ssh/cloud_storage_key")

# # # # Storage paths
# # # PRIMARY_VM_PATH = "/cloud-storage/uploads"
# # # BACKUP_VM_PATH = "/cloud-storage/backup"
# # BACKUP_ENABLED = True

# # PRIMARY_VM_HOST = "localhost"
# # PRIMARY_VM_USER = "bhavika"

# # BACKUP_VM_HOST = "localhost"
# # BACKUP_VM_USER = "bhavika"

# # PRIMARY_VM_PATH = "/home/bhavika/primary_vm"
# # BACKUP_VM_PATH = "/home/bhavika/backup_vm"

# # def backup_file(filename: str, file_id: str) -> bool:
# #     """
# #     Back up a single file from Primary VM to Backup VM.
    
# #     The command we run on the Primary VM is:
# #         scp /cloud-storage/uploads/file.txt ubuntu@backup-vm:/cloud-storage/backup/
    
# #     We do this by SSHing into the Primary VM and running SCP from there.
    
# #     Args:
# #         filename: Name of the file to back up
# #         file_id: The file's unique ID (to update metadata)
    
# #     Returns:
# #         True if backup succeeded
# #     """
# #     if not BACKUP_ENABLED:
# #         print(f"[Backup] Backup is disabled. Skipping {filename}")
# #         return False
    
# #     try:
# #         print(f"[Backup] Starting backup for: {filename}")
        
# #         # Build the SCP command to run ON the primary VM
# #         # This copies from primary VM to backup VM
# #         remote_scp_command = (
# #             f"scp -o StrictHostKeyChecking=no "
# #             f"-i ~/.ssh/cloud_storage_key "
# #             f"{PRIMARY_VM_PATH}/{filename} "
# #             f"{BACKUP_VM_USER}@{BACKUP_VM_HOST}:{BACKUP_VM_PATH}/{filename}"
# #         )
        
# #         # SSH into the primary VM and run the SCP command
# #         ssh_command = [
# #             "ssh",
# #             "-i", SSH_KEY_PATH,
# #             "-o", "StrictHostKeyChecking=no",
# #             f"{PRIMARY_VM_USER}@{PRIMARY_VM_HOST}",
# #             remote_scp_command  # Run this on the remote VM
# #         ]
        
# #         result = subprocess.run(
# #             ssh_command,
# #             capture_output=True,
# #             text=True,
# #             timeout=120
# #         )
        
# #         if result.returncode == 0:
# #             print(f"[Backup] ✅ Backed up: {filename}")
# #             # Update metadata to record backup success
# #             meta_service.update_backup_status(file_id, is_backed_up=True)
# #             return True
# #         else:
# #             print(f"[Backup] ❌ Backup failed for {filename}: {result.stderr}")
# #             return False
            
# #     except subprocess.TimeoutExpired:
# #         print(f"[Backup] ❌ Backup timed out for {filename}")
# #         return False
# #     except Exception as e:
# #         print(f"[Backup] ❌ Error during backup: {e}")
# #         return False


# # def restore_file(filename: str, file_id: str) -> bool:
# #     """
# #     Restore a file from Backup VM back to Primary VM.
# #     Used when a file is lost or corrupted on the Primary VM.
    
# #     The reverse of backup_file.
    
# #     Args:
# #         filename: Name of the file to restore
# #         file_id: The file's unique ID
    
# #     Returns:
# #         True if restore succeeded
# #     """
# #     if not BACKUP_ENABLED:
# #         print(f"[Backup] Backup is disabled. Cannot restore {filename}")
# #         return False
    
# #     try:
# #         print(f"[Backup] Restoring {filename} from backup VM...")
        
# #         # SCP from backup VM to primary VM storage path
# #         scp_command = [
# #             "scp",
# #             "-i", SSH_KEY_PATH,
# #             "-o", "StrictHostKeyChecking=no",
# #             f"{BACKUP_VM_USER}@{BACKUP_VM_HOST}:{BACKUP_VM_PATH}/{filename}",
# #             f"{PRIMARY_VM_USER}@{PRIMARY_VM_HOST}:{PRIMARY_VM_PATH}/{filename}"
# #         ]
        
# #         result = subprocess.run(
# #             scp_command,
# #             capture_output=True,
# #             text=True,
# #             timeout=120
# #         )
        
# #         if result.returncode == 0:
# #             print(f"[Backup] ✅ Restored: {filename}")
# #             return True
# #         else:
# #             print(f"[Backup] ❌ Restore failed: {result.stderr}")
# #             return False
            
# #     except Exception as e:
# #         print(f"[Backup] ❌ Error during restore: {e}")
# #         return False


# # def smart_backup_all() -> dict:
# #     """
# #     Intelligently back up all files based on their priority.
    
# #     This is the "smart" backup logic:
# #     - High priority files: always back up
# #     - Medium priority: back up if not backed up in 6 hours
# #     - Low priority: back up if not backed up in 24 hours
    
# #     Returns:
# #         Summary dict with counts of backed up, skipped, failed files
# #     """
# #     all_files = meta_service.get_all_records()
    
# #     results = {"backed_up": 0, "skipped": 0, "failed": 0}
    
# #     for file_record in all_files:
# #         priority = get_backup_priority(
# #             file_record.file_type,
# #             file_record.access_count
# #         )
        
# #         should_backup = False
        
# #         if priority == "high":
# #             # Always back up high priority files
# #             should_backup = True
            
# #         elif priority == "medium":
# #             # Back up if not backed up recently (6 hours)
# #             if not file_record.is_backed_up or _hours_since_backup(file_record) > 6:
# #                 should_backup = True
                
# #         elif priority == "low":
# #             # Back up if not backed up recently (24 hours)
# #             if not file_record.is_backed_up or _hours_since_backup(file_record) > 24:
# #                 should_backup = True
        
# #         if should_backup:
# #             success = backup_file(file_record.filename, file_record.file_id)
# #             if success:
# #                 results["backed_up"] += 1
# #             else:
# #                 results["failed"] += 1
# #         else:
# #             results["skipped"] += 1
# #             print(f"[Backup] Skipping {file_record.filename} (priority: {priority}, already backed up)")
    
# #     print(f"[Backup] Smart backup complete: {results}")
# #     return results


# # def _hours_since_backup(file_record) -> float:
# #     """
# #     Calculate how many hours have passed since last backup.
    
# #     Args:
# #         file_record: A FileRecord object
    
# #     Returns:
# #         Number of hours since last backup (float), or 999 if never backed up
# #     """
# #     if not file_record.last_backup_time:
# #         return 999  # Never backed up = treat as very old
    
# #     last_backup = datetime.fromisoformat(file_record.last_backup_time)
# #     now = datetime.now()
# #     delta = now - last_backup
# #     return delta.total_seconds() / 3600  # Convert seconds to hours


# # def list_backup_files() -> list[str]:
# #     """
# #     List all files currently on the backup VM.
    
# #     Returns:
# #         List of filenames on backup VM
# #     """
# #     if not BACKUP_ENABLED:
# #         return []
    
# #     try:
# #         ssh_command = [
# #             "ssh",
# #             "-i", SSH_KEY_PATH,
# #             "-o", "StrictHostKeyChecking=no",
# #             f"{BACKUP_VM_USER}@{BACKUP_VM_HOST}",
# #             f"ls {BACKUP_VM_PATH} 2>/dev/null || echo ''"
# #         ]
        
# #         result = subprocess.run(
# #             ssh_command,
# #             capture_output=True,
# #             text=True,
# #             timeout=30
# #         )
        
# #         if result.returncode == 0 and result.stdout.strip():
# #             return [f for f in result.stdout.strip().split("\n") if f]
# #         return []
        
# #     except Exception as e:
# #         print(f"[Backup] ❌ Error listing backup files: {e}")
# #         return []
# """
# backup_service.py
# -----------------
# This service handles backing up files from the Primary VM to the Backup VM.

# Architecture:
#     User → Backend → Primary VM → [SCP] → Backup VM

# How backup works:
#     1. Backend directly SCPs from Primary VM folder to Backup VM folder
#     2. We update the metadata to mark the file as backed up

# Think of it like:
#     - Primary VM = your main hard drive
#     - Backup VM = an external drive in a different room
#     - SCP = the cable connecting them
# """

# import subprocess
# import os
# from datetime import datetime
# from backend.services import metadata as meta_service
# from backend.services.classifier import get_backup_priority

# # ============================================================
# # BACKUP VM CONFIGURATION
# # ============================================================

# BACKUP_ENABLED = True

# # Primary VM details (source)
# PRIMARY_VM_HOST = "localhost"
# PRIMARY_VM_USER = "bhavika"

# # Backup VM details (destination)
# BACKUP_VM_HOST = "localhost"
# BACKUP_VM_USER = "bhavika"

# # Storage paths
# PRIMARY_VM_PATH = "/home/bhavika/primary_vm"
# BACKUP_VM_PATH = "/home/bhavika/backup_vm"

# # SSH key path
# SSH_KEY_PATH = os.path.expanduser("~/.ssh/id_rsa")


# def backup_file(filename: str, file_id: str) -> bool:
#     """
#     Back up a single file from Primary VM to Backup VM.
    
#     Uses direct SCP from the backend (no nested SSH).
#     Command: scp -P 2222 /path/to/source/file user@localhost:/path/to/dest/
    
#     Args:
#         filename: Name of the file to back up
#         file_id: The file's unique ID (to update metadata)
    
#     Returns:
#         True if backup succeeded
#     """
#     if not BACKUP_ENABLED:
#         print(f"[Backup] Backup is disabled. Skipping {filename}")
#         return False
    
#     try:
#         print(f"[Backup] Smart SCP → {filename}")
        
#         # Build source and destination paths
#         source = f"{PRIMARY_VM_PATH}/{filename}"
#         destination = f"{BACKUP_VM_USER}@{BACKUP_VM_HOST}:{BACKUP_VM_PATH}/{filename}"
        
#         # Build SCP command with port 2222 for backup VM
#         scp_command = [
#             "scp",
#             "-P", "2222",                    # Backup VM SSH port
#             "-i", SSH_KEY_PATH,              # SSH key for authentication
#             "-o", "StrictHostKeyChecking=no", # Don't ask to verify host
#             source,
#             destination
#         ]
        
#         print(f"[Backup] Running: scp -P 2222 {source} → {destination}")
        
#         result = subprocess.run(
#             scp_command,
#             capture_output=True,
#             text=True,
#             timeout=60
#         )
        
#         if result.returncode == 0:
#             print(f"[Backup] ✅ Backed up: {filename}")
#             # Update metadata to record backup success
#             meta_service.update_backup_status(file_id, is_backed_up=True)
#             return True
#         else:
#             print(f"[Backup] ❌ Backup failed for {filename}: {result.stderr}")
#             return False
            
#     except subprocess.TimeoutExpired:
#         print(f"[Backup] ❌ Backup timed out for {filename}")
#         return False
#     except Exception as e:
#         print(f"[Backup] ❌ Error during backup: {e}")
#         return False


# def restore_file(filename: str, file_id: str) -> bool:
#     """
#     Restore a file from Backup VM back to Primary VM.
#     Used when a file is lost or corrupted on the Primary VM.
    
#     The reverse of backup_file.
    
#     Args:
#         filename: Name of the file to restore
#         file_id: The file's unique ID
    
#     Returns:
#         True if restore succeeded
#     """
#     if not BACKUP_ENABLED:
#         print(f"[Backup] Backup is disabled. Cannot restore {filename}")
#         return False
    
#     try:
#         print(f"[Backup] Restoring {filename} from backup VM...")
        
#         # SCP from backup VM to primary VM
#         source = f"{BACKUP_VM_USER}@{BACKUP_VM_HOST}:{BACKUP_VM_PATH}/{filename}"
#         destination = f"{PRIMARY_VM_PATH}/{filename}"
        
#         scp_command = [
#             "scp",
#             "-P", "2222",                    # Backup VM SSH port
#             "-i", SSH_KEY_PATH,
#             "-o", "StrictHostKeyChecking=no",
#             source,
#             destination
#         ]
        
#         result = subprocess.run(
#             scp_command,
#             capture_output=True,
#             text=True,
#             timeout=60
#         )
        
#         if result.returncode == 0:
#             print(f"[Backup] ✅ Restored: {filename}")
#             return True
#         else:
#             print(f"[Backup] ❌ Restore failed: {result.stderr}")
#             return False
            
#     except Exception as e:
#         print(f"[Backup] ❌ Error during restore: {e}")
#         return False


# def smart_backup_all() -> dict:
#     """
#     Intelligently back up all files based on their priority.
    
#     This is the "smart" backup logic:
#     - High priority files: always back up
#     - Medium priority: back up if not backed up in 6 hours
#     - Low priority: back up if not backed up in 24 hours
    
#     Returns:
#         Summary dict with counts of backed up, skipped, failed files
#         Format: {"backed_up": X, "skipped": Y, "failed": Z}
#     """
#     all_files = meta_service.get_all_records()
    
#     results = {"backed_up": 0, "skipped": 0, "failed": 0}
    
#     print(f"[Backup] Starting smart backup for {len(all_files)} files...")
    
#     for file_record in all_files:
#         priority = get_backup_priority(
#             file_record.file_type,
#             file_record.access_count
#         )
        
#         should_backup = False
        
#         if priority == "high":
#             # Always back up high priority files
#             should_backup = True
#             print(f"[Backup] {file_record.filename}: priority=high → backing up")
            
#         elif priority == "medium":
#             # Back up if not backed up recently (6 hours)
#             if not file_record.is_backed_up or _hours_since_backup(file_record) > 6:
#                 should_backup = True
#                 print(f"[Backup] {file_record.filename}: priority=medium, needs backup → backing up")
#             else:
#                 print(f"[Backup] {file_record.filename}: priority=medium, recently backed up → skipping")
                
#         elif priority == "low":
#             # Back up if not backed up recently (24 hours)
#             if not file_record.is_backed_up or _hours_since_backup(file_record) > 24:
#                 should_backup = True
#                 print(f"[Backup] {file_record.filename}: priority=low, needs backup → backing up")
#             else:
#                 print(f"[Backup] {file_record.filename}: priority=low, recently backed up → skipping")
        
#         if should_backup:
#             success = backup_file(file_record.filename, file_record.file_id)
#             if success:
#                 results["backed_up"] += 1
#             else:
#                 results["failed"] += 1
#         else:
#             results["skipped"] += 1
    
#     print(f"[Backup] Smart backup complete: {results}")
#     return results


# def _hours_since_backup(file_record) -> float:
#     """
#     Calculate how many hours have passed since last backup.
    
#     Args:
#         file_record: A FileRecord object
    
#     Returns:
#         Number of hours since last backup (float), or 999 if never backed up
#     """
#     if not file_record.last_backup_time:
#         return 999  # Never backed up = treat as very old
    
#     last_backup = datetime.fromisoformat(file_record.last_backup_time)
#     now = datetime.now()
#     delta = now - last_backup
#     return delta.total_seconds() / 3600  # Convert seconds to hours


# def list_backup_files() -> list[str]:
#     """
#     List all files currently on the backup VM.
    
#     Returns:
#         List of filenames on backup VM
#     """
#     if not BACKUP_ENABLED:
#         return []
    
#     try:
#         # Use SSH to list files on backup VM
#         ssh_command = [
#             "ssh",
#             "-p", "2222",                    # Backup VM SSH port
#             "-i", SSH_KEY_PATH,
#             "-o", "StrictHostKeyChecking=no",
#             f"{BACKUP_VM_USER}@{BACKUP_VM_HOST}",
#             f"ls {BACKUP_VM_PATH} 2>/dev/null || echo ''"
#         ]
        
#         result = subprocess.run(
#             ssh_command,
#             capture_output=True,
#             text=True,
#             timeout=30
#         )
        
#         if result.returncode == 0 and result.stdout.strip():
#             return [f for f in result.stdout.strip().split("\n") if f]
#         return []
        
#     except Exception as e:
#         print(f"[Backup] ❌ Error listing backup files: {e}")
#         return []
"""
backup_service.py
-----------------
Handles backing up files from Primary VM to Backup VM.
"""

import subprocess
import os
from datetime import datetime
from backend.services import metadata as meta_service
from backend.services.classifier import get_backup_priority

# ============================================================
# CONFIGURATION
# ============================================================

BACKUP_ENABLED = True

PRIMARY_VM_HOST = "localhost"
PRIMARY_VM_USER = "bhavika"

BACKUP_VM_HOST = "localhost"
BACKUP_VM_USER = "bhavika"

PRIMARY_VM_PATH = "/home/bhavika/primary_vm"
BACKUP_VM_PATH = "/home/bhavika/backup_vm"

SSH_KEY_PATH = os.path.expanduser("~/.ssh/id_rsa")


def backup_file(filename: str, file_id: str) -> bool:
    """
    Back up a single file using direct SCP.
    """
    if not BACKUP_ENABLED:
        print(f"[Backup] Backup disabled. Skipping {filename}")
        return False
    
    try:
        print(f"[Backup] Smart SCP → {filename}")
        
        source = f"{PRIMARY_VM_PATH}/{filename}"
        destination = f"{BACKUP_VM_USER}@{BACKUP_VM_HOST}:{BACKUP_VM_PATH}/{filename}"
        
        scp_command = [
            "scp",
            "-P", "2222",
            "-i", SSH_KEY_PATH,
            "-o", "StrictHostKeyChecking=no",
            source,
            destination
        ]
        
        result = subprocess.run(scp_command, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print(f"[Backup] ✅ Backed up: {filename}")
            meta_service.update_backup_status(file_id, is_backed_up=True)
            return True
        else:
            print(f"[Backup] ❌ Failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"[Backup] ❌ Error: {e}")
        return False


def restore_file(filename: str, file_id: str) -> bool:
    """
    Restore a file from Backup VM to Primary VM.
    """
    if not BACKUP_ENABLED:
        return False
    
    try:
        print(f"[Backup] Restoring {filename}...")
        
        source = f"{BACKUP_VM_USER}@{BACKUP_VM_HOST}:{BACKUP_VM_PATH}/{filename}"
        destination = f"{PRIMARY_VM_PATH}/{filename}"
        
        scp_command = [
            "scp",
            "-P", "2222",
            "-i", SSH_KEY_PATH,
            "-o", "StrictHostKeyChecking=no",
            source,
            destination
        ]
        
        result = subprocess.run(scp_command, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print(f"[Backup] ✅ Restored: {filename}")
            return True
        else:
            print(f"[Backup] ❌ Restore failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"[Backup] ❌ Error: {e}")
        return False


def smart_backup_all() -> dict:
    """
    Intelligently back up files based on priority.
    
    Returns: {"backed_up": X, "skipped": Y, "failed": Z}
    """
    all_files = meta_service.get_all_records()
    
    results = {"backed_up": 0, "skipped": 0, "failed": 0}
    
    print(f"\n[Smart Backup] Processing {len(all_files)} files...")
    print("=" * 50)
    
    for file_record in all_files:
        priority = get_backup_priority(file_record.file_type, file_record.access_count)
        
        # Calculate hours since last backup
        hours_since = 999
        if file_record.last_backup_time:
            last_backup = datetime.fromisoformat(file_record.last_backup_time)
            hours_since = (datetime.now() - last_backup).total_seconds() / 3600
        
        should_backup = False
        reason = ""
        
        if priority == "high":
            should_backup = True
            reason = "HIGH priority (code/document or >10 downloads)"
            
        elif priority == "medium":
            if not file_record.is_backed_up or hours_since > 6:
                should_backup = True
                reason = f"MEDIUM priority, last backup {hours_since:.1f}h ago (>6h)"
            else:
                reason = f"MEDIUM priority, recently backed up ({hours_since:.1f}h ago)"
                
        elif priority == "low":
            if not file_record.is_backed_up or hours_since > 24:
                should_backup = True
                reason = f"LOW priority, last backup {hours_since:.1f}h ago (>24h)"
            else:
                reason = f"LOW priority, recently backed up ({hours_since:.1f}h ago)"
        
        print(f"  📄 {file_record.filename}")
        print(f"     Type: {file_record.file_type} | Downloads: {file_record.access_count} | Priority: {priority}")
        print(f"     Decision: {reason}")
        
        if should_backup:
            success = backup_file(file_record.filename, file_record.file_id)
            if success:
                results["backed_up"] += 1
                print(f"     ✅ BACKED UP\n")
            else:
                results["failed"] += 1
                print(f"     ❌ FAILED\n")
        else:
            results["skipped"] += 1
            print(f"     ⏭️ SKIPPED\n")
    
    print("=" * 50)
    print(f"[Smart Backup] Complete: {results}")
    
    return results


def list_backup_files() -> list[str]:
    """
    List all files on backup VM.
    """
    if not BACKUP_ENABLED:
        return []
    
    try:
        ssh_command = [
            "ssh",
            "-p", "2222",
            "-i", SSH_KEY_PATH,
            "-o", "StrictHostKeyChecking=no",
            f"{BACKUP_VM_USER}@{BACKUP_VM_HOST}",
            f"ls {BACKUP_VM_PATH} 2>/dev/null || echo ''"
        ]
        
        result = subprocess.run(ssh_command, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and result.stdout.strip():
            return [f for f in result.stdout.strip().split("\n") if f]
        return []
        
    except Exception as e:
        print(f"[Backup] Error listing backup files: {e}")
        return []