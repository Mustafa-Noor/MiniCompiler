from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from compiler.ast_builder import ASTParseError, build_ast
from compiler.integration.session import compilation_session

router = APIRouter(tags=["AST"])


class ASTResponse(BaseModel):
    accepted: bool
    ast: Dict[str, Any] | None = None
    errors: List[Dict[str, Any]] = []


@router.post("/run/ast", response_model=ASTResponse)
async def run_ast_builder() -> ASTResponse:
    if not compilation_session.source_path or not compilation_session.source_path.exists():
        raise HTTPException(
            status_code=400,
            detail="No source file loaded. Upload or save Pascal source first.",
        )

    try:
        ast = build_ast(compilation_session.source_path)
        return ASTResponse(accepted=True, ast=ast, errors=[])
    except ASTParseError as exc:
        return ASTResponse(accepted=False, ast=None, errors=[exc.to_dict()])
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to build AST: {exc}") from exc
