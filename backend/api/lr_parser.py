from typing import Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from compiler.integration.runner import CompilerRunner

router = APIRouter(tags=["LR Parser"])
runner = CompilerRunner()


class LRParserResponse(BaseModel):
    accepted: bool
    action_table: Dict[str, str]
    goto_table: Dict[str, str]
    trace: List[str]


@router.post("/run/lr", response_model=LRParserResponse)
async def run_lr_parser() -> LRParserResponse:
    try:
        result = runner.run_lr_parser()
        return LRParserResponse(**result)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
