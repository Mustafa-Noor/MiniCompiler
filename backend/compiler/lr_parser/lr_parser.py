"""
SLR(1) Parser for Mini Pascal Compiler
Implements shift-reduce parsing using LR(0) items and FOLLOW sets
"""

from typing import Dict, Set, List, Tuple, Optional, Any
from enum import Enum
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lexer.scanner import Scanner
from lexer.token import Token, TokenType
from error_handler.error_handler import ErrorHandler, ErrorType
from parsers.first_follow import create_ll1_grammar, GrammarAnalyzer


class ActionType(Enum):
    """Types of shift-reduce actions"""
    SHIFT = "shift"
    REDUCE = "reduce"
    ACCEPT = "accept"
    ERROR = "error"


class LRItem:
    """
    LR(0) item: represents a position in a production.
    Example: [A → α • β, lookahead] means we've seen α and expect β
    
    Note: SLR(1) uses FOLLOW sets as lookahead, not computed lookahead
    """
    
    def __init__(self, production: Tuple[str, List[str]], dot_position: int):
        """
        Initialize an LR item.
        
        Args:
            production: Tuple of (non_terminal, production_symbols)
            dot_position: Position of the dot in the production
        """
        self.non_terminal, self.symbols = production
        self.dot_position = dot_position
    
    def __hash__(self) -> int:
        """Hash for use in sets"""
        return hash((self.non_terminal, tuple(self.symbols), self.dot_position))
    
    def __eq__(self, other) -> bool:
        """Equality comparison"""
        if not isinstance(other, LRItem):
            return False
        return (self.non_terminal == other.non_terminal and
                self.symbols == other.symbols and
                self.dot_position == other.dot_position)
    
    def __repr__(self) -> str:
        """String representation"""
        symbols = []
        for i, sym in enumerate(self.symbols):
            if i == self.dot_position:
                symbols.append("•")
            symbols.append(sym)
        if self.dot_position == len(self.symbols):
            symbols.append("•")
        
        prod_str = " ".join(symbols)
        return f"[{self.non_terminal} → {prod_str}]"
    
    def get_next_symbol(self) -> Optional[str]:
        """Get symbol after the dot"""
        if self.dot_position < len(self.symbols):
            return self.symbols[self.dot_position]
        return None
    
    def is_reduce_item(self) -> bool:
        """Check if this is a reduce item (dot at end)"""
        return self.dot_position >= len(self.symbols)
    
    def advance(self) -> 'LRItem':
        """Create new item with dot advanced"""
        return LRItem((self.non_terminal, self.symbols), 
                     self.dot_position + 1)


class LRItemSet:
    """Set of LR(0) items representing a parser state"""
    
    def __init__(self, items: Set[LRItem] = None):
        """Initialize item set"""
        self.items = items if items is not None else set()
    
    def __hash__(self) -> int:
        """Hash for use in sets"""
        return hash(frozenset(self.items))
    
    def __eq__(self, other) -> bool:
        """Equality comparison"""
        if not isinstance(other, LRItemSet):
            return False
        return self.items == other.items
    
    def __repr__(self) -> str:
        """String representation"""
        return f"ItemSet({len(self.items)} items)"
    
    def add_item(self, item: LRItem) -> None:
        """Add an item to the set"""
        self.items.add(item)
    
    def add_items(self, items: Set[LRItem]) -> None:
        """Add multiple items to the set"""
        self.items.update(items)
    
    def closure(self, grammar: Dict) -> 'LRItemSet':
        """
        Compute closure of item set.
        For each item [A → α • B β]:
        - Add all items [B → • γ] for each production B → γ
        
        Epsilon productions are advanced in-place so reduce items appear
        without requiring a shift on the EPSILON pseudo-terminal.
        
        Args:
            grammar: Grammar dictionary
            
        Returns:
            New ItemSet with closure computed
        """
        closure_set = LRItemSet(set(self.items))
        added = True
        
        while added:
            added = False
            new_items = set()
            
            for item in list(closure_set.items):
                current = item
                while current.get_next_symbol() == 'EPSILON':
                    current = current.advance()
                if current != item and current not in closure_set.items:
                    new_items.add(current)
                    added = True
            
            closure_set.add_items(new_items)
            new_items = set()
            
            for item in closure_set.items:
                next_sym = item.get_next_symbol()
                
                if next_sym and next_sym != 'EPSILON' and next_sym in grammar:
                    for production in grammar[next_sym]:
                        new_item = LRItem((next_sym, production), 0)
                        if new_item not in closure_set.items:
                            new_items.add(new_item)
                            added = True
            
            closure_set.add_items(new_items)
        
        return closure_set
    
    def goto(self, symbol: str) -> 'LRItemSet':
        """
        Compute GOTO for a symbol.
        GOTO(I, X) = closure({[A → αX • β] | [A → α • Xβ] in I})
        
        Args:
            symbol: Symbol to compute GOTO for
            
        Returns:
            New ItemSet representing GOTO(I, symbol)
        """
        goto_items = set()
        
        for item in self.items:
            if item.get_next_symbol() == symbol:
                goto_items.add(item.advance())
        
        # Return closure of GOTO items
        return LRItemSet(goto_items)


class SLRParser:
    """
    SLR(1) Parser Implementation.
    
    Uses LR(0) item sets and FOLLOW sets to construct parsing tables.
    Implements shift-reduce parsing algorithm.
    """
    
    def __init__(self, grammar: Dict[str, List[List[str]]],
                 analyzer: GrammarAnalyzer):
        """
        Initialize SLR parser.
        
        Args:
            grammar: Grammar dictionary
            analyzer: GrammarAnalyzer with FIRST/FOLLOW sets
        """
        self.grammar = grammar
        self.analyzer = analyzer
        self.error_handler = ErrorHandler()
        
        # Parsing tables
        self.action_table: Dict[Tuple[int, str], Tuple[str, int]] = {}
        self.goto_table: Dict[Tuple[int, str], int] = {}
        
        # Item sets and state management
        self.item_sets: List[LRItemSet] = []
        self.state_map: Dict[frozenset, int] = {}
        
        # Production list
        self.productions: List[Tuple[str, List[str]]] = []
        self._build_production_list()
        
        # Build parser tables
        self._build_item_sets()
        self._build_parsing_tables()
    
    def _build_production_list(self) -> None:
        """Build list of all productions"""
        start_symbol = list(self.grammar.keys())[0]
        
        # Add augmented production: S' → S
        self.productions.append((f"{start_symbol}'", [start_symbol]))
        
        # Add all other productions
        for non_terminal, prods in self.grammar.items():
            for prod in prods:
                self.productions.append((non_terminal, prod))
    
    def _build_item_sets(self) -> None:
        """Build all LR(0) item sets"""
        start_symbol = list(self.grammar.keys())[0]
        
        # Create initial item set with augmented production
        initial_item = LRItem((f"{start_symbol}'", [start_symbol]), 0)
        initial_set = LRItemSet({initial_item})
        initial_set = initial_set.closure(self.grammar)
        
        self.item_sets = [initial_set]
        self.state_map[frozenset(initial_set.items)] = 0
        
        # Build all item sets (BFS)
        state_counter = 1
        queue = [initial_set]
        
        while queue:
            current_set = queue.pop(0)
            
            # Collect symbols that appear after dots
            symbols = set()
            for item in current_set.items:
                next_sym = item.get_next_symbol()
                if next_sym and next_sym != 'EPSILON':
                    symbols.add(next_sym)
            
            # Compute GOTO for each symbol
            for symbol in sorted(symbols):
                goto_set = current_set.goto(symbol).closure(self.grammar)
                
                # Check if we've seen this set before
                goto_hash = frozenset(goto_set.items)
                if goto_hash not in self.state_map:
                    self.state_map[goto_hash] = state_counter
                    self.item_sets.append(goto_set)
                    queue.append(goto_set)
                    state_counter += 1
    
    def _build_parsing_tables(self) -> None:
        """Build ACTION and GOTO tables"""
        
        for state_id, item_set in enumerate(self.item_sets):
            for item in item_set.items:
                next_sym = item.get_next_symbol()
                
                if next_sym is None:
                    # Reduce item
                    if item.non_terminal == f"{list(self.grammar.keys())[0]}'":
                        # Accept item
                        self.action_table[(state_id, 'EOF')] = ('accept', -1)
                    else:
                        # Find production number
                        prod_num = self._find_production_number(
                            item.non_terminal, item.symbols)
                        
                        # Add reduce action for all terminals in FOLLOW
                        follow_set = self.analyzer.get_follow_set(item.non_terminal)
                        for terminal in follow_set:
                            self.action_table[(state_id, terminal)] = \
                                ('reduce', prod_num)
                
                elif next_sym in self._get_terminals():
                    # Shift item
                    # Find GOTO state
                    goto_set = item_set.goto(next_sym).closure(self.grammar)
                    next_state = self.state_map.get(frozenset(goto_set.items))
                    
                    if next_state is not None:
                        self.action_table[(state_id, next_sym)] = \
                            ('shift', next_state)
                
                else:
                    # Non-terminal: add GOTO entry
                    goto_set = item_set.goto(next_sym).closure(self.grammar)
                    next_state = self.state_map.get(frozenset(goto_set.items))
                    
                    if next_state is not None:
                        self.goto_table[(state_id, next_sym)] = next_state
    
    def _get_terminals(self) -> Set[str]:
        """Get set of all terminals in grammar (excluding EPSILON)"""
        terminals = set()
        for non_terminal, prods in self.grammar.items():
            for prod in prods:
                for sym in prod:
                    if sym != 'EPSILON' and self.analyzer._is_terminal(sym):
                        terminals.add(sym)
        return terminals
    
    def _find_production_number(self, non_terminal: str,
                               symbols: List[str]) -> int:
        """Find production number in production list"""
        for i, (nt, prod) in enumerate(self.productions):
            if nt == non_terminal and prod == symbols:
                return i
        return -1
    
    def parse(self, tokens: List[Token]) -> Tuple[bool, str, List[str]]:
        """
        Parse input using shift-reduce algorithm.
        
        Args:
            tokens: List of tokens from lexer
            
        Returns:
            Tuple of (success, trace, errors)
        """
        state_stack = [0]
        symbol_stack = ['$']
        input_pos = 0
        trace = []
        step = 0
        
        trace.append("SLR(1) Parser Trace")
        trace.append("=" * 120)
        trace.append(f"{'Step':<5} {'State Stack':<20} {'Symbol Stack':<40} "
                    f"{'Input':<30} {'Action':<20}")
        trace.append("-" * 120)
        
        while True:
            step += 1
            current_state = state_stack[-1]
            current_token = tokens[input_pos] if input_pos < len(tokens) else \
                           Token(TokenType.EOF, 'EOF', 0, 0)
            
            # Convert token to symbol
            input_symbol = self._token_to_symbol(current_token)
            
            # Look up action
            action_key = (current_state, input_symbol)
            action = self.action_table.get(action_key)
            
            if action is None:
                error_msg = f"Parse error at state {current_state}, "
                error_msg += f"input {input_symbol}"
                self.error_handler.add_syntax_error(
                    current_token.line, current_token.column, error_msg)
                trace.append(f"Step {step}: ERROR - {error_msg}")
                return False, '\n'.join(trace), [str(e) for e in 
                                                self.error_handler.get_errors()]
            
            action_type, action_value = action
            
            # Format trace
            state_str = ' '.join(map(str, state_stack[-3:]))
            symbol_str = ' '.join(symbol_stack[-3:])
            input_str = ' '.join(t.lexeme for t in tokens[input_pos:input_pos+3])
            
            if action_type == 'shift':
                trace.append(f"Step {step:<5} {state_str:<20} {symbol_str:<40} "
                           f"{input_str:<30} SHIFT → state {action_value}")
                state_stack.append(action_value)
                symbol_stack.append(input_symbol)
                input_pos += 1
            
            elif action_type == 'reduce':
                prod_num = action_value
                nt, symbols = self.productions[prod_num]
                trace.append(f"Step {step:<5} {state_str:<20} {symbol_str:<40} "
                           f"{input_str:<30} REDUCE {nt} -> ...")
                
                # Epsilon productions have nothing to pop
                pop_count = 0 if symbols == ['EPSILON'] else len(symbols)
                for _ in range(pop_count):
                    if state_stack:
                        state_stack.pop()
                    if symbol_stack:
                        symbol_stack.pop()
                
                # Push non-terminal
                prev_state = state_stack[-1]
                goto_state = self.goto_table.get((prev_state, nt))
                if goto_state is not None:
                    state_stack.append(goto_state)
                    symbol_stack.append(nt)
            
            elif action_type == 'accept':
                trace.append(f"Step {step:<5} {state_str:<20} {symbol_str:<40} "
                           f"{input_str:<30} ACCEPT")
                return True, '\n'.join(trace), []
        
        return False, '\n'.join(trace), []
    
    def _token_to_symbol(self, token: Token) -> str:
        """Convert token to grammar symbol"""
        if token.token_type == TokenType.EOF:
            return 'EOF'

        token_type = token.token_type

        # Scanner emits KEYWORD_PROGRAM, KEYWORD_var, etc.
        if isinstance(token_type, str) and token_type.startswith('KEYWORD_'):
            keyword = token_type[len('KEYWORD_'):].lower()
            return f'KEYWORD_{keyword}'

        token_map = {
            'ID': 'ID',
            'NUMBER': 'NUMBER',
            'LPAREN': 'LPAREN',
            'RPAREN': 'RPAREN',
            'LBRACKET': 'LBRACKET',
            'RBRACKET': 'RBRACKET',
            'SEMICOLON': 'SEMICOLON',
            'COLON': 'COLON',
            'COMMA': 'COMMA',
            'DOT': 'DOT',
            'DOUBLE_DOT': 'DOUBLE_DOT',
            'ASSIGN': 'ASSIGN',
            'PLUS': 'PLUS',
            'MINUS': 'MINUS',
            'MULTIPLY': 'MULTIPLY',
            'DIVIDE': 'DIVIDE',
            'MOD': 'mulop',
            'INT_DIV': 'mulop',
            'EQ': 'relop',
            'NEQ': 'relop',
            'LT': 'relop',
            'LE': 'relop',
            'GT': 'relop',
            'GE': 'relop',
        }

        return token_map.get(token_type, token_type)
    
    def print_action_table(self) -> str:
        """Generate formatted ACTION table"""
        output = "ACTION Table\n"
        output += "=" * 100 + "\n\n"
        
        # Group by state
        states = set(key[0] for key in self.action_table.keys())
        
        for state in sorted(states):
            output += f"State {state}:\n"
            for (s, terminal), (action_type, value) in \
                    sorted(self.action_table.items()):
                if s == state:
                    if action_type == 'shift':
                        output += f"  {terminal:<15} → shift {value}\n"
                    elif action_type == 'reduce':
                        nt, prod = self.productions[value]
                        output += f"  {terminal:<15} → reduce {value} ({nt})\n"
                    elif action_type == 'accept':
                        output += f"  {terminal:<15} → accept\n"
            output += "\n"
        
        return output
    
    def print_goto_table(self) -> str:
        """Generate formatted GOTO table"""
        output = "GOTO Table\n"
        output += "=" * 100 + "\n\n"
        
        # Group by state
        states = set(key[0] for key in self.goto_table.keys())
        
        for state in sorted(states):
            output += f"State {state}:\n"
            for (s, nt), next_state in sorted(self.goto_table.items()):
                if s == state:
                    output += f"  {nt:<20} → {next_state}\n"
            output += "\n"
        
        return output


if __name__ == '__main__':
    from parsers.first_follow import create_ll1_grammar
    
    grammar = create_ll1_grammar()
    analyzer = GrammarAnalyzer(grammar)
    parser = SLRParser(grammar, analyzer)
    
    print(parser.print_action_table())
    print(parser.print_goto_table())
