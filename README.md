# ☁️ Personal Cloud Storage System (SCP-based)

## Features
- File upload via web UI
- Automatic SCP transfer to Primary VM
- Simulated VM using localhost ports (22 & 2222)
- Smart backup logic (priority-based)
- Manual SCP backup demonstration

## Architecture
Browser → FastAPI → SCP → Primary VM → SCP → Backup VM

## Tech Used
- Python (FastAPI)
- SSH & SCP
- Linux
- JavaScript frontend

## How it Works
- Upload uses SCP to store files in primary VM
- Backup uses SCP between simulated VMs
- SSH ports simulate multiple machines

## Run Project
```bash
uvicorn backend.main:app --reload
