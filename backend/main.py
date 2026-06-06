"""
Mini Pascal Compiler Studio — FastAPI Backend
"""

import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import (
    lexer_router,
    rd_router,
    ll1_router,
    lr_router,
    symbol_router,
    ast_router,
    reports_router,
    upload_router,
    pipeline_router,
)

app = FastAPI(
    title="Mini Pascal Compiler Studio API",
    description="REST API for the Mini Pascal Compiler (Lexer, RD, LL(1), SLR)",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)
app.include_router(lexer_router)
app.include_router(rd_router)
app.include_router(ll1_router)
app.include_router(lr_router)
app.include_router(symbol_router)
app.include_router(ast_router)
app.include_router(reports_router)
app.include_router(pipeline_router)


@app.get("/")
async def root() -> dict:
    return {
        "name": "Mini Pascal Compiler Studio API",
        "version": "1.0.0",
        "course": "CS-471L Compiler Construction Lab",
        "endpoints": {
            "upload": "POST /upload",
            "lexer": "POST /run/lexer",
            "rd": "POST /run/rd",
            "ll1": "POST /run/ll1",
            "lr": "POST /run/lr",
            "run_all": "POST /run/all",
            "symbol_table": "GET /symbol-table",
            "ast": "POST /run/ast, GET /ast",
            "errors": "GET /errors",
            "reports": "GET /reports",
            "status": "GET /status",
        },
    }


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
