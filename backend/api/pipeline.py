from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from compiler.integration.runner import CompilerRunner

router = APIRouter(tags=["Pipeline"])
runner = CompilerRunner()


class RunAllResponse(BaseModel):
    lexer: Dict[str, Any]
    rd: Dict[str, Any]
    ll1: Dict[str, Any]
    lr: Dict[str, Any]
    symbol_table: Dict[str, Any]
    errors: Dict[str, Any]
    status: Dict[str, Any]


@router.post("/run/all", response_model=RunAllResponse)
async def run_all_phases() -> RunAllResponse:
    try:
        result = runner.run_all()
        return RunAllResponse(**result)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
