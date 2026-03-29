"""
metadata.py
-----------
This service handles reading and writing file metadata.
We use a simple JSON file as our "database" for now.
Think of it like a spreadsheet that tracks all files.

In production you'd use a real database (like PostgreSQL or Firestore),
but JSON is perfect for learning.
"""

import json
import os
from datetime import datetime
from typing import Optional
from backend.models.file_model import FileRecord

# Path to our JSON "database" file
METADATA_FILE = os.path.join(os.path.dirname(__file__), "..", "metadata_store.json")


def _load_all() -> dict:
    """
    Load all metadata from the JSON file.
    Returns a dictionary where keys are file_ids.
    """
    if not os.path.exists(METADATA_FILE):
        # If file doesn't exist yet, return empty dict
        return {}
    
    with open(METADATA_FILE, "r") as f:
        content = f.read().strip()
        if not content:
            return {}
        return json.loads(content)


def _save_all(data: dict):
    """
    Save all metadata back to the JSON file.
    We use indent=2 to make it human-readable.
    """
    with open(METADATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def save_file_record(record: FileRecord):
    """
    Save a new file record to our metadata store.
    
    Args:
        record: A FileRecord object with all file info
    """
    all_records = _load_all()
    # Convert Pydantic model to plain dict for JSON storage
    all_records[record.file_id] = record.model_dump()
    _save_all(all_records)
    print(f"[Metadata] Saved record for: {record.filename}")


def get_file_record(file_id: str) -> Optional[FileRecord]:
    """
    Get a single file record by its ID.
    Returns None if not found.
    
    Args:
        file_id: The unique identifier for the file
    """
    all_records = _load_all()
    record_dict = all_records.get(file_id)
    
    if record_dict is None:
        return None
    
    # Convert dict back to FileRecord object
    return FileRecord(**record_dict)


def get_all_records() -> list[FileRecord]:
    """
    Get all file records from the metadata store.
    Returns a list of FileRecord objects.
    """
    all_records = _load_all()
    return [FileRecord(**v) for v in all_records.values()]


def increment_access_count(file_id: str):
    """
    Increase the access count for a file by 1.
    Called every time someone downloads a file.
    
    Args:
        file_id: The unique identifier for the file
    """
    all_records = _load_all()
    
    if file_id in all_records:
        all_records[file_id]["access_count"] += 1
        _save_all(all_records)
        print(f"[Metadata] Access count for {file_id}: {all_records[file_id]['access_count']}")


def update_backup_status(file_id: str, is_backed_up: bool):
    """
    Update whether a file has been backed up.
    
    Args:
        file_id: The unique identifier for the file
        is_backed_up: True if backed up successfully
    """
    all_records = _load_all()
    
    if file_id in all_records:
        all_records[file_id]["is_backed_up"] = is_backed_up
        all_records[file_id]["last_backup_time"] = datetime.now().isoformat()
        _save_all(all_records)
        print(f"[Metadata] Backup status for {file_id}: {is_backed_up}")


def delete_file_record(file_id: str):
    """
    Remove a file record from metadata.
    
    Args:
        file_id: The unique identifier for the file
    """
    all_records = _load_all()
    
    if file_id in all_records:
        del all_records[file_id]
        _save_all(all_records)
        print(f"[Metadata] Deleted record for: {file_id}")