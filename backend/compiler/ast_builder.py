"""AST builder for Mini Pascal source files."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from lexer.scanner import Scanner
from lexer.token import Token


@dataclass
class ASTNode:
    type: str
    value: Optional[str] = None
    children: List["ASTNode"] = field(default_factory=list)
    line: int = 0
    column: int = 0

    def add(self, node: Optional["ASTNode"]) -> Optional["ASTNode"]:
        if node is not None:
            self.children.append(node)
        return node

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {"type": self.type}
        if self.value is not None:
            data["value"] = self.value
        if self.line:
            data["line"] = self.line
        if self.column:
            data["column"] = self.column
        if self.children:
            data["children"] = [child.to_dict() for child in self.children]
        return data


class ASTBuilder:
    """Small recursive AST builder aligned with the Mini Pascal grammar."""

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    @property
    def current(self) -> Token:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]

    def advance(self) -> Token:
        token = self.current
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return token

    def match(self, token_type: str) -> Optional[Token]:
        if self.current.token_type == token_type:
            return self.advance()
        return None

    def expect(self, token_type: str) -> Token:
        if self.current.token_type != token_type:
            raise SyntaxError(
                f"Expected {token_type}, found {self.current.lexeme} "
                f"at line {self.current.line}, column {self.current.column}"
            )
        return self.advance()

    def parse(self) -> ASTNode:
        return self.parse_program()

    def parse_program(self) -> ASTNode:
        self.expect("KEYWORD_PROGRAM")
        name = self.expect("ID")
        root = ASTNode("Program", name.lexeme, line=name.line, column=name.column)

        if self.match("LPAREN"):
            root.add(self.parse_id_list("ProgramParameters"))
            self.expect("RPAREN")
        self.expect("SEMICOLON")

        root.add(self.parse_declarations())
        root.add(self.parse_subprograms())
        root.add(self.parse_compound_statement())
        self.expect("DOT")
        return root

    def parse_id_list(self, node_type: str = "IdentifierList") -> ASTNode:
        node = ASTNode(node_type)
        while self.current.token_type == "ID":
            tok = self.advance()
            node.add(ASTNode("Identifier", tok.lexeme, line=tok.line, column=tok.column))
            if not self.match("COMMA"):
                break
        return node

    def parse_declarations(self) -> ASTNode:
        node = ASTNode("Declarations")
        while self.match("KEYWORD_VAR"):
            ids = self.parse_id_list()
            self.expect("COLON")
            type_node = self.parse_type()
            self.expect("SEMICOLON")
            decl = ASTNode("VariableDeclaration")
            decl.add(ids)
            decl.add(type_node)
            node.add(decl)
        return node

    def parse_type(self) -> ASTNode:
        if self.current.token_type in ("KEYWORD_INTEGER", "KEYWORD_REAL"):
            tok = self.advance()
            return ASTNode("Type", tok.lexeme.lower(), line=tok.line, column=tok.column)
        if self.match("KEYWORD_ARRAY"):
            node = ASTNode("ArrayType")
            self.expect("LBRACKET")
            lower = self.expect("NUMBER")
            self.expect("DOUBLE_DOT")
            upper = self.expect("NUMBER")
            self.expect("RBRACKET")
            self.expect("KEYWORD_OF")
            node.add(ASTNode("LowerBound", lower.lexeme, line=lower.line, column=lower.column))
            node.add(ASTNode("UpperBound", upper.lexeme, line=upper.line, column=upper.column))
            node.add(self.parse_type())
            return node
        raise SyntaxError(f"Expected type, found {self.current.lexeme}")

    def parse_subprograms(self) -> ASTNode:
        node = ASTNode("Subprograms")
        while self.current.token_type in ("KEYWORD_FUNCTION", "KEYWORD_PROCEDURE"):
            node.add(self.parse_subprogram())
            self.expect("SEMICOLON")
        return node

    def parse_subprogram(self) -> ASTNode:
        if self.match("KEYWORD_FUNCTION"):
            name = self.expect("ID")
            node = ASTNode("Function", name.lexeme, line=name.line, column=name.column)
            node.add(self.parse_arguments())
            self.expect("COLON")
            node.add(ASTNode("ReturnType", children=[self.parse_type()]))
            self.expect("SEMICOLON")
        else:
            self.expect("KEYWORD_PROCEDURE")
            name = self.expect("ID")
            node = ASTNode("Procedure", name.lexeme, line=name.line, column=name.column)
            node.add(self.parse_arguments())
            self.expect("SEMICOLON")

        node.add(self.parse_declarations())
        node.add(self.parse_compound_statement())
        return node

    def parse_arguments(self) -> ASTNode:
        node = ASTNode("Parameters")
        if not self.match("LPAREN"):
            return node
        while self.current.token_type == "ID":
            group = ASTNode("ParameterGroup")
            group.add(self.parse_id_list())
            self.expect("COLON")
            group.add(self.parse_type())
            node.add(group)
            if not self.match("SEMICOLON"):
                break
        self.expect("RPAREN")
        return node

    def parse_compound_statement(self) -> ASTNode:
        begin = self.expect("KEYWORD_BEGIN")
        node = ASTNode("CompoundStatement", line=begin.line, column=begin.column)
        while self.current.token_type not in ("KEYWORD_END", "EOF"):
            node.add(self.parse_statement())
            self.match("SEMICOLON")
        self.expect("KEYWORD_END")
        return node

    def parse_statement(self) -> ASTNode:
        if self.current.token_type == "KEYWORD_BEGIN":
            return self.parse_compound_statement()
        if self.match("KEYWORD_IF"):
            node = ASTNode("IfStatement")
            node.add(ASTNode("Condition", children=[self.parse_expression_until({"KEYWORD_THEN"})]))
            self.expect("KEYWORD_THEN")
            node.add(self.parse_statement())
            if self.match("KEYWORD_ELSE"):
                node.add(ASTNode("Else", children=[self.parse_statement()]))
            return node
        if self.match("KEYWORD_WHILE"):
            node = ASTNode("WhileStatement")
            node.add(ASTNode("Condition", children=[self.parse_expression_until({"KEYWORD_DO"})]))
            self.expect("KEYWORD_DO")
            node.add(self.parse_statement())
            return node
        if self.current.token_type == "ID":
            return self.parse_id_statement()
        tok = self.advance()
        return ASTNode("UnknownStatement", tok.lexeme, line=tok.line, column=tok.column)

    def parse_id_statement(self) -> ASTNode:
        name = self.expect("ID")
        if self.match("LPAREN"):
            node = ASTNode("CallStatement", name.lexeme, line=name.line, column=name.column)
            node.add(self.parse_expression_list())
            self.expect("RPAREN")
            return node
        target = ASTNode("Target", name.lexeme, line=name.line, column=name.column)
        if self.match("LBRACKET"):
            target.add(ASTNode("Index", children=[self.parse_expression_until({"RBRACKET"})]))
            self.expect("RBRACKET")
        if self.match("ASSIGN"):
            node = ASTNode("Assignment")
            node.add(target)
            node.add(ASTNode("Expression", children=[self.parse_expression_until({"SEMICOLON", "KEYWORD_END", "KEYWORD_ELSE"})]))
            return node
        return ASTNode("ProcedureCall", name.lexeme, line=name.line, column=name.column)

    def parse_expression_list(self) -> ASTNode:
        node = ASTNode("Arguments")
        while self.current.token_type not in ("RPAREN", "EOF"):
            node.add(ASTNode("Expression", children=[self.parse_expression_until({"COMMA", "RPAREN"})]))
            if not self.match("COMMA"):
                break
        return node

    def parse_expression_until(self, stops: set[str]) -> ASTNode:
        node = ASTNode("ExpressionTokens")
        depth = 0
        while self.current.token_type != "EOF":
            if depth == 0 and self.current.token_type in stops:
                break
            tok = self.advance()
            if tok.token_type in ("LPAREN", "LBRACKET"):
                depth += 1
            elif tok.token_type in ("RPAREN", "RBRACKET") and depth:
                depth -= 1
            node.add(ASTNode(tok.token_type, tok.lexeme, line=tok.line, column=tok.column))
        return node


def build_ast_from_file(filename: str) -> Dict[str, Any]:
    scanner = Scanner(filename)
    try:
        tokens = scanner.scan()
    finally:
        scanner.close()
    ast = ASTBuilder(tokens).parse()
    return ast.to_dict()


def ast_to_json(ast: Dict[str, Any]) -> str:
    return json.dumps(ast, indent=2)
