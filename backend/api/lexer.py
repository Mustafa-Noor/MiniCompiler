from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List

from compiler.integration.runner import CompilerRunner

router = APIRouter(tags=["Lexer"])
runner = CompilerRunner()


class TokenItem(BaseModel):
    token_type: str
    lexeme: str
    line: int
    column: int


class TokenStatistics(BaseModel):
    keywords: int = 0
    identifiers: int = 0
    numbers: int = 0
    operators: int = 0
    total: int = 0


class LexerResponse(BaseModel):
    success: bool
    tokens: List[TokenItem]
    statistics: TokenStatistics


@router.post("/run/lexer", response_model=LexerResponse)
async def run_lexer() -> LexerResponse:
    try:
        result = runner.run_lexer()
        return LexerResponse(**result)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
