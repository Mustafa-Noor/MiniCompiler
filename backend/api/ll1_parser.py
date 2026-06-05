from typing import Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from compiler.integration.runner import CompilerRunner

router = APIRouter(tags=["LL1 Parser"])
runner = CompilerRunner()


class LL1ParserResponse(BaseModel):
    accepted: bool
    first_sets: Dict[str, List[str]]
    follow_sets: Dict[str, List[str]]
    parsing_table: Dict[str, str]
    trace: List[str]


@router.post("/run/ll1", response_model=LL1ParserResponse)
async def run_ll1_parser() -> LL1ParserResponse:
    try:
        result = runner.run_ll1_parser()
        return LL1ParserResponse(**result)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
