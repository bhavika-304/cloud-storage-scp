"""
file_model.py
-------------
These are our data models — they define what a "file record" looks like.
Think of it like a template or blueprint for every file we store.
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class FileRecord(BaseModel):
    """Represents metadata for a single uploaded file."""
    
    # Unique ID for the file (we'll use the filename for now)
    file_id: str
    
    # Original name of the file (e.g., "photo.jpg")
    filename: str
    
    # Size of the file in bytes
    size_bytes: int
    
    # When the file was uploaded (automatically set)
    upload_time: str
    
    # Where the file is stored on disk
    storage_path: str
    
    # File type category — will be filled in Phase 3
    # Options: "image", "code", "document", "other"
    file_type: str = "other"
    
    # How many times this file has been accessed/downloaded
    access_count: int = 0
    
    # Whether this file has been backed up to the backup VM
    is_backed_up: bool = False
    
    # When it was last backed up (None if never)
    last_backup_time: Optional[str] = None


class UploadResponse(BaseModel):
    """Response we send back after a file is uploaded."""
    
    success: bool
    message: str
    file_id: str
    filename: str
    file_type: str
    size_bytes: int


class FileListResponse(BaseModel):
    """Response for listing all files."""
    
    total_files: int
    files: list[FileRecord]