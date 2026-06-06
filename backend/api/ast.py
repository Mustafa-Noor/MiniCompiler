from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from compiler.integration.runner import CompilerRunner

router = APIRouter(tags=["AST"])
runner = CompilerRunner()


class ASTResponse(BaseModel):
    success: bool
    ast: Dict[str, Any]
    node_count: int = 0
    root: str = ""


@router.post("/run/ast", response_model=ASTResponse)
async def run_ast() -> ASTResponse:
    try:
        result = runner.run_ast()
        return ASTResponse(**result)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to build AST: {exc}") from exc


@router.get("/ast", response_model=ASTResponse)
async def get_ast() -> ASTResponse:
    try:
        result = runner.get_ast()
        return ASTResponse(**result)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to load AST: {exc}") from exc
