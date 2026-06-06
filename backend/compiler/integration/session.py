"""Shared compilation session state across API requests."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class CompilationSession:
    source_path: Optional[Path] = None
    source_code: str = ""
    filename: str = ""

    tokens: List[Dict[str, Any]] = field(default_factory=list)
    token_statistics: Dict[str, int] = field(default_factory=dict)

    rd_accepted: Optional[bool] = None
    rd_trace: List[str] = field(default_factory=list)

    ll1_accepted: Optional[bool] = None
    ll1_trace: List[str] = field(default_factory=list)
    first_sets: Dict[str, List[str]] = field(default_factory=dict)
    follow_sets: Dict[str, List[str]] = field(default_factory=dict)
    parsing_table: Dict[str, str] = field(default_factory=dict)

    lr_accepted: Optional[bool] = None
    lr_trace: List[str] = field(default_factory=list)
    action_table: Dict[str, str] = field(default_factory=dict)
    goto_table: Dict[str, str] = field(default_factory=dict)

    symbol_entries: List[Dict[str, Any]] = field(default_factory=list)
    ast_tree: Dict[str, Any] = field(default_factory=dict)
    errors: List[Dict[str, Any]] = field(default_factory=list)

    compilation_status: str = "idle"

    def reset_results(self) -> None:
        self.tokens = []
        self.token_statistics = {}
        self.rd_accepted = None
        self.rd_trace = []
        self.ll1_accepted = None
        self.ll1_trace = []
        self.first_sets = {}
        self.follow_sets = {}
        self.parsing_table = {}
        self.lr_accepted = None
        self.lr_trace = []
        self.action_table = {}
        self.goto_table = {}
        self.symbol_entries = []
        self.ast_tree = {}
        self.errors = []
        self.compilation_status = "idle"


compilation_session = CompilationSession()
