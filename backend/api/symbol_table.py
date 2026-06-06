from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from compiler.integration.runner import CompilerRunner
from compiler.integration.session import compilation_session

router = APIRouter(tags=["Symbol Table"])
runner = CompilerRunner()


class SymbolEntry(BaseModel):
    name: str
    kind: str = ""
    type: str = ""
    scope: str = ""
    line: int = 0
    column: int = 0


class SymbolTableResponse(BaseModel):
    entries: List[SymbolEntry]


@router.get("/symbol-table", response_model=SymbolTableResponse)
async def get_symbol_table() -> SymbolTableResponse:
    try:
        result = runner.get_symbol_table()
        return SymbolTableResponse(**result)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to build symbol table: {exc}",
        ) from exc


@router.get("/status")
async def get_status() -> Dict[str, Any]:
    s = compilation_session
    return {
        "filename": s.filename,
        "compilation_status": s.compilation_status,
        "token_count": len(s.tokens),
        "error_count": len(s.errors),
        "symbol_count": len(s.symbol_entries),
        "rd_accepted": s.rd_accepted,
        "ll1_accepted": s.ll1_accepted,
        "lr_accepted": s.lr_accepted,
        "token_statistics": s.token_statistics,
    }
