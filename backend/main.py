"""BrickCraft API Server – FastAPI backend."""
import os
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles

import converter

app = FastAPI(title="BrickCraft API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store for downloadable outputs (session_id → {ldr, xml})
_store: dict[str, dict] = {}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXT = {".schem", ".schematic", ".litematic"}


@app.post("/api/convert")
async def convert_file(file: UploadFile = File(...), scale: str = Form("compact")):
    if scale not in ("compact", "official"):
        scale = "compact"
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXT:
        raise HTTPException(400, f"Unsupported file type '{ext}'. Accepted: {', '.join(ALLOWED_EXT)}")

    data = await file.read()
    if len(data) == 0:
        raise HTTPException(400, "Empty file")
    if len(data) > MAX_FILE_SIZE:
        raise HTTPException(400, "File too large (max 10 MB)")

    try:
        result = converter.convert_and_optimize(file.filename, data, scale=scale)
    except ImportError as exc:
        raise HTTPException(500, str(exc))
    except Exception as exc:
        raise HTTPException(500, f"Conversion failed: {exc}")

    if "error" in result:
        raise HTTPException(400, result["error"])

    sid = result["session_id"]
    _store[sid] = {
        "ldr": result.pop("ldr_content"),
        "xml": result["bricklink_xml"],   # keep in response AND store
    }
    return result


@app.get("/api/download/{session_id}/ldr")
async def download_ldr(session_id: str):
    if session_id not in _store:
        raise HTTPException(404, "Session expired or not found")
    return Response(
        content=_store[session_id]["ldr"],
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="brickcraft_{session_id}.ldr"'},
    )


@app.get("/api/download/{session_id}/xml")
async def download_xml(session_id: str):
    if session_id not in _store:
        raise HTTPException(404, "Session expired or not found")
    return Response(
        content=_store[session_id]["xml"],
        media_type="application/xml",
        headers={"Content-Disposition": f'attachment; filename="brickcraft_{session_id}_bricklink.xml"'},
    )


# Serve the frontend (index.html sits one level up)
_parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app.mount("/", StaticFiles(directory=_parent, html=True), name="static")
