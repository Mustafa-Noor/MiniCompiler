"""
LL(1) Predictive Parser for Mini Pascal
Stack-driven parser using LL(1) parsing table
"""

from typing import List, Dict, Tuple, Optional, Set
import sys
from pathlib import Path

# Add parent directory to path for lexer import
sys.path.insert(0, str(Path(__file__).parent.parent))

from lexer.scanner import Scanner
from lexer.token import Token, TokenType
from .first_follow import create_ll1_grammar, GrammarAnalyzer
from .parsing_table import ParsingTableGenerator


class ParseError(Exception):
    """Parsing error"""
    pass


class PredictiveParser:
    """
    LL(1) Predictive Parser for Mini Pascal.
    
    Uses a stack-driven algorithm with an LL(1) parsing table.
    Algorithm:
    1. Push $ onto stack
    2. Push start symbol onto stack
    3. While stack not empty:
       - If top is terminal: match with input
       - If top is non-terminal: use parsing table to expand
    
    Produces parser trace showing:
    - Stack contents
    - Input remaining
    - Action taken
    """
    
    # Terminal type mapping from Token to grammar symbols
    TOKEN_TO_SYMBOL = {
        'KEYWORD': {
            'program': 'KEYWORD_program',
            'var': 'KEYWORD_var',
            'integer': 'KEYWORD_integer',
            'real': 'KEYWORD_real',
            'array': 'KEYWORD_array',
            'of': 'KEYWORD_of',
            'function': 'KEYWORD_function',
            'procedure': 'KEYWORD_procedure',
            'begin': 'KEYWORD_begin',
            'end': 'KEYWORD_end',
            'if': 'KEYWORD_if',
            'then': 'KEYWORD_then',
            'else': 'KEYWORD_else',
            'while': 'KEYWORD_while',
            'do': 'KEYWORD_do',
            'or': 'KEYWORD_or',
            'div': 'KEYWORD_div',
            'mod': 'KEYWORD_mod',
            'and': 'KEYWORD_and',
            'not': 'KEYWORD_not',
        },
        'ID': 'ID',
        'NUMBER': 'NUMBER',
        'ASSIGN': 'ASSIGN',
        'EQ': 'relop',
        'NEQ': 'relop',
        'LT': 'relop',
        'LE': 'relop',
        'GT': 'relop',
        'GE': 'relop',
        'PLUS': 'PLUS',
        'MINUS': 'MINUS',
        'MULTIPLY': 'MULTIPLY',
        'DIVIDE': 'DIVIDE',
        'LPAREN': 'LPAREN',
        'RPAREN': 'RPAREN',
        'LBRACKET': 'LBRACKET',
        'RBRACKET': 'RBRACKET',
        'SEMICOLON': 'SEMICOLON',
        'COLON': 'COLON',
        'COMMA': 'COMMA',
        'DOT': 'DOT',
        'DOUBLE_DOT': 'DOUBLE_DOT',
        'EOF': 'EOF',
    }
    
    def __init__(self, scanner: Scanner):
        """
        Initialize the predictive parser.
        
        Args:
            scanner: Lexical scanner instance
        """
        self.scanner = scanner
        self.grammar = create_ll1_grammar()
        self.analyzer = GrammarAnalyzer(self.grammar)
        self.table_gen = ParsingTableGenerator(self.grammar, self.analyzer)
        
        # Parser state
        self.stack: List[str] = []
        self.input_tokens: List[Token] = []
        self.trace: List[str] = []
        self.errors: List[Dict[str, object]] = []
        self.max_errors = 25
        
        # Read all tokens
        self._read_all_tokens()
        self.input_pos = 0
    
    def _read_all_tokens(self):
        """Read all tokens from scanner"""
        while True:
            token = self.scanner.get_next_token()
            self.input_tokens.append(token)
            if token.token_type == 'EOF':
                break
    
    def _get_current_token(self) -> Token:
        """Get current input token"""
        if self.input_pos < len(self.input_tokens):
            return self.input_tokens[self.input_pos]
        return self.input_tokens[-1]  # Return EOF
    
    def _advance(self):
        """Move to next input token"""
        self.input_pos += 1
    
    def _token_to_symbol(self, token: Token) -> str:
        """Convert token to grammar symbol"""
        token_type = token.token_type

        if token_type == 'KEYWORD':
            lexeme_lower = token.lexeme.lower()
            return self.TOKEN_TO_SYMBOL['KEYWORD'].get(
                lexeme_lower, 'KEYWORD_' + lexeme_lower)

        if isinstance(token_type, str) and token_type.startswith('KEYWORD_'):
            keyword = token_type[len('KEYWORD_'):].lower()
            return f'KEYWORD_{keyword}'

        return self.TOKEN_TO_SYMBOL.get(token_type, token_type)
    
    def _log_step(self, step_num: int, stack_top: Optional[str], action: str):
        """Log a parse step"""
        stack_str = ' '.join(reversed(self.stack)) if self.stack else 'ε'
        
        # Get remaining input
        input_str = ' '.join(
            t.lexeme for t in self.input_tokens[self.input_pos:]
        )
        
        line = f"Step {step_num:3d}: [{stack_str:50s}] [{input_str:40s}] {action}"
        self.trace.append(line)
    
    def _record_error(self, message: str, action: str, step: int, stack_top: Optional[str]) -> None:
        token = self._get_current_token()
        self.errors.append({
            'line': token.line,
            'column': token.column,
            'message': message,
            'lexeme': token.lexeme,
        })
        self._log_step(step, stack_top, f"ERROR: {action}")

    def _sync_tokens(self) -> Set[str]:
        """Common synchronization terminals for panic-mode recovery."""
        return {
            'SEMICOLON', 'KEYWORD_END', 'EOF', 'RPAREN', 'RBRACKET',
            'KEYWORD_THEN', 'KEYWORD_ELSE', 'KEYWORD_DO',
        }

    def _panic_recover(self, stack_non_terminal: str, step: int) -> bool:
        """
        Skip input tokens until a symbol in FOLLOW(non_terminal) or sync set.
        Pop the faulting non-terminal so parsing can continue.
        """
        follow = set(self.analyzer.get_follow_set(stack_non_terminal))
        sync = follow | self._sync_tokens()
        skipped = 0

        while self.input_pos < len(self.input_tokens):
            token = self._get_current_token()
            if token.token_type == 'EOF':
                break
            symbol = self._token_to_symbol(token)
            if symbol in sync:
                break
            self._advance()
            skipped += 1
            if skipped > 50:
                break

        if self.stack and self.stack[-1] == stack_non_terminal:
            self.stack.pop()

        self._log_step(step, stack_non_terminal, f"RECOVER skip {skipped} token(s), pop {stack_non_terminal}")
        return skipped > 0 or bool(sync & follow)

    def parse(self) -> Tuple[bool, str, List[Dict[str, object]]]:
        """
        Parse using stack-driven LL(1) algorithm.
        
        Returns:
            Tuple of (success: bool, trace: str, errors: List[str])
        """
        # Initialize stack
        self.stack = ['EOF', 'program']
        self.input_pos = 0
        step = 0
        recovered = False
        
        # Add header to trace
        self.trace = [
            "LL(1) Predictive Parser Trace",
            "=" * 150,
            f"{'Step':<5} {'Stack':<52} {'Input':<42} {'Action':<50}",
            "-" * 150,
        ]
        
        try:
            while self.stack:
                step += 1
                top = self.stack.pop()
                current_token = self._get_current_token()
                
                # Convert token to symbol
                input_symbol = self._token_to_symbol(current_token)
                
                if top == 'EOF':
                    # Reached bottom of stack
                    if current_token.token_type == 'EOF':
                        action = "ACCEPT - Parsing successful!"
                        self._log_step(step, top, action)
                        return True, self._format_trace(), self.errors
                    else:
                        error = f"Expected EOF, found {current_token.lexeme}"
                        self._record_error(error, error, step, top)
                        return False, self._format_trace(), self.errors
                
                # Terminal on stack
                elif top in self.TERMINALS_SET():
                    if top == input_symbol or top == current_token.token_type:
                        # Match!
                        action = f"MATCH {top} '{current_token.lexeme}'"
                        self._log_step(step, top, action)
                        self._advance()
                    else:
                        error = f"Expected {top}, found {current_token.lexeme}"
                        self._record_error(error, error, step, top)
                        if len(self.errors) >= self.max_errors:
                            return False, self._format_trace(), self.errors
                        self._advance()
                        recovered = True
                        continue
                
                # Non-terminal on stack
                else:
                    production = self.table_gen.get_production(top, input_symbol)
                    
                    if production is None:
                        error = f"No production for [{top}, {input_symbol}]"
                        self._record_error(error, error, step, top)
                        if len(self.errors) >= self.max_errors:
                            return False, self._format_trace(), self.errors
                        if not self._panic_recover(top, step):
                            return False, self._format_trace(), self.errors
                        recovered = True
                        continue
                    
                    # Push production onto stack (reversed)
                    if production != ['EPSILON']:
                        for symbol in reversed(production):
                            self.stack.append(symbol)
                    
                    prod_str = ' '.join(production) if production != ['EPSILON'] else 'ε'
                    action = f"EXPAND {top} → {prod_str}"
                    self._log_step(step, top, action)
            
            # Stack empty - parsing complete
            if current_token.token_type == 'EOF':
                action = "ACCEPT - Parsing successful!"
                self._log_step(step + 1, None, action)
                return True, self._format_trace(), self.errors
            else:
                error = f"Unexpected input: {current_token.lexeme}"
                self._record_error(error, error, step + 1, None)
                return False, self._format_trace(), self.errors
        
        except Exception as e:
            error = f"Parser exception: {str(e)}"
            token = self._get_current_token()
            self.errors.append({
                'line': token.line,
                'column': token.column,
                'message': error,
                'lexeme': token.lexeme,
            })
            self._log_step(step, None, f"ERROR: {error}")
            return False, self._format_trace(), self.errors

    def TERMINALS_SET(self) -> set:
        """Get set of all terminals"""
        terminals = set()
        for token_type in self.TOKEN_TO_SYMBOL.values():
            if isinstance(token_type, dict):
                terminals.update(token_type.values())
            elif isinstance(token_type, str):
                terminals.add(token_type)
        return terminals

    def _format_trace(self) -> str:
        """Format the trace as a string"""
        return '\n'.join(self.trace)


def parse_file(filename: str) -> Tuple[bool, str, List[str]]:
    """
    Parse a Pascal file using the LL(1) predictive parser.
    
    Args:
        filename: Path to source file
        
    Returns:
        Tuple of (success: bool, trace: str, errors: List[str])
    """
    try:
        scanner = Scanner(filename)
        parser = PredictiveParser(scanner)
        return parser.parse()
    except Exception as e:
        return False, "", [str(e)]


if __name__ == '__main__':
    # Example usage
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        success, trace, errors = parse_file(filename)
        
        print("LL(1) Predictive Parser Output")
        print("=" * 60)
        print("\nParsing Trace:")
        print(trace)
        
        if errors:
            print("\nErrors:")
            for error in errors:
                print(f"  {error}")
        
        print(f"\nResult: {'ACCEPT' if success else 'REJECT'}")
