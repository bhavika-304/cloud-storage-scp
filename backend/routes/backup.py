# # """
# # backup.py (routes)
# # ------------------
# # API endpoints for backup and restore operations:
# #   POST /backup/{file_id}   — Back up a specific file
# #   POST /backup/all         — Run smart backup for all files
# #   POST /restore/{file_id}  — Restore a file from backup VM
# #   GET  /backup/status      — List all files and their backup status
# #   GET  /backup/list        — List files currently on backup VM
# # """

# # from fastapi import APIRouter, HTTPException
# # from fastapi.responses import JSONResponse

# # from backend.services import metadata as meta_service
# # from backend.services import backup_service
# # from backend.services.classifier import get_backup_priority

# # router = APIRouter()


# # @router.post("/backup/{file_id}")
# # async def backup_single_file(file_id: str):
# #     """
# #     Back up a specific file from Primary VM to Backup VM.
    
# #     Args:
# #         file_id: The unique identifier for the file to back up
# #     """
# #     record = meta_service.get_file_record(file_id)
    
# #     if not record:
# #         raise HTTPException(status_code=404, detail=f"File '{file_id}' not found")
    
# #     print(f"\n[API] Backup requested for: {record.filename}")
    
# #     success = backup_service.backup_file(record.filename, file_id)
    
# #     if success:
# #         return JSONResponse(content={
# #             "success": True,
# #             "message": f"File '{record.filename}' backed up successfully",
# #             "file_id": file_id
# #         })
# #     else:
# #         return JSONResponse(
# #             status_code=500,
# #             content={
# #                 "success": False,
# #                 "message": "Backup failed. Check that backup is enabled and VMs are reachable.",
# #                 "tip": "Set BACKUP_ENABLED = True in backup_service.py and configure VM IPs"
# #             }
# #         )


# # @router.post("/backup/all")
# # async def backup_all_files():
# #     """
# #     Run the smart backup for ALL files.
# #     Files are backed up based on their priority:
# #     - High: always backed up
# #     - Medium: backed up if not done in 6 hours  
# #     - Low: backed up if not done in 24 hours
# #     """
# #     print("\n[API] Smart backup all files triggered")
    
# #     results = backup_service.smart_backup_all()
    
# #     return JSONResponse(content={
# #         "success": True,
# #         "message": "Smart backup completed",
# #         "results": results
# #     })


# # @router.post("/restore/{file_id}")
# # async def restore_file(file_id: str):
# #     """
# #     Restore a file from Backup VM back to Primary VM.
# #     Use this when a file is lost or corrupted on the primary VM.
    
# #     Args:
# #         file_id: The unique identifier for the file to restore
# #     """
# #     record = meta_service.get_file_record(file_id)
    
# #     if not record:
# #         raise HTTPException(status_code=404, detail=f"File '{file_id}' not found in metadata")
    
# #     if not record.is_backed_up:
# #         raise HTTPException(
# #             status_code=400,
# #             detail=f"File '{record.filename}' has not been backed up yet"
# #         )
    
# #     print(f"\n[API] Restore requested for: {record.filename}")
    
# #     success = backup_service.restore_file(record.filename, file_id)
    
# #     if success:
# #         return JSONResponse(content={
# #             "success": True,
# #             "message": f"File '{record.filename}' restored successfully from backup VM",
# #             "file_id": file_id
# #         })
# #     else:
# #         return JSONResponse(
# #             status_code=500,
# #             content={
# #                 "success": False,
# #                 "message": "Restore failed. Check backup VM connection."
# #             }
# #         )


# # @router.get("/backup/status")
# # async def get_backup_status():
# #     """
# #     Get backup status for ALL files.
# #     Shows which files are backed up, their priority, and last backup time.
# #     """
# #     all_records = meta_service.get_all_records()
    
# #     status_list = []
# #     for record in all_records:
# #         priority = get_backup_priority(record.file_type, record.access_count)
        
# #         status_list.append({
# #             "file_id": record.file_id,
# #             "filename": record.filename,
# #             "file_type": record.file_type,
# #             "access_count": record.access_count,
# #             "is_backed_up": record.is_backed_up,
# #             "last_backup_time": record.last_backup_time,
# #             "backup_priority": priority
# #         })
    
# #     # Sort by priority (high first)
# #     priority_order = {"high": 0, "medium": 1, "low": 2}
# #     status_list.sort(key=lambda x: priority_order.get(x["backup_priority"], 3))
    
# #     return JSONResponse(content={
# #         "total_files": len(status_list),
# #         "backup_enabled": backup_service.BACKUP_ENABLED,
# #         "files": status_list
# #     })


# # @router.get("/backup/list")
# # async def list_backup_vm_files():
# #     """
# #     List all files currently stored on the Backup VM.
# #     Useful to verify what's been backed up.
# #     """
# #     files = backup_service.list_backup_files()
    
# #     return JSONResponse(content={
# #         "backup_enabled": backup_service.BACKUP_ENABLED,
# #         "total_files": len(files),
# #         "files": files,
# #         "backup_vm": backup_service.BACKUP_VM_HOST
# #     })
# """
# backup.py (routes)
# ------------------
# API endpoints for backup and restore operations:
#   POST /backup/{file_id}   — Back up a specific file
#   POST /backup/all         — Run smart backup for all files
#   POST /restore/{file_id}  — Restore a file from backup VM
#   GET  /backup/status      — List all files and their backup status
#   GET  /backup/list        — List files currently on backup VM
# """

# from fastapi import APIRouter, HTTPException
# from fastapi.responses import JSONResponse

# from backend.services import metadata as meta_service
# from backend.services import backup_service
# from backend.services.classifier import get_backup_priority

# router = APIRouter()


# @router.post("/backup/{file_id}")
# async def backup_single_file(file_id: str):
#     """
#     Back up a specific file from Primary VM to Backup VM.
    
#     Args:
#         file_id: The unique identifier for the file to back up
#     """
#     record = meta_service.get_file_record(file_id)
    
#     if not record:
#         raise HTTPException(status_code=404, detail=f"File '{file_id}' not found")
    
#     print(f"\n[API] Backup requested for: {record.filename}")
    
#     success = backup_service.backup_file(record.filename, file_id)
    
#     if success:
#         return JSONResponse(content={
#             "success": True,
#             "message": f"File '{record.filename}' backed up successfully",
#             "file_id": file_id
#         })
#     else:
#         return JSONResponse(
#             status_code=500,
#             content={
#                 "success": False,
#                 "message": "Backup failed. Check that backup is enabled and VMs are reachable.",
#                 "tip": "Make sure backup VM is running on port 2222"
#             }
#         )


# @router.post("/backup/all")
# async def backup_all_files():
#     """
#     Run the smart backup for ALL files.
#     Files are backed up based on their priority:
#     - High: always backed up
#     - Medium: backed up if not done in 6 hours  
#     - Low: backed up if not done in 24 hours
#     """
#     print("\n[API] Smart backup all files triggered")
    
#     results = backup_service.smart_backup_all()
    
#     # Return the results in the format frontend expects
#     return JSONResponse(content={
#         "success": True,
#         "message": "Smart backup completed",
#         "results": results  # This has backed_up, skipped, failed
#     })


# @router.post("/restore/{file_id}")
# async def restore_file(file_id: str):
#     """
#     Restore a file from Backup VM back to Primary VM.
#     Use this when a file is lost or corrupted on the primary VM.
    
#     Args:
#         file_id: The unique identifier for the file to restore
#     """
#     record = meta_service.get_file_record(file_id)
    
#     if not record:
#         raise HTTPException(status_code=404, detail=f"File '{file_id}' not found in metadata")
    
#     if not record.is_backed_up:
#         raise HTTPException(
#             status_code=400,
#             detail=f"File '{record.filename}' has not been backed up yet"
#         )
    
#     print(f"\n[API] Restore requested for: {record.filename}")
    
#     success = backup_service.restore_file(record.filename, file_id)
    
#     if success:
#         return JSONResponse(content={
#             "success": True,
#             "message": f"File '{record.filename}' restored successfully from backup VM",
#             "file_id": file_id
#         })
#     else:
#         return JSONResponse(
#             status_code=500,
#             content={
#                 "success": False,
#                 "message": "Restore failed. Check backup VM connection."
#             }
#         )


# @router.get("/backup/status")
# async def get_backup_status():
#     """
#     Get backup status for ALL files.
#     Shows which files are backed up, their priority, and last backup time.
#     """
#     all_records = meta_service.get_all_records()
    
#     status_list = []
#     for record in all_records:
#         priority = get_backup_priority(record.file_type, record.access_count)
        
#         status_list.append({
#             "file_id": record.file_id,
#             "filename": record.filename,
#             "file_type": record.file_type,
#             "access_count": record.access_count,
#             "is_backed_up": record.is_backed_up,
#             "last_backup_time": record.last_backup_time,
#             "backup_priority": priority
#         })
    
#     # Sort by priority (high first)
#     priority_order = {"high": 0, "medium": 1, "low": 2}
#     status_list.sort(key=lambda x: priority_order.get(x["backup_priority"], 3))
    
#     return JSONResponse(content={
#         "total_files": len(status_list),
#         "backup_enabled": backup_service.BACKUP_ENABLED,
#         "files": status_list
#     })


# @router.get("/backup/list")
# async def list_backup_vm_files():
#     """
#     List all files currently stored on the Backup VM.
#     Useful to verify what's been backed up.
#     """
#     files = backup_service.list_backup_files()
    
#     return JSONResponse(content={
#         "backup_enabled": backup_service.BACKUP_ENABLED,
#         "total_files": len(files),
#         "files": files,
#         "backup_vm": backup_service.BACKUP_VM_HOST
#     })
"""
backup.py (routes)
------------------
API endpoints for backup and restore operations
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from backend.services import metadata as meta_service
from backend.services import backup_service
from backend.services.classifier import get_backup_priority

# Create router WITHOUT prefix - we'll add prefix in main.py
router = APIRouter(tags=["Backup & Restore"])


@router.post("/backup/{file_id}")
async def backup_single_file(file_id: str):
    """
    Back up a specific file from Primary VM to Backup VM.
    """
    record = meta_service.get_file_record(file_id)
    
    if not record:
        raise HTTPException(status_code=404, detail=f"File '{file_id}' not found")
    
    print(f"\n[API] Backup requested for: {record.filename}")
    
    success = backup_service.backup_file(record.filename, file_id)
    
    if success:
        return JSONResponse(content={
            "success": True,
            "message": f"File '{record.filename}' backed up successfully",
            "file_id": file_id
        })
    else:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Backup failed. Check that backup VM is running on port 2222"
            }
        )


@router.post("/backup/all")
async def backup_all_files():
    """
    Run the smart backup for ALL files.
    
    Smart backup logic:
    - HIGH priority (code, document, or downloaded >10x): ALWAYS backup
    - MEDIUM priority (video, audio, or image with >2 downloads): 
      Backup if >6 hours since last backup
    - LOW priority (everything else):
      Backup if >24 hours since last backup
    """
    print("\n[API] Smart backup all files triggered")
    
    results = backup_service.smart_backup_all()
    
    return JSONResponse(content={
        "success": True,
        "message": "Smart backup completed",
        "results": results  # {backed_up: X, skipped: Y, failed: Z}
    })


@router.post("/restore/{file_id}")
async def restore_file(file_id: str):
    """
    Restore a file from Backup VM back to Primary VM.
    """
    record = meta_service.get_file_record(file_id)
    
    if not record:
        raise HTTPException(status_code=404, detail=f"File '{file_id}' not found")
    
    if not record.is_backed_up:
        raise HTTPException(
            status_code=400,
            detail=f"File '{record.filename}' has not been backed up yet"
        )
    
    print(f"\n[API] Restore requested for: {record.filename}")
    
    success = backup_service.restore_file(record.filename, file_id)
    
    if success:
        return JSONResponse(content={
            "success": True,
            "message": f"File '{record.filename}' restored successfully"
        })
    else:
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "Restore failed"}
        )


@router.get("/backup/status")
async def get_backup_status():
    """
    Get backup status for ALL files.
    """
    all_records = meta_service.get_all_records()
    
    status_list = []
    for record in all_records:
        priority = get_backup_priority(record.file_type, record.access_count)
        
        status_list.append({
            "file_id": record.file_id,
            "filename": record.filename,
            "file_type": record.file_type,
            "access_count": record.access_count,
            "is_backed_up": record.is_backed_up,
            "last_backup_time": record.last_backup_time,
            "backup_priority": priority
        })
    
    return JSONResponse(content={
        "total_files": len(status_list),
        "backup_enabled": backup_service.BACKUP_ENABLED,
        "files": status_list
    })


@router.get("/backup/list")
async def list_backup_vm_files():
    """
    List all files on the Backup VM.
    """
    files = backup_service.list_backup_files()
    
    return JSONResponse(content={
        "backup_enabled": backup_service.BACKUP_ENABLED,
        "total_files": len(files),
        "files": files
    })