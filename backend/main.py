# """
# main.py
# -------
# This is the entry point of our FastAPI backend application.
# Think of it as the "main door" to your backend.

# When you run this file, it starts a web server that:
#   - Listens on http://localhost:8000
#   - Accepts file uploads
#   - Serves files for download
#   - Manages backups

# To run this app:
#     uvicorn backend.main:app --reload --port 8000

# Then visit:
#     http://localhost:8000        → Welcome message
#     http://localhost:8000/docs  → Interactive API documentation (try it in browser!)
# """

# import os
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import JSONResponse

# from backend.routes import files as files_router
# from backend.routes import backup as backup_router

# # ============================================================
# # Create the FastAPI application
# # ============================================================

# app = FastAPI(
#     title="Personal Cloud Storage System",
#     description="""
#     A Google Drive-like personal cloud storage system.
    
#     Features:
#     - File upload and download
#     - Automatic file type classification (image, code, document, etc.)
#     - Metadata tracking (access count, upload time)
#     - VM-based storage with SCP backup
#     - Intelligent backup scheduling based on file usage
#     - File restore from backup VM
    
#     Built with FastAPI + Python + Linux VMs + SCP
#     """,
#     version="1.0.0"
# )

# # ============================================================
# # CORS Middleware
# # ============================================================
# # CORS = Cross-Origin Resource Sharing
# # This allows our HTML frontend (running on a different port)
# # to communicate with this backend.
# # Without this, the browser would BLOCK frontend → backend requests.

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],        # Allow all origins (for development)
#     allow_credentials=True,
#     allow_methods=["*"],        # Allow GET, POST, DELETE, etc.
#     allow_headers=["*"],        # Allow all headers
# )

# # ============================================================
# # Register Routes (API Endpoints)
# # ============================================================
# # We split our endpoints into separate files (routes/) to keep
# # things organized. Here we "include" them into the main app.

# app.include_router(
#     files_router.router,
#     tags=["Files"]  # Groups them under "Files" in the docs
# )

# app.include_router(
#     backup_router.router,
#     tags=["Backup & Restore"]
# )

# # ============================================================
# # Serve the Frontend
# # ============================================================
# # This mounts our frontend folder so the HTML/JS files are
# # accessible at http://localhost:8000/frontend/

# frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
# if os.path.exists(frontend_path):
#     app.mount("/app", StaticFiles(directory=frontend_path, html=True), name="frontend")


# # ============================================================
# # Root Endpoint
# # ============================================================

# @app.get("/")
# async def root():
#     """
#     Welcome endpoint — confirms the backend is running.
#     Visit http://localhost:8000 in your browser.
#     """
#     return JSONResponse(content={
#         "message": "☁️ Personal Cloud Storage System is running!",
#         "version": "1.0.0",
#         "endpoints": {
#             "docs": "http://localhost:8000/docs",
#             "upload": "POST http://localhost:8000/upload",
#             "list_files": "GET http://localhost:8000/files",
#             "download": "GET http://localhost:8000/files/{file_id}",
#             "backup": "POST http://localhost:8000/backup/{file_id}",
#             "restore": "POST http://localhost:8000/restore/{file_id}",
#             "backup_status": "GET http://localhost:8000/backup/status",
#             "frontend": "http://localhost:8000/app"
#         }
#     })


# @app.get("/health")
# async def health_check():
#     """Health check endpoint — confirms server is alive."""
#     return JSONResponse(content={
#         "status": "healthy",
#         "service": "cloud-storage-backend"
#     })


# # ============================================================
# # Run the server (when running directly with python main.py)
# # ============================================================

# if __name__ == "__main__":
#     import uvicorn
    
#     print("=" * 50)
#     print("☁️  Starting Personal Cloud Storage System")
#     print("=" * 50)
#     print("→ API:      http://localhost:8000")
#     print("→ Docs:     http://localhost:8000/docs")
#     print("→ Frontend: http://localhost:8000/app")
#     print("=" * 50)
    
#     uvicorn.run(
#         "backend.main:app",
#         host="0.0.0.0",
#         port=8000,
#         reload=True  # Auto-restart when you save code changes
#     )
"""
main.py
-------
This is the entry point of our FastAPI backend application.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from backend.routes import files as files_router
from backend.routes import backup as backup_router

# Create FastAPI application
app = FastAPI(
    title="Personal Cloud Storage System",
    description="A Google Drive-like personal cloud storage system with smart backup",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routes
# Files routes (these have their own prefixes internally)
app.include_router(files_router.router, tags=["Files"])

# Backup routes - mount at root level (routes already have /backup in their paths)
app.include_router(backup_router.router, tags=["Backup & Restore"])

# Serve Frontend
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/app", StaticFiles(directory=frontend_path, html=True), name="frontend")


@app.get("/")
async def root():
    return JSONResponse(content={
        "message": "☁️ Personal Cloud Storage System is running!",
        "version": "1.0.0",
        "endpoints": {
            "docs": "http://localhost:8000/docs",
            "upload": "POST http://localhost:8000/upload",
            "list_files": "GET http://localhost:8000/files",
            "backup_single": "POST http://localhost:8000/backup/{file_id}",
            "backup_all": "POST http://localhost:8000/backup/all",
            "frontend": "http://localhost:8000/app"
        }
    })


@app.get("/health")
async def health_check():
    return JSONResponse(content={"status": "healthy"})


if __name__ == "__main__":
    import uvicorn
    
    print("=" * 50)
    print("☁️  Starting Personal Cloud Storage System")
    print("=" * 50)
    print("→ API:      http://localhost:8000")
    print("→ Docs:     http://localhost:8000/docs")
    print("→ Frontend: http://localhost:8000/app")
    print("=" * 50)
    
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )