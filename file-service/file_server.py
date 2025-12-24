#! /usr/bin/env python3

import os
from typing import List

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
import aiofiles

app = FastAPI()
BASE_DIR = "files"  # Local directory to manage

@app.on_event("startup")
async def ensure_base_dir():
    os.makedirs(BASE_DIR, exist_ok=True)

@app.get("/files", response_model=List[str])
async def list_files():
    """List all files in the base directory."""
    return os.listdir(BASE_DIR)

@app.get("/files/{filename}")
async def download_file(filename: str):
    """Download a file by filename."""
    file_path = os.path.join(BASE_DIR, filename)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=file_path, filename=filename)

@app.post("/files/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a new file to the base directory."""
    destination = os.path.join(BASE_DIR, file.filename)
    
    # Schedule the background task
    app.background_tasks.add_task(process_uploaded_file, destination)
    return {"filename": file.filename}

@app.put("/files/{filename}/rename")
async def rename_file(filename: str, new_name: str):
    """Rename an existing file."""
    source = os.path.join(BASE_DIR, filename)
    target = os.path.join(BASE_DIR, new_name)
    if not os.path.isfile(source):
        raise HTTPException(status_code=404, detail="Source file not found")
    os.rename(source, target)
    return {"old_name": filename, "new_name": new_name}

@app.delete("/files/{filename}")
async def delete_file(filename: str):
    """Delete a file by filename."""
    file_path = os.path.join(BASE_DIR, filename)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    os.remove(file_path)
    return {"filename": filename, "deleted": True}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("file_server:app", host="0.0.0.0", port=8000, reload=True)
