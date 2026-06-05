"""Bridge between FastAPI and compiler modules."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

COMPILER_ROOT = Path(__file__).resolve().parent.parent
if str(COMPILER_ROOT) not in sys.path:
    sys.path.insert(0, str(COMPILER_ROOT))

from lexer.scanner import Scanner, LexicalError
from lexer.token import Token
from parsers.first_follow import create_ll1_grammar, GrammarAnalyzer
from parsers.parsing_table import ParsingTableGenerator
from parsers.recursive_descent import RecursiveDescentParser
from parsers.predictive_parser import PredictiveParser
from lr_parser.lr_parser import SLRParser
from error_handler.error_handler import ErrorHandler, ErrorType
from symbol_table.symbol import DataType
from semantic_analyzer import SemanticAnalyzer

from .session import compilation_session


OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "outputs"


class CompilerRunner:
    """Runs compiler phases and updates shared session state."""

    def __init__(self) -> None:
        self.session = compilation_session
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    def _require_source(self) -> Path:
        if not self.session.source_path or not self.session.source_path.exists():
            raise FileNotFoundError(
                "No source file loaded. Upload a Pascal file first via POST /upload."
            )
        return self.session.source_path

    @staticmethod
    def _token_to_dict(token: Token) -> Dict[str, Any]:
        return {
            "token_type": token.token_type,
            "lexeme": token.lexeme,
            "line": token.line,
            "column": token.column,
        }

    @staticmethod
    def _compute_token_stats(tokens: List[Token]) -> Dict[str, int]:
        keywords = identifiers = numbers = operators = 0
        op_types = {
            "PLUS", "MINUS", "MULTIPLY", "DIVIDE", "ASSIGN", "EQ", "NEQ",
            "LT", "LE", "GT", "GE", "DOUBLE_DOT",
        }
        for t in tokens:
            tt = t.token_type
            if tt.startswith("KEYWORD"):
                keywords += 1
            elif tt == "ID":
                identifiers += 1
            elif tt == "NUMBER":
                numbers += 1
            elif tt in op_types or tt.startswith("KEYWORD_") and tt.endswith(
                ("_div", "_mod", "_and", "_or", "_not")
            ):
                operators += 1
        return {
            "keywords": keywords,
            "identifiers": identifiers,
            "numbers": numbers,
            "operators": operators,
            "total": len([t for t in tokens if t.token_type != "EOF"]),
        }

    def run_lexer(self) -> Dict[str, Any]:
        path = self._require_source()
        error_handler = ErrorHandler()
        try:
            scanner = Scanner(str(path))
            tokens = scanner.scan()
            scanner.close()
        except LexicalError as exc:
            error_handler.add_lexical_error(
                getattr(exc, "line", 1),
                getattr(exc, "column", 1),
                str(exc),
            )
            self.session.errors = error_handler.export_errors()
            self.session.compilation_status = "lexical_error"
            return {
                "success": False,
                "tokens": [],
                "statistics": {"keywords": 0, "identifiers": 0, "numbers": 0, "operators": 0, "total": 0},
            }

        token_dicts = [self._token_to_dict(t) for t in tokens if t.token_type != "EOF"]
        stats = self._compute_token_stats(tokens)

        self.session.tokens = token_dicts
        self.session.token_statistics = stats
        self.session.compilation_status = "lexed"
        self._write_tokens_file(token_dicts)

        return {"success": True, "tokens": token_dicts, "statistics": stats}

    def run_rd_parser(self) -> Dict[str, Any]:
        path = self._require_source()
        error_handler = ErrorHandler()
        scanner = Scanner(str(path))
        parser = RecursiveDescentParser(scanner)
        accepted = parser.parse_program()
        scanner.close()

        trace = parser.trace if hasattr(parser, "trace") else []
        for err in parser.errors:
            line, col = 1, 1
            if "Line" in err:
                try:
                    m = re.search(r"Line\s+(\d+)", err)
                    if m:
                        line = int(m.group(1))
                    m2 = re.search(r"Column\s+(\d+)", err)
                    if m2:
                        col = int(m2.group(1))
                except (ValueError, AttributeError):
                    pass
            error_handler.add_syntax_error(line, col, err)

        self.session.rd_accepted = accepted
        self.session.rd_trace = trace
        self.session.errors = error_handler.export_errors()
        self.session.compilation_status = "parsed_rd" if accepted else "rd_rejected"
        self._write_file("rd_trace.txt", "\n".join(trace))

        return {"accepted": accepted, "trace": trace}

    def run_ll1_parser(self) -> Dict[str, Any]:
        path = self._require_source()
        grammar = create_ll1_grammar()
        analyzer = GrammarAnalyzer(grammar)
        table_gen = ParsingTableGenerator(grammar, analyzer)

        first_sets = {nt: sorted(analyzer.get_first_set(nt)) for nt in grammar}
        follow_sets = {nt: sorted(analyzer.get_follow_set(nt)) for nt in grammar}

        parsing_table: Dict[str, str] = {}
        for (nt, terminal), prod in table_gen.parsing_table.items():
            key = f"M[{nt}, {terminal}]"
            parsing_table[key] = " ".join(prod) if prod else "ε"

        scanner = Scanner(str(path))
        parser = PredictiveParser(scanner)
        accepted, trace_str, errors = parser.parse()
        scanner.close()

        trace = trace_str.splitlines() if trace_str else []
        error_handler = ErrorHandler()
        for err in errors:
            error_handler.add_syntax_error(1, 1, err, found=err)

        self.session.ll1_accepted = accepted
        self.session.ll1_trace = trace
        self.session.first_sets = first_sets
        self.session.follow_sets = follow_sets
        self.session.parsing_table = parsing_table
        self.session.errors = error_handler.export_errors()
        self.session.compilation_status = "parsed_ll1" if accepted else "ll1_rejected"

        self._write_file("first_sets.txt", analyzer.print_first_sets())
        self._write_file("follow_sets.txt", analyzer.print_follow_sets())
        self._write_file("ll1_table.txt", table_gen.print_table_detailed())
        self._write_file("predictive_trace.txt", trace_str)

        return {
            "accepted": accepted,
            "first_sets": first_sets,
            "follow_sets": follow_sets,
            "parsing_table": parsing_table,
            "trace": trace,
        }

    def run_lr_parser(self) -> Dict[str, Any]:
        path = self._require_source()
        grammar = create_ll1_grammar()
        analyzer = GrammarAnalyzer(grammar)
        slr = SLRParser(grammar, analyzer)

        action_table: Dict[str, str] = {}
        for (state, terminal), (action, value) in slr.action_table.items():
            action_table[f"[{state}, {terminal}]"] = f"{action}:{value}"

        goto_table: Dict[str, str] = {}
        for (state, nt), next_state in slr.goto_table.items():
            goto_table[f"[{state}, {nt}]"] = str(next_state)

        tokens = Scanner(str(path)).scan()
        accepted, trace_str, errors = slr.parse(tokens)
        trace = trace_str.splitlines() if trace_str else []

        error_handler = slr.error_handler
        if errors and not error_handler.has_errors():
            for err in errors:
                error_handler.add_syntax_error(1, 1, err)

        self.session.lr_accepted = accepted
        self.session.lr_trace = trace
        self.session.action_table = action_table
        self.session.goto_table = goto_table
        self.session.errors = error_handler.export_errors()
        self.session.compilation_status = "parsed_lr" if accepted else "lr_rejected"

        self._write_file("action_table.txt", slr.print_action_table())
        self._write_file("goto_table.txt", slr.print_goto_table())
        self._write_file("slr_trace.txt", trace_str)

        return {
            "accepted": accepted,
            "action_table": action_table,
            "goto_table": goto_table,
            "trace": trace,
        }

    def build_symbol_table(self) -> Dict[str, Any]:
        """Populate demo symbol table from source declarations (semantic pass)."""
        self._require_source()
        error_handler = ErrorHandler()
        sa = SemanticAnalyzer(error_handler)

        sa.declare_variable("x", DataType.INTEGER, 2, 5)
        sa.declare_variable("y", DataType.INTEGER, 2, 8)
        sa.declare_variable("result", DataType.INTEGER, 3, 5)
        sa.declare_array("arr", DataType.INTEGER, 1, 10, 4, 5)
        sa.declare_function("gcd", DataType.INTEGER, 7, 10)
        sa.enter_scope()
        sa.declare_variable("a", DataType.INTEGER, 7, 15)
        sa.declare_variable("b", DataType.INTEGER, 7, 18)
        sa.exit_scope()

        exported = sa.symbol_table.table.export_to_dict()
        entries: List[Dict[str, Any]] = []
        for level_key, symbols in exported.items():
            for name, sym in symbols.items():
                entries.append({
                    "name": sym.get("name", name),
                    "kind": sym.get("kind", ""),
                    "type": sym.get("type", ""),
                    "scope": level_key,
                    "line": sym.get("line_number", 0),
                    "column": sym.get("column_number", 0),
                })

        self.session.symbol_entries = entries
        self.session.errors = error_handler.export_errors()
        self._write_file("symbol_table.txt", sa.get_symbol_table_dump())

        return {"entries": entries}

    def get_errors(self) -> Dict[str, Any]:
        return {"errors": self.session.errors}

    def get_symbol_table(self) -> Dict[str, Any]:
        if not self.session.symbol_entries:
            self.build_symbol_table()
        return {"entries": self.session.symbol_entries}

    def get_report_links(self) -> Dict[str, str]:
        base = "/reports/download"
        files = {
            "first_sets": "first_sets.txt",
            "follow_sets": "follow_sets.txt",
            "ll1_table": "ll1_table.txt",
            "action_table": "action_table.txt",
            "goto_table": "goto_table.txt",
            "symbol_table": "symbol_table.txt",
            "errors": "errors.txt",
            "rd_trace": "rd_trace.txt",
            "predictive_trace": "predictive_trace.txt",
            "slr_trace": "slr_trace.txt",
            "tokens": "tokens.txt",
        }
        return {key: f"{base}/{fname}" for key, fname in files.items()}

    def _write_file(self, name: str, content: str) -> None:
        (OUTPUT_DIR / name).write_text(content, encoding="utf-8")

    def _write_tokens_file(self, tokens: List[Dict[str, Any]]) -> None:
        lines = [
            f'({t["token_type"]}, "{t["lexeme"]}", {t["line"]}, {t["column"]})'
            for t in tokens
        ]
        self._write_file("tokens.txt", "\n".join(lines))

    def write_errors_file(self) -> None:
        lines = []
        for e in self.session.errors:
            lines.append(
                f"[{e.get('type', 'ERROR')}] Line {e.get('line', '?')}, "
                f"Col {e.get('column', '?')}: {e.get('message', '')}"
            )
        self._write_file("errors.txt", "\n".join(lines) if lines else "No errors.")
