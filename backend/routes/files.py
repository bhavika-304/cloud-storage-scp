"""
files.py (routes)
-----------------
These are the API endpoints for file operations:
  POST /upload        — Upload a file
  GET  /files         — List all files
  GET  /files/{id}    — Download a specific file
  DELETE /files/{id}  — Delete a file

An "endpoint" is like a door in your backend — each URL is a different door.
FastAPI handles all the HTTP stuff, you just write Python functions.
"""

import os
import uuid
import tempfile
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse

from backend.models.file_model import FileRecord, UploadResponse, FileListResponse
from backend.services import metadata as meta_service
from backend.services.classifier import classify_file, get_category_icon
from backend.services.vm_storage import (
    save_file_locally,
    save_file_to_vm,
    USE_VM_STORAGE,
    LOCAL_STORAGE_PATH,
    download_file_from_vm
)

# Create a router (a group of related endpoints)
router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a file to the cloud storage system.
    
    This endpoint:
    1. Receives the file from the browser
    2. Classifies it (image, code, document, etc.)
    3. Saves it (locally or to VM)
    4. Records metadata (name, size, type, time)
    5. Returns info about the uploaded file
    
    Args:
        file: The uploaded file (sent by the browser form)
    
    Returns:
        UploadResponse with file details
    """
    print(f"\n[Upload] Receiving file: {file.filename}")
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    # Read the file content from the request
    file_content = await file.read()
    file_size = len(file_content)
    
    print(f"[Upload] File size: {file_size} bytes")
    
    # Generate a unique ID for this file
    # We use the filename as the ID (sanitized)
    # In production, you'd use UUID to avoid conflicts
    file_id = file.filename.replace(" ", "_")
    
    # Classify the file type using our classifier
    file_type = classify_file(file.filename)
    icon = get_category_icon(file_type)
    print(f"[Upload] Classified as: {icon} {file_type}")
    
    # Save the file to a temporary location first
    with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as temp:
        temp.write(file_content)
        temp_path = temp.name
    
    try:
        if USE_VM_STORAGE:
            # Phase 4+: Send to VM
            success = save_file_to_vm(temp_path, file_id)
            if not success:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to upload to VM. Check VM connection."
                )
            storage_path = f"vm://{file_id}"
        else:
            # Phase 1-3: Save locally
            storage_path = save_file_locally(temp_path, file_id)
    finally:
        # Always clean up the temp file
        os.unlink(temp_path)
    
    # Create the metadata record
    record = FileRecord(
        file_id=file_id,
        filename=file.filename,
        size_bytes=file_size,
        upload_time=datetime.now().isoformat(),
        storage_path=storage_path,
        file_type=file_type,
        access_count=0,
        is_backed_up=False
    )
    
    # Save metadata to our JSON store
    meta_service.save_file_record(record)
    
    print(f"[Upload] ✅ Done! File saved as: {file_id}")
    
    return UploadResponse(
        success=True,
        message=f"File '{file.filename}' uploaded successfully!",
        file_id=file_id,
        filename=file.filename,
        file_type=file_type,
        size_bytes=file_size
    )


@router.get("/files", response_model=FileListResponse)
async def list_files():
    """
    List all uploaded files with their metadata.
    
    Returns a list of all files with:
    - filename, file_type, size, upload time
    - access count (how many times downloaded)
    - backup status
    """
    print("[Files] Fetching all file records...")
    
    records = meta_service.get_all_records()
    
    print(f"[Files] Found {len(records)} files")
    
    return FileListResponse(
        total_files=len(records),
        files=records
    )


@router.get("/files/{file_id}")
async def download_file(file_id: str):
    """
    Download a specific file by its ID.
    
    This endpoint:
    1. Finds the file record in metadata
    2. Increments the access counter
    3. Serves the file to the browser
    
    Args:
        file_id: The unique file identifier
    
    Returns:
        The actual file content
    """
    print(f"\n[Download] Request for: {file_id}")
    
    # Get the file record from metadata
    record = meta_service.get_file_record(file_id)
    
    if not record:
        raise HTTPException(
            status_code=404,
            detail=f"File '{file_id}' not found"
        )
    
    # Increment access count (tracking file usage)
    meta_service.increment_access_count(file_id)
    
    if USE_VM_STORAGE:
        # Download from VM to a temp location, then serve
        temp_path = f"/tmp/{file_id}"
        success = download_file_from_vm(file_id, temp_path)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve file from VM"
            )
        
        file_path = temp_path
    else:
        # Serve from local storage
        file_path = os.path.join(LOCAL_STORAGE_PATH, file_id)
    
    # Check the file actually exists on disk
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail=f"File not found on disk. It may have been deleted."
        )
    
    print(f"[Download] ✅ Serving file: {record.filename}")
    
    # FileResponse tells FastAPI to send the actual file bytes
    return FileResponse(
        path=file_path,
        filename=record.filename,  # Browser will use this as the download name
        media_type="application/octet-stream"  # Generic binary type = triggers download
    )


@router.get("/files/{file_id}/info")
async def get_file_info(file_id: str):
    """
    Get metadata for a specific file without downloading it.
    
    Args:
        file_id: The unique file identifier
    
    Returns:
        File metadata (type, size, access count, etc.)
    """
    record = meta_service.get_file_record(file_id)
    
    if not record:
        raise HTTPException(status_code=404, detail=f"File '{file_id}' not found")
    
    return record


@router.delete("/files/{file_id}")
async def delete_file(file_id: str):
    """
    Delete a file and its metadata.
    
    Args:
        file_id: The unique file identifier
    
    Returns:
        Success message
    """
    record = meta_service.get_file_record(file_id)
    
    if not record:
        raise HTTPException(status_code=404, detail=f"File '{file_id}' not found")
    
    # Delete from local storage
    if not USE_VM_STORAGE:
        file_path = os.path.join(LOCAL_STORAGE_PATH, file_id)
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"[Delete] Removed file from disk: {file_path}")
    
    # Delete metadata record
    meta_service.delete_file_record(file_id)
    
    return JSONResponse(
        content={
            "success": True,
            "message": f"File '{record.filename}' deleted successfully"
        }
    )