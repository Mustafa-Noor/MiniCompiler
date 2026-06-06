"""
Recursive Descent Parser for Mini Pascal
Implements top-down parsing with one method per non-terminal
"""

from typing import List, Optional, Tuple, TYPE_CHECKING
import sys
from pathlib import Path

# Add parent directory to path for lexer import
sys.path.insert(0, str(Path(__file__).parent.parent))

from lexer.scanner import Scanner
from lexer.token import Token, TokenType
from symbol_table.symbol import DataType

if TYPE_CHECKING:
    from semantic_analyzer import SemanticAnalyzer


class SyntaxError(Exception):
    """Syntax error during parsing"""
    def __init__(self, message: str, token: Token):
        self.message = message
        self.token = token
        super().__init__(message)


class RecursiveDescentParser:
    """
    Recursive Descent Parser for Mini Pascal.
    
    Implements top-down parsing with one method per non-terminal.
    Produces a derivation trace and reports syntax errors.
    """
    
    def __init__(self, scanner: Scanner, semantic: Optional["SemanticAnalyzer"] = None):
        """
        Initialize the parser.
        
        Args:
            scanner: Lexical scanner instance
            semantic: Optional semantic analyzer for symbol table integration
        """
        self.scanner = scanner
        self.semantic = semantic
        self.current_token = scanner.get_next_token()
        self.trace = []
        self.errors = []
        self.depth = 0
        self._pending_params: List[Tuple[List[Tuple[str, int, int]], DataType]] = []
        self._last_expr_count = 0
    
    def _log_entry(self, non_terminal: str):
        """Log entry into a non-terminal"""
        self.trace.append(f"{'  ' * self.depth}→ {non_terminal} (Found: {self.current_token.token_type})")
        self.depth += 1
    
    def _log_exit(self, non_terminal: str, success: bool):
        """Log exit from a non-terminal"""
        self.depth -= 1
        status = "✓" if success else "✗"
        self.trace.append(f"{'  ' * self.depth}← {non_terminal} {status}")
    
    def _log_match(self, expected: str, actual: str):
        """Log token match"""
        self.trace.append(f"{'  ' * self.depth}[Match] {expected} = {actual}")
    
    def _expect(self, token_type: str, lexeme: Optional[str] = None) -> bool:
        """
        Match and consume a token.
        
        Args:
            token_type: Expected token type (can be 'KEYWORD_PROGRAM', 'ID', etc.)
            lexeme: Optional expected lexeme (for keywords)
            
        Returns:
            True if matched, False otherwise
        """
        if self.current_token.token_type != token_type:
            return False
        
        if lexeme and self.current_token.lexeme.lower() != lexeme.lower():
            return False
        
        actual_lexeme = self.current_token.lexeme
        self._log_match(token_type, actual_lexeme)
        self.current_token = self.scanner.get_next_token()
        return True
    
    def _error(self, expected: str):
        """Record a syntax error"""
        msg = f"Syntax Error: Line {self.current_token.line}, Column {self.current_token.column}: " \
              f"Expected {expected}, found {self.current_token.lexeme} ({self.current_token.token_type})"
        self.errors.append(msg)
        self.trace.append(f"ERROR: {msg}")
        raise SyntaxError(msg, self.current_token)
    
    def parse_program(self) -> bool:
        """
        Parse a program.
        program → program ID ( id_list ); declarations subprogram_decls compound_stmt .
        """
        self._log_entry('program')
        try:
            if not self._expect('KEYWORD_PROGRAM'):
                self._error('keyword program')
            if not self._expect('ID'):
                self._error('identifier')
            if not self._expect('LPAREN'):
                self._error('(')
            if not self.parse_id_list():
                self._error('identifier list')
            if not self._expect('RPAREN'):
                self._error(')')
            if not self._expect('SEMICOLON'):
                self._error(';')
            
            self.parse_declarations()
            self.parse_subprogram_declarations()
            
            if not self.parse_compound_statement():
                self._error('begin...end block')
            
            if not self._expect('DOT'):
                self._error('.')
            
            if self.current_token.token_type != 'EOF':
                self._error('end of file')
            
            self._log_exit('program', True)
            return True
        except SyntaxError:
            self._log_exit('program', False)
            return False
    
    def _collect_id_list(self) -> List[Tuple[str, int, int]]:
        """Collect identifier names with source positions."""
        names: List[Tuple[str, int, int]] = []
        if self.current_token.token_type != 'ID':
            return names

        while True:
            tok = self.current_token
            names.append((tok.lexeme, tok.line, tok.column))
            if not self._expect('ID'):
                break
            if not self._expect('COMMA'):
                break
        return names

    def parse_id_list(self) -> bool:
        """
        Parse identifier list.
        id_list → ID id_list_prime
        """
        self._log_entry('id_list')
        try:
            names = self._collect_id_list()
            if not names:
                raise SyntaxError("Expected identifier", self.current_token)

            self._log_exit('id_list', True)
            return True
        except SyntaxError:
            self._log_exit('id_list', False)
            return False
    
    def parse_declarations(self) -> bool:
        """
        Parse declarations.
        declarations → var id_list : type_spec ; declarations | ε
        """
        self._log_entry('declarations')
        try:
            while self._expect('KEYWORD_VAR'):
                names = self._collect_id_list()
                if not names:
                    self._error('identifier list')
                if not self._expect('COLON'):
                    self._error(':')
                dtype, arr_bounds = self._parse_type_info()
                if dtype is None:
                    self._error('type specification')
                if not self._expect('SEMICOLON'):
                    self._error(';')
                if self.semantic:
                    for name, line, col in names:
                        if arr_bounds:
                            lo, hi = arr_bounds
                            self.semantic.declare_array(name, dtype, lo, hi, line, col)
                        else:
                            self.semantic.declare_variable(name, dtype, line, col)

            self._log_exit('declarations', True)
            return True
        except SyntaxError:
            self._log_exit('declarations', False)
            return False

    def _parse_type_info(self) -> Tuple[Optional[DataType], Optional[Tuple[int, int]]]:
        """Parse a type and return (DataType, optional array bounds)."""
        if self._expect('KEYWORD_INTEGER'):
            return DataType.INTEGER, None
        if self._expect('KEYWORD_REAL'):
            return DataType.REAL, None

        if self._expect('KEYWORD_ARRAY'):
            if not self._expect('LBRACKET'):
                self._error('[')
            lower = int(self.current_token.lexeme) if self.current_token.token_type == 'NUMBER' else 0
            if not self._expect('NUMBER'):
                self._error('number')
            if not self._expect('DOUBLE_DOT'):
                self._error('..')
            upper = int(self.current_token.lexeme) if self.current_token.token_type == 'NUMBER' else 0
            if not self._expect('NUMBER'):
                self._error('number')
            if not self._expect('RBRACKET'):
                self._error(']')
            if not self._expect('KEYWORD_OF'):
                self._error('keyword of')
            element_type, _ = self._parse_type_info()
            if element_type is None:
                self._error('type specification')
            return element_type, (lower, upper)

        return None, None

    def _declare_pending_params(self, subprogram_name: Optional[str] = None) -> None:
        """Insert collected parameter names into the current scope."""
        if not self.semantic:
            return
        sub_sym = self.semantic.symbol_table.lookup(subprogram_name) if subprogram_name else None
        for names, dtype in self._pending_params:
            for name, line, col in names:
                self.semantic.declare_variable(name, dtype, line, col)
                if sub_sym is not None:
                    sub_sym.add_parameter(name, dtype)
        self._pending_params = []

    def parse_type_spec(self) -> bool:
        """
        Parse type specification.
        type_spec → integer | real | array [ num .. num ] of type_spec
        """
        self._log_entry('type_spec')
        try:
            dtype, _ = self._parse_type_info()
            if dtype is not None:
                self._log_exit('type_spec', True)
                return True
            self._error('type')
        except SyntaxError:
            self._log_exit('type_spec', False)
            return False
    
    def parse_subprogram_declarations(self) -> bool:
        """
        Parse subprogram declarations.
        subprogram_decls → subprogram_decl ; subprogram_decls | ε
        """
        self._log_entry('subprogram_declarations')
        try:
            # Check for function or procedure
            while self.current_token.token_type in ('KEYWORD_FUNCTION', 'KEYWORD_PROCEDURE'):
                
                if not self.parse_subprogram_declaration():
                    self._error('subprogram declaration')
                
                if not self._expect('SEMICOLON'):
                    self._error(';')
            
            self._log_exit('subprogram_declarations', True)
            return True
        except SyntaxError:
            self._log_exit('subprogram_declarations', False)
            return False
    
    def parse_subprogram_declaration(self) -> bool:
        """
        Parse a single subprogram declaration.
        subprogram_decl → subprogram_head declarations compound_stmt
        """
        self._log_entry('subprogram_declaration')
        scope_entered = False
        try:
            if not self.parse_subprogram_head():
                self._error('subprogram head')
            scope_entered = self.semantic is not None
            
            self.parse_declarations()
            
            if not self.parse_compound_statement():
                self._error('compound statement')

            if self.semantic:
                self.semantic.exit_scope()
                scope_entered = False
            
            self._log_exit('subprogram_declaration', True)
            return True
        except SyntaxError:
            if self.semantic and scope_entered:
                self.semantic.exit_scope()
            self._log_exit('subprogram_declaration', False)
            return False
    
    def parse_subprogram_head(self) -> bool:
        """
        Parse subprogram head.
        subprogram_head → function id arguments : type_spec ;
                        | procedure id arguments ;
        """
        self._log_entry('subprogram_head')
        try:
            self._pending_params = []

            if self._expect('KEYWORD_FUNCTION'):
                fn_tok = self.current_token
                if not self._expect('ID'):
                    self._error('identifier')
                fn_name, fn_line, fn_col = fn_tok.lexeme, fn_tok.line, fn_tok.column
                if not self.parse_arguments():
                    self._error('arguments')
                if not self._expect('COLON'):
                    self._error(':')
                return_type, _ = self._parse_type_info()
                if return_type is None:
                    self._error('type specification')
                if not self._expect('SEMICOLON'):
                    self._error(';')
                if self.semantic:
                    self.semantic.declare_function(fn_name, return_type, fn_line, fn_col)
                    self.semantic.enter_scope()
                    self._declare_pending_params(fn_name)
                self._log_exit('subprogram_head', True)
                return True
            
            if self._expect('KEYWORD_PROCEDURE'):
                proc_tok = self.current_token
                if not self._expect('ID'):
                    self._error('identifier')
                proc_name = proc_tok.lexeme
                proc_line, proc_col = proc_tok.line, proc_tok.column
                if not self.parse_arguments():
                    self._error('arguments')
                if self.semantic:
                    self.semantic.declare_procedure(proc_name, proc_line, proc_col)
                    self.semantic.enter_scope()
                    self._declare_pending_params(proc_name)
                self._log_exit('subprogram_head', True)
                return True
            
            self._error('function or procedure')
        except SyntaxError:
            self._log_exit('subprogram_head', False)
            return False
    
    def parse_arguments(self) -> bool:
        """
        Parse arguments.
        arguments → ( parameter_list ) | ε
        """
        self._log_entry('arguments')
        try:
            if self._expect('LPAREN'):
                self.parse_parameter_list()
                if not self._expect('RPAREN'):
                    self._error(')')
            
            self._log_exit('arguments', True)
            return True
        except SyntaxError:
            self._log_exit('arguments', False)
            return False
    
    def parse_parameter_list(self) -> bool:
        """
        Parse parameter list.
        parameter_list → id_list : type_spec (parameter_list_prime)*
        """
        self._log_entry('parameter_list')
        try:
            groups: List[Tuple[List[Tuple[str, int, int]], DataType]] = []

            names = self._collect_id_list()
            if not names:
                self._error('identifier list')
            if not self._expect('COLON'):
                self._error(':')
            dtype, _ = self._parse_type_info()
            if dtype is None:
                self._error('type specification')
            groups.append((names, dtype))

            while self._expect('SEMICOLON'):
                names = self._collect_id_list()
                if not names:
                    self._error('identifier list')
                if not self._expect('COLON'):
                    self._error(':')
                dtype, _ = self._parse_type_info()
                if dtype is None:
                    self._error('type specification')
                groups.append((names, dtype))

            self._pending_params = groups
            self._log_exit('parameter_list', True)
            return True
        except SyntaxError:
            self._log_exit('parameter_list', False)
            return False
    
    def parse_compound_statement(self) -> bool:
        """
        Parse compound statement.
        compound_stmt → begin optional_stmts end
        """
        self._log_entry('compound_statement')
        try:
            if not self._expect('KEYWORD_BEGIN'):
                self._error('keyword begin')
            
            self.parse_optional_statements()
            
            if not self._expect('KEYWORD_END'):
                self._error('keyword end')
            
            self._log_exit('compound_statement', True)
            return True
        except SyntaxError:
            self._log_exit('compound_statement', False)
            return False
    
    def parse_optional_statements(self) -> bool:
        """
        Parse optional statements.
        optional_stmts → statement_list | ε
        """
        self._log_entry('optional_statements')
        try:
            # Check if there's a statement
            if (self.current_token.token_type in ('ID', 'LPAREN') or 
                (self.current_token.token_type not in ('KEYWORD_END', 'EOF'))) and \
               not (self.current_token.token_type == 'KEYWORD_END'):
                self.parse_statement_list()
            
            self._log_exit('optional_statements', True)
            return True
        except SyntaxError:
            self._log_exit('optional_statements', False)
            return False
    
    def parse_statement_list(self) -> bool:
        """
        Parse statement list.
        stmt_list → statement (SEMICOLON statement)*
        """
        self._log_entry('statement_list')
        try:
            if not self.parse_statement():
                self._error('statement')
            
            while self.current_token.token_type == 'SEMICOLON':
                if not self._expect('SEMICOLON'):
                    self._error(';')
                if self.current_token.token_type not in ('KEYWORD_END', 'EOF'):
                    if not self.parse_statement():
                        self._error('statement')
            
            self._log_exit('statement_list', True)
            return True
        except SyntaxError:
            self._log_exit('statement_list', False)
            return False
    
    def parse_statement(self) -> bool:
        """
        Parse a statement.
        statement → ID ... | compound_stmt | if ... | while ...
        """
        self._log_entry('statement')
        try:
            # Compound statement
            if self.current_token.token_type == 'KEYWORD_BEGIN':
                if not self.parse_compound_statement():
                    self._error('compound statement')
                self._log_exit('statement', True)
                return True
            
            # If statement
            if self._expect('KEYWORD_IF'):
                if not self.parse_expression():
                    self._error('expression')
                if not self._expect('KEYWORD_THEN'):
                    self._error('keyword then')
                if not self.parse_statement():
                    self._error('statement')
                
                # Optional else
                if self.current_token.token_type == 'KEYWORD_ELSE':
                    self._expect('KEYWORD_ELSE')
                    if not self.parse_statement():
                        self._error('statement')
                
                self._log_exit('statement', True)
                return True
            
            # While statement
            if self._expect('KEYWORD_WHILE'):
                if not self.parse_expression():
                    self._error('expression')
                if not self._expect('KEYWORD_DO'):
                    self._error('keyword do')
                if not self.parse_statement():
                    self._error('statement')
                self._log_exit('statement', True)
                return True
            
            # ID-based statement (assignment or procedure call)
            if self.current_token.token_type == 'ID':
                id_name = self.current_token.lexeme
                id_line = self.current_token.line
                id_col = self.current_token.column
                self._expect('ID')
                
                # Check for array subscript
                if self.current_token.token_type == 'LBRACKET':
                    if self.semantic:
                        self.semantic.check_array_access(id_name, id_line, id_col)
                    self._expect('LBRACKET')
                    if not self.parse_expression():
                        self._error('expression')
                    if not self._expect('RBRACKET'):
                        self._error(']')
                    if not self._expect('ASSIGN'):
                        self._error(':=')
                    if not self.parse_expression():
                        self._error('expression')
                # Check for procedure call
                elif self.current_token.token_type == 'LPAREN':
                    self._expect('LPAREN')
                    self.parse_expression_list()
                    if not self._expect('RPAREN'):
                        self._error(')')
                    if self.semantic:
                        self.semantic.check_call_with_args(
                            id_name, self._last_expr_count, id_line, id_col
                        )
                # Check for assignment
                elif self.current_token.token_type == 'ASSIGN':
                    if self.semantic:
                        self.semantic.check_assignment_target(id_name, id_line, id_col)
                    self._expect('ASSIGN')
                    if not self.parse_expression():
                        self._error('expression')
                else:
                    if self.semantic:
                        self.semantic.check_procedure_call(id_name, id_line, id_col)
                
                self._log_exit('statement', True)
                return True
            
            self._error('statement')
            return False
        except SyntaxError:
            self._log_exit('statement', False)
            return False
    
    def parse_expression(self) -> bool:
        """
        Parse expression.
        expression → simple_expr (relop simple_expr)?
        """
        self._log_entry('expression')
        try:
            if not self.parse_simple_expression():
                self._error('simple expression')
            
            # Check for relation operator
            if self.current_token.token_type in ('EQ', 'NEQ', 'LT', 'LE', 'GT', 'GE', 'ASSIGN'):
                token_type = self.current_token.token_type
                self._expect(token_type)
                if not self.parse_simple_expression():
                    self._error('simple expression')
            
            self._log_exit('expression', True)
            return True
        except SyntaxError:
            self._log_exit('expression', False)
            return False
    
    def parse_simple_expression(self) -> bool:
        """
        Parse simple expression.
        simple_expr → (sign)? term (addop term)*
        """
        self._log_entry('simple_expression')
        try:
            # Optional sign
            if self.current_token.token_type in ('PLUS', 'MINUS'):
                self._expect(self.current_token.token_type)
            
            if not self.parse_term():
                self._error('term')
            
            # Additional terms
            while self.current_token.token_type in ('PLUS', 'MINUS', 'KEYWORD_OR'):
                token_type = self.current_token.token_type
                self._expect(token_type)
                if not self.parse_term():
                    self._error('term')
            
            self._log_exit('simple_expression', True)
            return True
        except SyntaxError:
            self._log_exit('simple_expression', False)
            return False
    
    def parse_term(self) -> bool:
        """
        Parse term.
        term → factor (mulop factor)*
        """
        self._log_entry('term')
        try:
            if not self.parse_factor():
                self._error('factor')
            
            # Additional factors
            while self.current_token.token_type in ('MULTIPLY', 'DIVIDE', 'KEYWORD_DIV', 'KEYWORD_MOD', 'KEYWORD_AND'):
                token_type = self.current_token.token_type
                self._expect(token_type)
                if not self.parse_factor():
                    self._error('factor')
            
            self._log_exit('term', True)
            return True
        except SyntaxError:
            self._log_exit('term', False)
            return False
    
    def parse_factor(self) -> bool:
        """
        Parse factor.
        factor → id (function_call)?
               | number
               | ( expression )
               | not factor
               | sign factor
        """
        self._log_entry('factor')
        try:
            if self.current_token.token_type == 'ID':
                id_name = self.current_token.lexeme
                id_line = self.current_token.line
                id_col = self.current_token.column
                self._expect('ID')

                if self._expect('LPAREN'):
                    self.parse_expression_list()
                    if not self._expect('RPAREN'):
                        self._error(')')
                    if self.semantic:
                        self.semantic.check_function_call(
                            id_name, self._last_expr_count, id_line, id_col
                        )
                elif self.semantic:
                    self.semantic.check_identifier_declared(id_name, id_line, id_col)

                self._log_exit('factor', True)
                return True
            
            if self._expect('NUMBER'):
                self._log_exit('factor', True)
                return True
            
            if self._expect('LPAREN'):
                if not self.parse_expression():
                    self._error('expression')
                if not self._expect('RPAREN'):
                    self._error(')')
                self._log_exit('factor', True)
                return True
            
            if self._expect('KEYWORD_NOT'):
                if not self.parse_factor():
                    self._error('factor')
                self._log_exit('factor', True)
                return True
            
            if self.current_token.token_type in ('PLUS', 'MINUS'):
                self._expect(self.current_token.token_type)
                if not self.parse_factor():
                    self._error('factor')
                self._log_exit('factor', True)
                return True
            
            self._error('factor')
        except SyntaxError:
            self._log_exit('factor', False)
            return False
    
    def parse_expression_list(self) -> bool:
        """
        Parse expression list.
        expr_list → expression (COMMA expression)*  | ε
        """
        self._log_entry('expression_list')
        try:
            self._last_expr_count = 0
            if self.current_token.token_type not in (
                'KEYWORD_END', 'KEYWORD_THEN', 'KEYWORD_DO', 'KEYWORD_ELSE',
                'SEMICOLON', 'RPAREN', 'RBRACKET', 'EOF',
            ):
                if not self.parse_expression():
                    raise SyntaxError("Expected expression", self.current_token)
                self._last_expr_count = 1

                while self._expect('COMMA'):
                    if not self.parse_expression():
                        self._error('expression')
                    self._last_expr_count += 1
            
            self._log_exit('expression_list', True)
            return True
        except SyntaxError:
            self._log_exit('expression_list', False)
            return False
    
    def get_trace(self) -> str:
        """Get the parsing trace as a formatted string"""
        return '\n'.join(self.trace)
    
    def get_errors(self) -> List[str]:
        """Get all syntax errors"""
        return self.errors


def parse_file(filename: str) -> Tuple[bool, str, List[str]]:
    """
    Parse a Pascal file using the recursive descent parser.
    
    Args:
        filename: Path to source file
        
    Returns:
        Tuple of (success: bool, trace: str, errors: List[str])
    """
    try:
        scanner = Scanner(filename)
        parser = RecursiveDescentParser(scanner)
        success = parser.parse_program()
        return success, parser.get_trace(), parser.get_errors()
    except Exception as e:
        return False, "", [str(e)]


if __name__ == '__main__':
    # Example usage
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        success, trace, errors = parse_file(filename)
        
        print("Recursive Descent Parser Output")
        print("=" * 60)
        print("\nParsing Trace:")
        print(trace)
        
        if errors:
            print("\nErrors:")
            for error in errors:
                print(f"  {error}")
        
        print(f"\nResult: {'ACCEPT' if success else 'REJECT'}")
