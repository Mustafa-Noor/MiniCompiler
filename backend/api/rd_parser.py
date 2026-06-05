from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from compiler.integration.runner import CompilerRunner

router = APIRouter(tags=["RD Parser"])
runner = CompilerRunner()


class RDParserResponse(BaseModel):
    accepted: bool
    trace: List[str]


@router.post("/run/rd", response_model=RDParserResponse)
async def run_rd_parser() -> RDParserResponse:
    try:
        result = runner.run_rd_parser()
        return RDParserResponse(**result)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
