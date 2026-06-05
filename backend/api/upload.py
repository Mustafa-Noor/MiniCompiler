from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from compiler.integration.session import compilation_session

router = APIRouter(tags=["Upload"])

UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


class UploadResponse(BaseModel):
    filename: str
    size: int
    message: str


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)) -> UploadResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    if not file.filename.lower().endswith((".pas", ".txt")):
        raise HTTPException(status_code=400, detail="Only .pas or .txt files are accepted")

    content = await file.read()
    dest = UPLOAD_DIR / file.filename
    dest.write_bytes(content)

    compilation_session.reset_results()
    compilation_session.source_path = dest
    compilation_session.filename = file.filename
    compilation_session.source_code = content.decode("utf-8", errors="replace")

    return UploadResponse(
        filename=file.filename,
        size=len(content),
        message="File uploaded successfully",
    )


@router.get("/source")
async def get_source() -> dict:
    return {
        "filename": compilation_session.filename,
        "source_code": compilation_session.source_code,
        "has_file": bool(compilation_session.source_path),
    }


@router.post("/source")
async def set_source(payload: dict) -> dict:
    code = payload.get("source_code", "")
    filename = payload.get("filename", "editor.pas")
    dest = UPLOAD_DIR / filename
    dest.write_text(code, encoding="utf-8")

    compilation_session.reset_results()
    compilation_session.source_path = dest
    compilation_session.filename = filename
    compilation_session.source_code = code

    return {"filename": filename, "size": len(code.encode("utf-8")), "message": "Source saved"}
