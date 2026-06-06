from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from compiler.integration.runner import CompilerRunner
from compiler.integration.session import compilation_session

router = APIRouter(tags=["Reports"])
runner = CompilerRunner()

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "outputs"

ALLOWED_FILES = {
    "first_sets.txt",
    "follow_sets.txt",
    "ll1_table.txt",
    "action_table.txt",
    "goto_table.txt",
    "symbol_table.txt",
    "ast.json",
    "ast_tree.txt",
    "errors.txt",
    "rd_trace.txt",
    "predictive_trace.txt",
    "slr_trace.txt",
    "tokens.txt",
}


@router.get("/errors")
async def get_errors() -> dict:
    runner.write_errors_file()
    return runner.get_errors()


@router.get("/reports")
async def get_reports() -> dict:
    links = runner.get_report_links()
    return {
        "reports": links,
        "labels": {
            "first_sets": "FIRST Sets",
            "follow_sets": "FOLLOW Sets",
            "ll1_table": "LL(1) Table",
            "action_table": "ACTION Table",
            "goto_table": "GOTO Table",
            "symbol_table": "Symbol Table",
            "ast_json": "AST JSON",
            "ast_tree": "AST Tree",
            "errors": "Errors",
            "rd_trace": "RD Parser Trace",
            "predictive_trace": "LL(1) Trace",
            "slr_trace": "SLR Trace",
            "tokens": "Token Stream",
        },
        "status": compilation_session.compilation_status,
    }


@router.get("/reports/download/{filename}")
async def download_report(filename: str) -> FileResponse:
    if filename not in ALLOWED_FILES:
        raise HTTPException(status_code=404, detail="Report not found")

    path = OUTPUT_DIR / filename
    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Report '{filename}' not generated yet. Run the corresponding compiler phase first.",
        )

    return FileResponse(
        path=path,
        filename=filename,
        media_type="text/plain",
    )
