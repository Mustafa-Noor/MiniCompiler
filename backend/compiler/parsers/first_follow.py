"""
FIRST and FOLLOW Set Computation for LL(1) Grammar
Implements computation of FIRST and FOLLOW sets for grammar analysis
"""

from typing import Dict, Set, List, Tuple


class GrammarAnalyzer:
    """
    Analyzes an LL(1) grammar to compute FIRST and FOLLOW sets.
    
    The grammar is stored as a dictionary where:
    - Keys are non-terminal symbols (strings)
    - Values are lists of productions (alternatives)
    - Each production is a list of symbols (non-terminals and terminals)
    
    Terminals are represented as:
    - Keywords/operators in ALL_CAPS or quoted strings
    - EPSILON for empty production
    """
    
    # Terminal symbols in the grammar
    TERMINALS = {
        'program', 'var', 'integer', 'real', 'array', 'of',
        'function', 'procedure', 'begin', 'end', 'if', 'then', 'else',
        'while', 'do', 'assignop', 'relop', 'addop', 'mulop', 'sign', 'not',
        'ID', 'NUMBER', 'LPAREN', 'RPAREN', 'LBRACKET', 'RBRACKET',
        'SEMICOLON', 'COLON', 'COMMA', 'DOT', 'DOUBLE_DOT', 'EOF', 'EPSILON'
    }
    
    def __init__(self, grammar: Dict[str, List[List[str]]]):
        """
        Initialize the analyzer with a grammar.
        
        Args:
            grammar: Dictionary of {non-terminal: [[production1], [production2], ...]}
        """
        self.grammar = grammar
        self.first_sets: Dict[str, Set[str]] = {}
        self.follow_sets: Dict[str, Set[str]] = {}
        self._compute_first_sets()
        self._compute_follow_sets()
    
    def _is_terminal(self, symbol: str) -> bool:
        """Check if a symbol is a terminal"""
        if symbol == 'EPSILON':
            return True
        if symbol in self.grammar:
            return False
        return (
            symbol in self.TERMINALS
            or symbol.isupper()
            or symbol.startswith('KEYWORD_')
        )
    
    def _compute_first_sets(self):
        """Compute FIRST sets for all non-terminals"""
        # Initialize FIRST sets
        for non_terminal in self.grammar:
            self.first_sets[non_terminal] = set()
        
        # Iterate until no changes (fixed point)
        changed = True
        while changed:
            changed = False
            
            for non_terminal, productions in self.grammar.items():
                old_size = len(self.first_sets[non_terminal])
                
                for production in productions:
                    # Handle empty production
                    if not production or production[0] == 'EPSILON':
                        self.first_sets[non_terminal].add('EPSILON')
                        continue
                    
                    # Process symbols in production
                    can_derive_epsilon = True
                    for symbol in production:
                        if self._is_terminal(symbol):
                            self.first_sets[non_terminal].add(symbol)
                            can_derive_epsilon = False
                            break
                        else:
                            # Add FIRST of non-terminal (except EPSILON)
                            first_of_symbol = self.first_sets.get(symbol, set()) - {'EPSILON'}
                            self.first_sets[non_terminal].update(first_of_symbol)
                            
                            # If non-terminal can't derive epsilon, stop
                            if 'EPSILON' not in self.first_sets.get(symbol, set()):
                                can_derive_epsilon = False
                                break
                    
                    # If all symbols derive epsilon, add epsilon to FIRST
                    if can_derive_epsilon:
                        self.first_sets[non_terminal].add('EPSILON')
                
                # Check if changed
                if len(self.first_sets[non_terminal]) > old_size:
                    changed = True
    
    def _compute_follow_sets(self):
        """Compute FOLLOW sets for all non-terminals"""
        # Initialize FOLLOW sets
        for non_terminal in self.grammar:
            self.follow_sets[non_terminal] = set()
        
        # Add EOF to FOLLOW of start symbol
        start_symbol = list(self.grammar.keys())[0]
        self.follow_sets[start_symbol].add('EOF')
        
        # Iterate until no changes (fixed point)
        changed = True
        while changed:
            changed = False
            
            for non_terminal, productions in self.grammar.items():
                for production in productions:
                    for i, symbol in enumerate(production):
                        # Only compute FOLLOW for non-terminals
                        if self._is_terminal(symbol) or symbol == 'EPSILON':
                            continue
                        
                        # Skip if symbol not in grammar
                        if symbol not in self.follow_sets:
                            continue
                        
                        old_size = len(self.follow_sets[symbol])
                        
                        # Get symbols after current symbol
                        symbols_after = production[i + 1:]
                        
                        if not symbols_after:
                            # No symbols after, add FOLLOW of non_terminal
                            self.follow_sets[symbol].update(
                                self.follow_sets.get(non_terminal, set())
                            )
                        else:
                            # Add FIRST of symbols after
                            can_derive_epsilon = True
                            for next_symbol in symbols_after:
                                if self._is_terminal(next_symbol):
                                    self.follow_sets[symbol].add(next_symbol)
                                    can_derive_epsilon = False
                                    break
                                else:
                                    first_of_next = self.first_sets.get(next_symbol, set()) - {'EPSILON'}
                                    self.follow_sets[symbol].update(first_of_next)
                                    
                                    if 'EPSILON' not in self.first_sets.get(next_symbol, set()):
                                        can_derive_epsilon = False
                                        break
                            
                            # If all symbols after derive epsilon, add FOLLOW of non_terminal
                            if can_derive_epsilon:
                                self.follow_sets[symbol].update(
                                    self.follow_sets.get(non_terminal, set())
                                )
                        
                        if len(self.follow_sets[symbol]) > old_size:
                            changed = True
    
    def get_first_set(self, symbol: str) -> Set[str]:
        """Get FIRST set of a symbol"""
        if self._is_terminal(symbol):
            return {symbol}
        return self.first_sets.get(symbol, set())
    
    def get_follow_set(self, non_terminal: str) -> Set[str]:
        """Get FOLLOW set of a non-terminal"""
        return self.follow_sets.get(non_terminal, set())
    
    def print_first_sets(self) -> str:
        """Generate formatted output for FIRST sets"""
        output = "FIRST Sets\n"
        output += "=" * 60 + "\n\n"
        
        for non_terminal in sorted(self.grammar.keys()):
            first_set = self.first_sets.get(non_terminal, set())
            first_str = ', '.join(sorted(first_set)) if first_set else 'EMPTY'
            output += f"FIRST({non_terminal:20s}) = {{ {first_str} }}\n"
        
        return output
    
    def print_follow_sets(self) -> str:
        """Generate formatted output for FOLLOW sets"""
        output = "FOLLOW Sets\n"
        output += "=" * 60 + "\n\n"
        
        for non_terminal in sorted(self.grammar.keys()):
            follow_set = self.follow_sets.get(non_terminal, set())
            follow_str = ', '.join(sorted(follow_set)) if follow_set else 'EMPTY'
            output += f"FOLLOW({non_terminal:20s}) = {{ {follow_str} }}\n"
        
        return output


def create_ll1_grammar() -> Dict[str, List[List[str]]]:
    """
    Create the LL(1) form of the Mini Pascal grammar.
    
    This grammar has been transformed from the Dragon Book's LALR(1) grammar
    by removing left recursion and applying left factoring.
    
    Returns:
        Dictionary representing the LL(1) grammar
    """
    
    grammar = {
        # Main program structure
        'program': [
            ['KEYWORD_program', 'ID', 'LPAREN', 'id_list', 'RPAREN', 'SEMICOLON',
             'declarations', 'subprogram_decls', 'compound_stmt', 'DOT']
        ],
        
        # Identifier list with right recursion
        'id_list': [
            ['ID', 'id_list_prime']
        ],
        'id_list_prime': [
            ['COMMA', 'ID', 'id_list_prime'],
            ['EPSILON']
        ],
        
        # Declarations (with right recursion)
        'declarations': [
            ['KEYWORD_var', 'id_list', 'COLON', 'type_spec', 'SEMICOLON', 'declarations'],
            ['EPSILON']
        ],
        
        # Type specification
        'type_spec': [
            ['KEYWORD_integer'],
            ['KEYWORD_real'],
            ['KEYWORD_array', 'LBRACKET', 'NUMBER', 'DOUBLE_DOT', 'NUMBER', 'RBRACKET',
             'KEYWORD_of', 'type_spec']
        ],
        
        # Subprogram declarations (right recursion)
        'subprogram_decls': [
            ['subprogram_decl', 'SEMICOLON', 'subprogram_decls'],
            ['EPSILON']
        ],
        
        # Single subprogram declaration
        'subprogram_decl': [
            ['subprogram_head', 'declarations', 'compound_stmt']
        ],
        
        # Subprogram head
        'subprogram_head': [
            ['KEYWORD_function', 'ID', 'arguments', 'COLON', 'type_spec', 'SEMICOLON'],
            ['KEYWORD_procedure', 'ID', 'arguments', 'SEMICOLON']
        ],
        
        # Arguments (optional parameter list)
        'arguments': [
            ['LPAREN', 'param_list', 'RPAREN'],
            ['EPSILON']
        ],
        
        # Parameter list
        'param_list': [
            ['id_list', 'COLON', 'type_spec', 'param_list_prime']
        ],
        'param_list_prime': [
            ['SEMICOLON', 'id_list', 'COLON', 'type_spec', 'param_list_prime'],
            ['EPSILON']
        ],
        
        # Compound statement
        'compound_stmt': [
            ['KEYWORD_begin', 'optional_stmts', 'KEYWORD_end']
        ],
        
        # Optional statements
        'optional_stmts': [
            ['stmt_list'],
            ['EPSILON']
        ],
        
        # Statement list (right recursion)
        'stmt_list': [
            ['statement', 'stmt_list_prime']
        ],
        'stmt_list_prime': [
            ['SEMICOLON', 'statement', 'stmt_list_prime'],
            ['EPSILON']
        ],
        
        # Individual statement
        'statement': [
            ['var_or_proc_call', 'stmt_tail'],
            ['compound_stmt'],
            ['KEYWORD_if', 'expression', 'KEYWORD_then', 'statement', 'else_part'],
            ['KEYWORD_while', 'expression', 'KEYWORD_do', 'statement']
        ],
        
        # Tail for variable assignment or procedure call
        'var_or_proc_call': [
            ['ID', 'var_or_proc_tail']
        ],
        'var_or_proc_tail': [
            ['LBRACKET', 'expression', 'RBRACKET', 'ASSIGN', 'expression'],
            ['ASSIGN', 'expression'],
            ['LPAREN', 'expr_list', 'RPAREN']
        ],
        
        # Empty tail after variable assignment or procedure call
        'stmt_tail': [
            ['EPSILON']
        ],
        
        # Optional else part
        'else_part': [
            ['KEYWORD_else', 'statement'],
            ['EPSILON']
        ],
        
        # Expression with relation operators
        'expression': [
            ['simple_expr', 'expr_prime']
        ],
        'expr_prime': [
            ['relop', 'simple_expr'],
            ['EPSILON']
        ],
        
        # Simple expression (handles addop right recursion)
        'simple_expr': [
            ['term', 'simple_expr_prime']
        ],
        'simple_expr_prime': [
            ['addop', 'term', 'simple_expr_prime'],
            ['EPSILON']
        ],
        
        # Term (handles mulop right recursion)
        'term': [
            ['factor', 'term_prime']
        ],
        'term_prime': [
            ['mulop', 'factor', 'term_prime'],
            ['EPSILON']
        ],
        
        # Factor
        'factor': [
            ['ID', 'factor_tail'],
            ['NUMBER'],
            ['LPAREN', 'expression', 'RPAREN'],
            ['KEYWORD_not', 'factor'],
            ['sign', 'factor']
        ],
        
        # Factor tail (function call or array subscript)
        'factor_tail': [
            ['LPAREN', 'expr_list', 'RPAREN'],
            ['EPSILON']
        ],
        
        # Expression list (right recursion)
        'expr_list': [
            ['expression', 'expr_list_prime'],
            ['EPSILON']
        ],
        'expr_list_prime': [
            ['COMMA', 'expression', 'expr_list_prime'],
            ['EPSILON']
        ],
        
        # Sign (unary operators)
        'sign': [
            ['PLUS'],
            ['MINUS']
        ],
        
        # Relation operators
        'relop': [
            ['EQ'],
            ['NEQ'],
            ['LT'],
            ['LE'],
            ['GT'],
            ['GE']
        ],
        
        # Addition operators
        'addop': [
            ['PLUS'],
            ['MINUS'],
            ['KEYWORD_or']
        ],
        
        # Multiplication operators
        'mulop': [
            ['MULTIPLY'],
            ['DIVIDE'],
            ['KEYWORD_div'],
            ['KEYWORD_mod'],
            ['KEYWORD_and']
        ]
    }
    
    return grammar


if __name__ == '__main__':
    # Test the analyzer
    grammar = create_ll1_grammar()
    analyzer = GrammarAnalyzer(grammar)
    
    # Print results
    print(analyzer.print_first_sets())
    print("\n\n")
    print(analyzer.print_follow_sets())
