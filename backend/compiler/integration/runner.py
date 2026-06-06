"""Bridge between FastAPI and compiler modules."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

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
from ast_builder import build_ast_from_file, ast_to_json

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

    @staticmethod
    def _seed_builtins(sa: SemanticAnalyzer) -> None:
        """Declare standard I/O procedures supplied by the runtime."""
        sa.declare_procedure("read", 0, 0)
        sa.declare_procedure("write", 0, 0)

    @staticmethod
    def _symbol_entries_from_analyzer(sa: SemanticAnalyzer) -> List[Dict[str, Any]]:
        exported = sa.symbol_table.table.export_to_dict()
        entries: List[Dict[str, Any]] = []
        for level_key, symbols in exported.items():
            level_num = int(str(level_key).replace("level_", "") or 0)
            scope_label = "Global" if level_num == 0 else f"Scope {level_num}"
            for name, sym in symbols.items():
                entries.append({
                    "name": str(sym.get("name", name)),
                    "kind": str(sym.get("kind", "")),
                    "type": str(sym.get("type", sym.get("data_type", ""))),
                    "scope": scope_label,
                    "line": int(sym.get("line_number", 0) or 0),
                    "column": int(sym.get("column_number", 0) or 0),
                })
        return entries

    def _merge_errors(self, new_errors: List[Dict[str, Any]], replace: bool = False) -> None:
        if replace:
            self.session.errors = list(new_errors)
            return
        seen = {
            (e.get("type"), e.get("line"), e.get("column"), e.get("message"))
            for e in self.session.errors
        }
        for err in new_errors:
            key = (err.get("type"), err.get("line"), err.get("column"), err.get("message"))
            if key not in seen:
                self.session.errors.append(err)
                seen.add(key)

    def _append_syntax_errors_from_strings(
        self, error_handler: ErrorHandler, messages: List[str]
    ) -> None:
        for err in messages:
            line, col = 1, 1
            m = re.search(r"Line\s+(\d+)", err)
            if m:
                line = int(m.group(1))
            m2 = re.search(r"Column\s+(\d+)", err)
            if m2:
                col = int(m2.group(1))
            error_handler.add_syntax_error(line, col, err)

    def _finalize_errors(self, error_handler: ErrorHandler, merge: bool = True) -> None:
        exported = error_handler.export_errors()
        if merge:
            self._merge_errors(exported)
        else:
            self.session.errors = exported
        self.write_errors_file()

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
            self._finalize_errors(error_handler, merge=False)
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
        sa = SemanticAnalyzer(error_handler)
        self._seed_builtins(sa)

        scanner = Scanner(str(path))
        parser = RecursiveDescentParser(scanner, semantic=sa)
        accepted = parser.parse_program()
        scanner.close()

        trace = parser.trace if hasattr(parser, "trace") else []
        self._append_syntax_errors_from_strings(error_handler, parser.errors)

        entries = self._symbol_entries_from_analyzer(sa)
        self.session.symbol_entries = entries
        self._finalize_errors(error_handler, merge=True)
        self._write_file("symbol_table.txt", sa.get_symbol_table_dump())

        self.session.rd_accepted = accepted
        self.session.rd_trace = trace
        self.session.compilation_status = "parsed_rd" if accepted else "rd_rejected"
        self._write_file("rd_trace.txt", "\n".join(trace))

        return {"accepted": accepted, "trace": trace}

    def run_ll1_parser(self, merge_errors: bool = True) -> Dict[str, Any]:
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
        accepted, trace_str, parse_errors = parser.parse()
        scanner.close()

        trace = trace_str.splitlines() if trace_str else []
        error_handler = ErrorHandler()
        for err in parse_errors:
            if isinstance(err, dict):
                error_handler.add_syntax_error(
                    int(err.get("line", 1)),
                    int(err.get("column", 1)),
                    str(err.get("message", "Syntax error")),
                    found=str(err.get("lexeme", "")),
                )
            else:
                error_handler.add_syntax_error(1, 1, str(err))

        self._finalize_errors(error_handler, merge=merge_errors)
        self.session.ll1_trace = trace
        self.session.first_sets = first_sets
        self.session.follow_sets = follow_sets
        self.session.parsing_table = parsing_table
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

    def run_lr_parser(self, merge_errors: bool = True) -> Dict[str, Any]:
        path = self._require_source()
        grammar = create_ll1_grammar()
        analyzer = GrammarAnalyzer(grammar)
        slr = SLRParser(grammar, analyzer)

        action_table = slr.export_action_table()
        goto_table = slr.export_goto_table()

        tokens = Scanner(str(path)).scan()
        try:
            accepted, trace_str, errors = slr.parse(tokens)
        except Exception as exc:
            error_handler = ErrorHandler()
            error_handler.add_syntax_error(1, 1, f"LR parser internal error: {exc}")
            self._finalize_errors(error_handler, merge=merge_errors)
            self.session.lr_accepted = False
            self.session.lr_trace = [f"LR parser aborted: {exc}"]
            self.session.compilation_status = "lr_rejected"
            return {
                "accepted": False,
                "action_table": action_table,
                "goto_table": goto_table,
                "trace": self.session.lr_trace,
            }
        trace = trace_str.splitlines() if trace_str else []

        if slr.error_handler.has_errors():
            self._finalize_errors(slr.error_handler, merge=merge_errors)
        elif errors:
            error_handler = ErrorHandler()
            for err in errors:
                error_handler.add_syntax_error(1, 1, str(err))
            self._finalize_errors(error_handler, merge=merge_errors)

        self.session.lr_accepted = accepted
        self.session.lr_trace = trace
        self.session.action_table = action_table
        self.session.goto_table = goto_table
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
        """Build symbol table by running the RD parser with semantic analysis."""
        if self.session.symbol_entries:
            return {"entries": self.session.symbol_entries}

        result = self.run_rd_parser()
        if not self.session.symbol_entries:
            path = self._require_source()
            error_handler = ErrorHandler()
            sa = SemanticAnalyzer(error_handler)
            self._seed_builtins(sa)
            scanner = Scanner(str(path))
            parser = RecursiveDescentParser(scanner, semantic=sa)
            parser.parse_program()
            scanner.close()
            entries = self._symbol_entries_from_analyzer(sa)
            self.session.symbol_entries = entries
            self._merge_errors(error_handler.export_errors())
            self._write_file("symbol_table.txt", sa.get_symbol_table_dump())

        return {"entries": self.session.symbol_entries}

    def run_all(self) -> Dict[str, Any]:
        """Run lexer, all parsers, and build symbol table in one pipeline."""
        self.session.reset_results()
        results: Dict[str, Any] = {}

        lexer_result = self.run_lexer()
        results["lexer"] = lexer_result

        if lexer_result.get("success"):
            results["rd"] = self.run_rd_parser()
            base_errors = list(self.session.errors)

            results["ll1"] = self.run_ll1_parser(merge_errors=False)
            ll1_errors = self.session.errors[:10]
            self.session.errors = base_errors + ll1_errors

            results["lr"] = self.run_lr_parser(merge_errors=False)
            lr_errors = self.session.errors[:10]
            self.session.errors = base_errors + ll1_errors + lr_errors
            self.write_errors_file()
            try:
                results["ast"] = self.run_ast()
            except Exception as exc:
                results["ast"] = {
                    "success": False,
                    "ast": {},
                    "node_count": 0,
                    "root": "",
                    "error": str(exc),
                }
        else:
            results["rd"] = {"accepted": False, "trace": [], "skipped": True}
            results["ll1"] = {"accepted": False, "trace": [], "skipped": True}
            results["lr"] = {"accepted": False, "trace": [], "skipped": True}
            results["ast"] = {"success": False, "ast": {}, "node_count": 0, "root": "", "skipped": True}

        results["symbol_table"] = self.get_symbol_table()
        results["errors"] = self.get_errors()
        results["status"] = self.get_status()
        self.write_errors_file()
        return results

    def get_errors(self) -> Dict[str, Any]:
        return {"errors": self.session.errors, "summary": self._error_summary()}

    def _error_summary(self) -> Dict[str, Any]:
        counts: Dict[str, int] = {}
        for err in self.session.errors:
            err_type = str(err.get("type", "UNKNOWN"))
            counts[err_type] = counts.get(err_type, 0) + 1
        return {
            "total": len(self.session.errors),
            "by_type": counts,
        }

    def get_symbol_table(self) -> Dict[str, Any]:
        if not self.session.symbol_entries:
            self.build_symbol_table()
        return {"entries": self.session.symbol_entries}

    def _count_ast_nodes(self, node: Dict[str, Any]) -> int:
        return 1 + sum(self._count_ast_nodes(child) for child in node.get("children", []))

    def _format_ast_tree(self, node: Dict[str, Any], indent: str = "") -> str:
        label = str(node.get("type", "Node"))
        if node.get("value") is not None:
            label += f": {node['value']}"
        lines = [indent + label]
        for child in node.get("children", []):
            lines.append(self._format_ast_tree(child, indent + "  "))
        return "\n".join(lines)

    def run_ast(self) -> Dict[str, Any]:
        path = self._require_source()
        ast = build_ast_from_file(str(path))
        self.session.ast_tree = ast
        self.session.compilation_status = "ast_generated"
        self._write_file("ast.json", ast_to_json(ast))
        self._write_file("ast_tree.txt", self._format_ast_tree(ast))
        return {
            "success": True,
            "ast": ast,
            "node_count": self._count_ast_nodes(ast),
            "root": ast.get("type", ""),
        }

    def get_ast(self) -> Dict[str, Any]:
        if not self.session.ast_tree:
            return self.run_ast()
        ast = self.session.ast_tree
        return {
            "success": True,
            "ast": ast,
            "node_count": self._count_ast_nodes(ast),
            "root": ast.get("type", ""),
        }

    def get_status(self) -> Dict[str, Any]:
        return {
            "compilation_status": self.session.compilation_status,
            "token_count": self.session.token_statistics.get("total", len(self.session.tokens)),
            "error_count": len(self.session.errors),
            "symbol_count": len(self.session.symbol_entries),
            "ast_node_count": self._count_ast_nodes(self.session.ast_tree) if self.session.ast_tree else 0,
            "ast_root": self.session.ast_tree.get("type", "") if self.session.ast_tree else "",
            "token_statistics": self.session.token_statistics,
            "rd_accepted": self.session.rd_accepted,
            "ll1_accepted": self.session.ll1_accepted,
            "lr_accepted": self.session.lr_accepted,
        }

    def get_report_links(self) -> Dict[str, str]:
        base = "/reports/download"
        files = {
            "first_sets": "first_sets.txt",
            "follow_sets": "follow_sets.txt",
            "ll1_table": "ll1_table.txt",
            "action_table": "action_table.txt",
            "goto_table": "goto_table.txt",
            "symbol_table": "symbol_table.txt",
            "ast_json": "ast.json",
            "ast_tree": "ast_tree.txt",
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
        summary = self._error_summary()
        lines.append("COMPILATION ERROR SUMMARY")
        lines.append("=" * 60)
        lines.append(f"Total errors: {summary['total']}")
        for err_type, count in sorted(summary["by_type"].items()):
            lines.append(f"  {err_type}: {count}")
        lines.append("")
        lines.append("DETAILED ERRORS")
        lines.append("=" * 60)
        if not self.session.errors:
            lines.append("No errors.")
        else:
            for e in self.session.errors:
                lines.append(
                    f"[{e.get('type', 'ERROR')}] Line {e.get('line', '?')}, "
                    f"Col {e.get('column', '?')}: {e.get('message', '')}"
                )
        self._write_file("errors.txt", "\n".join(lines))
