"""Abstract syntax tree builder for the Mini Pascal subset."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from .lexer.scanner import Scanner
from .lexer.token import Token, TokenType


@dataclass
class ASTNode:
    kind: str
    label: str
    value: str = ""
    line: int = 0
    column: int = 0
    meta: Dict[str, Any] = field(default_factory=dict)
    children: List["ASTNode"] = field(default_factory=list)

    def add(self, node: Optional["ASTNode"]) -> Optional["ASTNode"]:
        if node is not None:
            self.children.append(node)
        return node

    def to_dict(self) -> Dict[str, Any]:
        return {
            "kind": self.kind,
            "label": self.label,
            "value": self.value,
            "line": self.line,
            "column": self.column,
            "meta": self.meta,
            "children": [child.to_dict() for child in self.children],
        }


class ASTParseError(Exception):
    """Raised when the AST builder cannot parse the current source."""

    def __init__(self, message: str, token: Token):
        self.message = message
        self.token = token
        super().__init__(message)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Syntax Error",
            "line": self.token.line,
            "column": self.token.column,
            "message": self.message,
            "lexeme": self.token.lexeme,
        }


class ASTBuilder:
    """Small recursive parser that emits an AST instead of a parse trace."""

    def __init__(self, source_file: str | Path):
        scanner = Scanner(str(source_file))
        try:
            self.tokens = scanner.scan()
        finally:
            scanner.close()
        self.pos = 0

    @property
    def current(self) -> Token:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]

    def at(self, token_type: str) -> bool:
        return self.current.token_type == token_type

    def advance(self) -> Token:
        token = self.current
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return token

    def match(self, *token_types: str) -> Optional[Token]:
        if self.current.token_type in token_types:
            return self.advance()
        return None

    def expect(self, token_type: str, label: str = "") -> Token:
        if not self.at(token_type):
            expected = label or token_type
            raise ASTParseError(
                f"Expected {expected}, found {self.current.lexeme} ({self.current.token_type})",
                self.current,
            )
        return self.advance()

    def build(self) -> ASTNode:
        tree = self.parse_program()
        self.expect(TokenType.EOF, "end of file")
        return tree

    def parse_program(self) -> ASTNode:
        start = self.expect("KEYWORD_PROGRAM", "program")
        name = self.expect("ID", "program name")
        root = ASTNode("program", "Program", name.lexeme, start.line, start.column)

        if self.match("LPAREN"):
            params = ASTNode("io_list", "Program Parameters")
            if not self.at("RPAREN"):
                params.children = self.parse_identifier_nodes()
            self.expect("RPAREN", ")")
            root.add(params)

        self.expect("SEMICOLON", ";")
        root.add(self.parse_declarations())
        root.add(self.parse_subprograms())
        root.add(self.parse_compound_statement("Main Block"))
        self.expect("DOT", ".")
        return root

    def parse_identifier_nodes(self) -> List[ASTNode]:
        nodes = []
        token = self.expect("ID", "identifier")
        nodes.append(ASTNode("identifier", "Identifier", token.lexeme, token.line, token.column))
        while self.match("COMMA"):
            token = self.expect("ID", "identifier")
            nodes.append(ASTNode("identifier", "Identifier", token.lexeme, token.line, token.column))
        return nodes

    def parse_declarations(self) -> ASTNode:
        decls = ASTNode("declarations", "Declarations")
        if not self.match("KEYWORD_VAR"):
            return decls

        while self.at("ID"):
            ids = self.parse_identifier_nodes()
            self.expect("COLON", ":")
            type_node = self.parse_type_spec()
            self.expect("SEMICOLON", ";")
            node = ASTNode(
                "var_decl",
                "VarDecl",
                ", ".join(identifier.value for identifier in ids),
                ids[0].line if ids else 0,
                ids[0].column if ids else 0,
                {"type": type_node.value},
            )
            node.children = ids + [type_node]
            decls.add(node)
        return decls

    def parse_type_spec(self) -> ASTNode:
        token = self.current
        if self.match("KEYWORD_INTEGER"):
            return ASTNode("type", "Type", "integer", token.line, token.column)
        if self.match("KEYWORD_REAL"):
            return ASTNode("type", "Type", "real", token.line, token.column)
        if self.match("KEYWORD_ARRAY"):
            node = ASTNode("type", "ArrayType", "", token.line, token.column)
            self.expect("LBRACKET", "[")
            lower = self.expect("NUMBER", "array lower bound")
            self.expect("DOUBLE_DOT", "..")
            upper = self.expect("NUMBER", "array upper bound")
            self.expect("RBRACKET", "]")
            self.expect("KEYWORD_OF", "of")
            element_type = self.parse_type_spec()
            node.value = f"array[{lower.lexeme}..{upper.lexeme}] of {element_type.value}"
            node.meta = {"lower": lower.lexeme, "upper": upper.lexeme}
            node.add(element_type)
            return node
        raise ASTParseError("Expected type specification", self.current)

    def parse_subprograms(self) -> ASTNode:
        node = ASTNode("subprograms", "Subprograms")
        while self.current.token_type in ("KEYWORD_FUNCTION", "KEYWORD_PROCEDURE"):
            node.add(self.parse_subprogram())
            self.expect("SEMICOLON", ";")
        return node

    def parse_subprogram(self) -> ASTNode:
        if self.match("KEYWORD_FUNCTION"):
            name = self.expect("ID", "function name")
            node = ASTNode("function", "Function", name.lexeme, name.line, name.column)
            node.add(self.parse_arguments())
            self.expect("COLON", ":")
            node.add(self.parse_type_spec())
            self.expect("SEMICOLON", ";")
            node.add(self.parse_declarations())
            node.add(self.parse_compound_statement("Function Body"))
            return node

        token = self.expect("KEYWORD_PROCEDURE", "procedure")
        name = self.expect("ID", "procedure name")
        node = ASTNode("procedure", "Procedure", name.lexeme, token.line, token.column)
        node.add(self.parse_arguments())
        self.expect("SEMICOLON", ";")
        node.add(self.parse_declarations())
        node.add(self.parse_compound_statement("Procedure Body"))
        return node

    def parse_arguments(self) -> ASTNode:
        node = ASTNode("parameters", "Parameters")
        if not self.match("LPAREN"):
            return node
        if not self.at("RPAREN"):
            while True:
                ids = self.parse_identifier_nodes()
                self.expect("COLON", ":")
                type_node = self.parse_type_spec()
                group = ASTNode(
                    "parameter_group",
                    "ParamGroup",
                    ", ".join(identifier.value for identifier in ids),
                    ids[0].line if ids else 0,
                    ids[0].column if ids else 0,
                    {"type": type_node.value},
                )
                group.children = ids + [type_node]
                node.add(group)
                if not self.match("SEMICOLON"):
                    break
        self.expect("RPAREN", ")")
        return node

    def parse_compound_statement(self, label: str = "Block") -> ASTNode:
        start = self.expect("KEYWORD_BEGIN", "begin")
        node = ASTNode("block", label, "", start.line, start.column)
        while not self.at("KEYWORD_END") and not self.at(TokenType.EOF):
            if self.at("SEMICOLON"):
                self.advance()
                continue
            node.add(self.parse_statement())
            self.match("SEMICOLON")
        self.expect("KEYWORD_END", "end")
        return node

    def parse_statement(self) -> ASTNode:
        if self.at("KEYWORD_BEGIN"):
            return self.parse_compound_statement()
        if self.match("KEYWORD_IF"):
            token = self.tokens[self.pos - 1]
            node = ASTNode("if", "If", "", token.line, token.column)
            node.add(self.parse_expression("condition"))
            self.expect("KEYWORD_THEN", "then")
            node.add(self.parse_statement())
            if self.match("KEYWORD_ELSE"):
                node.add(self.parse_statement())
            return node
        if self.match("KEYWORD_WHILE"):
            token = self.tokens[self.pos - 1]
            node = ASTNode("while", "While", "", token.line, token.column)
            node.add(self.parse_expression("condition"))
            self.expect("KEYWORD_DO", "do")
            node.add(self.parse_statement())
            return node
        if self.at("ID"):
            return self.parse_id_statement()
        raise ASTParseError("Expected statement", self.current)

    def parse_id_statement(self) -> ASTNode:
        name = self.expect("ID", "identifier")
        target = ASTNode("identifier", "Identifier", name.lexeme, name.line, name.column)

        if self.match("LBRACKET"):
            target = ASTNode("array_access", "ArrayAccess", name.lexeme, name.line, name.column)
            target.add(self.parse_expression("index"))
            self.expect("RBRACKET", "]")

        if self.match("ASSIGN"):
            node = ASTNode("assignment", "Assignment", name.lexeme, name.line, name.column)
            node.add(target)
            node.add(self.parse_expression("expr"))
            return node

        if self.match("LPAREN"):
            node = ASTNode("call", "ProcedureCall", name.lexeme, name.line, name.column)
            node.children = self.parse_expression_list()
            self.expect("RPAREN", ")")
            return node

        return ASTNode("call", "ProcedureCall", name.lexeme, name.line, name.column)

    def parse_expression_list(self) -> List[ASTNode]:
        nodes = []
        if self.at("RPAREN"):
            return nodes
        nodes.append(self.parse_expression("arg"))
        while self.match("COMMA"):
            nodes.append(self.parse_expression("arg"))
        return nodes

    def parse_expression(self, label: str = "Expression") -> ASTNode:
        left = self.parse_simple_expression()
        if self.current.token_type in ("EQ", "NEQ", "LT", "LE", "GT", "GE"):
            op = self.advance()
            node = ASTNode("binary_op", "BinaryOp", op.lexeme, op.line, op.column, {"role": label})
            node.add(left)
            node.add(self.parse_simple_expression())
            return node
        if label != "Expression":
            left.meta = {**left.meta, "role": label}
        return left

    def parse_simple_expression(self) -> ASTNode:
        if self.current.token_type in ("PLUS", "MINUS"):
            op = self.advance()
            node = ASTNode("unary_op", "UnaryOp", op.lexeme, op.line, op.column)
            node.add(self.parse_term())
            left = node
        else:
            left = self.parse_term()

        while self.current.token_type in ("PLUS", "MINUS", "KEYWORD_OR"):
            op = self.advance()
            node = ASTNode("binary_op", "BinaryOp", op.lexeme, op.line, op.column)
            node.add(left)
            node.add(self.parse_term())
            left = node
        return left

    def parse_term(self) -> ASTNode:
        left = self.parse_factor()
        while self.current.token_type in (
            "MULTIPLY",
            "DIVIDE",
            "KEYWORD_DIV",
            "KEYWORD_MOD",
            "KEYWORD_AND",
        ):
            op = self.advance()
            node = ASTNode("binary_op", "BinaryOp", op.lexeme, op.line, op.column)
            node.add(left)
            node.add(self.parse_factor())
            left = node
        return left

    def parse_factor(self) -> ASTNode:
        token = self.current
        if self.match("NUMBER"):
            return ASTNode("constant", "Constant", token.lexeme, token.line, token.column, {"type": "number"})
        if self.match("ID"):
            if self.match("LPAREN"):
                node = ASTNode("call", "FunctionCall", token.lexeme, token.line, token.column)
                node.children = self.parse_expression_list()
                self.expect("RPAREN", ")")
                return node
            if self.match("LBRACKET"):
                node = ASTNode("array_access", "ArrayAccess", token.lexeme, token.line, token.column)
                node.add(self.parse_expression("index"))
                self.expect("RBRACKET", "]")
                return node
            return ASTNode("identifier", "Identifier", token.lexeme, token.line, token.column)
        if self.match("LPAREN"):
            expr = self.parse_expression()
            self.expect("RPAREN", ")")
            return expr
        if self.match("KEYWORD_NOT"):
            node = ASTNode("unary_op", "UnaryOp", "not", token.line, token.column)
            node.add(self.parse_factor())
            return node
        if self.current.token_type in ("PLUS", "MINUS"):
            op = self.advance()
            node = ASTNode("unary_op", "UnaryOp", op.lexeme, op.line, op.column)
            node.add(self.parse_factor())
            return node
        raise ASTParseError("Expected expression factor", self.current)


def build_ast(source_file: str | Path) -> Dict[str, Any]:
    builder = ASTBuilder(source_file)
    root = builder.build()
    return root.to_dict()
