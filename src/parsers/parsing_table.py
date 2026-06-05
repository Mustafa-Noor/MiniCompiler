"""
LL(1) Parsing Table Construction
Builds the M[A, a] parsing table from grammar, FIRST and FOLLOW sets
"""

from typing import Dict, Set, List, Tuple, Optional
from .first_follow import GrammarAnalyzer


class ParsingTableGenerator:
    """
    Generates an LL(1) parsing table from grammar and FIRST/FOLLOW sets.
    
    The parsing table M[A, a] contains:
    - A: non-terminal
    - a: terminal
    - value: production (or error)
    """
    
    def __init__(self, grammar: Dict[str, List[List[str]]], 
                 analyzer: GrammarAnalyzer):
        """
        Initialize the parsing table generator.
        
        Args:
            grammar: Dictionary of {non-terminal: [[production1], ...]}
            analyzer: GrammarAnalyzer instance with FIRST/FOLLOW sets
        """
        self.grammar = grammar
        self.analyzer = analyzer
        self.parsing_table: Dict[Tuple[str, str], List[str]] = {}
        self._build_table()
    
    def _build_table(self):
        """Build the LL(1) parsing table using the algorithm from Dragon Book"""
        
        # For each production A → α
        for non_terminal, productions in self.grammar.items():
            for production in productions:
                # Compute FIRST(α)
                first_of_alpha = self._compute_first_of_production(production)
                
                # For each terminal 'a' in FIRST(α) - {ε}
                for terminal in first_of_alpha - {'EPSILON'}:
                    table_key = (non_terminal, terminal)
                    if table_key in self.parsing_table:
                        # Conflict detected - grammar is not LL(1)
                        print(f"ERROR: LL(1) conflict at [{non_terminal}, {terminal}]")
                    self.parsing_table[table_key] = production
                
                # If ε ∈ FIRST(α), for each terminal 'b' in FOLLOW(A)
                if 'EPSILON' in first_of_alpha:
                    for terminal in self.analyzer.get_follow_set(non_terminal):
                        table_key = (non_terminal, terminal)
                        if table_key in self.parsing_table:
                            # Conflict detected
                            print(f"ERROR: LL(1) conflict at [{non_terminal}, {terminal}]")
                        self.parsing_table[table_key] = production
    
    def _compute_first_of_production(self, production: List[str]) -> Set[str]:
        """
        Compute FIRST(α) for a production α.
        
        Args:
            production: List of symbols (terminals and non-terminals)
            
        Returns:
            Set of terminals in FIRST(α)
        """
        if not production or production[0] == 'EPSILON':
            return {'EPSILON'}
        
        first_set = set()
        all_can_derive_epsilon = True
        
        for symbol in production:
            if self.analyzer._is_terminal(symbol):
                first_set.add(symbol)
                all_can_derive_epsilon = False
                break
            else:
                # Add FIRST of non-terminal (except EPSILON)
                first_of_symbol = self.analyzer.get_first_set(symbol) - {'EPSILON'}
                first_set.update(first_of_symbol)
                
                # If non-terminal can't derive epsilon, stop
                if 'EPSILON' not in self.analyzer.get_first_set(symbol):
                    all_can_derive_epsilon = False
                    break
        
        # If all symbols derive epsilon, add epsilon
        if all_can_derive_epsilon:
            first_set.add('EPSILON')
        
        return first_set
    
    def get_production(self, non_terminal: str, terminal: str) -> Optional[List[str]]:
        """
        Get the production for M[non_terminal, terminal]
        
        Returns:
            Production (list of symbols) or None if no entry
        """
        return self.parsing_table.get((non_terminal, terminal))
    
    def print_table(self) -> str:
        """Generate formatted output for parsing table"""
        output = "LL(1) Parsing Table\n"
        output += "=" * 100 + "\n\n"
        
        # Get all terminals and non-terminals
        non_terminals = sorted(self.grammar.keys())
        terminals = set()
        
        for nt in non_terminals:
            for productions in self.grammar[nt]:
                for prod in self.grammar[nt]:
                    terminals.update(prod)
        
        terminals = sorted([t for t in terminals if self.analyzer._is_terminal(t)])
        terminals.append('EOF')
        
        # Print table header
        output += f"{'Non-Terminal':<15}"
        for terminal in terminals:
            output += f" {terminal:<12}"
        output += "\n"
        output += "-" * 100 + "\n"
        
        # Print table rows
        for non_terminal in non_terminals:
            output += f"{non_terminal:<15}"
            for terminal in terminals:
                entry = self.parsing_table.get((non_terminal, terminal))
                if entry:
                    prod_str = ' '.join(entry)
                    if len(prod_str) > 12:
                        prod_str = prod_str[:9] + "..."
                    output += f" {prod_str:<12}"
                else:
                    output += f" {'-':<12}"
            output += "\n"
        
        return output
    
    def print_table_detailed(self) -> str:
        """Generate detailed output for parsing table"""
        output = "LL(1) Parsing Table (Detailed)\n"
        output += "=" * 100 + "\n\n"
        
        for (non_terminal, terminal), production in sorted(self.parsing_table.items()):
            prod_str = ' '.join(production)
            output += f"M[{non_terminal:<15}, {terminal:<10}] -> {prod_str}\n"
        
        return output


if __name__ == '__main__':
    from .first_follow import create_ll1_grammar
    
    # Test the table generator
    grammar = create_ll1_grammar()
    analyzer = GrammarAnalyzer(grammar)
    table_gen = ParsingTableGenerator(grammar, analyzer)
    
    print(table_gen.print_table_detailed())
