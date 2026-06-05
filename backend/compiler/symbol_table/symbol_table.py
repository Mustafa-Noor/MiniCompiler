"""
Symbol Table Implementation for Mini Pascal Compiler
Hash-table-based symbol table with nested scope support
"""

from typing import Dict, List, Optional, Tuple
from .symbol import Symbol, SymbolKind, DataType


class SymbolTable:
    """
    Hash-table-based symbol table with nested scope support.
    
    Features:
    - Hierarchical scoping with scope stack
    - Fast O(1) lookup using hash table
    - Automatic scope level tracking
    - Symbol shadowing support
    - Comprehensive query capabilities
    """
    
    def __init__(self):
        """Initialize the symbol table"""
        # Stack of scopes, each scope is a dict of symbols
        self.scope_stack: List[Dict[str, Symbol]] = [{}]  # Start with global scope
        self.current_scope_level = 0
    
    def enter_scope(self) -> None:
        """Enter a new nested scope (e.g., function body)"""
        self.scope_stack.append({})
        self.current_scope_level += 1
    
    def exit_scope(self) -> Dict[str, Symbol]:
        """
        Exit current scope and return symbols from exited scope.
        
        Returns:
            Dictionary of symbols in exited scope
        """
        if self.current_scope_level == 0:
            raise RuntimeError("Cannot exit global scope")
        
        exited_scope = self.scope_stack.pop()
        self.current_scope_level -= 1
        return exited_scope
    
    def insert(self, symbol: Symbol) -> bool:
        """
        Insert a symbol into the current scope.
        
        Args:
            symbol: Symbol to insert
            
        Returns:
            True if inserted, False if symbol already exists in this scope
        """
        if symbol.name in self.scope_stack[self.current_scope_level]:
            return False  # Symbol already exists in this scope
        
        self.scope_stack[self.current_scope_level][symbol.name] = symbol
        return True
    
    def insert_or_fail(self, symbol: Symbol) -> Symbol:
        """
        Insert a symbol or raise an error if it already exists in current scope.
        
        Args:
            symbol: Symbol to insert
            
        Returns:
            The inserted symbol
            
        Raises:
            RuntimeError: If symbol already exists in current scope
        """
        if not self.insert(symbol):
            existing = self.lookup_in_current_scope(symbol.name)
            raise RuntimeError(
                f"Symbol '{symbol.name}' already declared at "
                f"Line {existing.line_number}, Column {existing.column_number}"
            )
        return symbol
    
    def lookup(self, name: str) -> Optional[Symbol]:
        """
        Look up a symbol in the current and all parent scopes.
        
        Args:
            name: Symbol name
            
        Returns:
            Symbol if found, None otherwise
        """
        # Search from current scope backwards to global scope
        for scope in reversed(self.scope_stack):
            if name in scope:
                return scope[name]
        return None
    
    def lookup_in_current_scope(self, name: str) -> Optional[Symbol]:
        """
        Look up a symbol in only the current scope.
        
        Args:
            name: Symbol name
            
        Returns:
            Symbol if found in current scope, None otherwise
        """
        return self.scope_stack[self.current_scope_level].get(name)
    
    def lookup_in_scope(self, name: str, scope_level: int) -> Optional[Symbol]:
        """
        Look up a symbol in a specific scope level.
        
        Args:
            name: Symbol name
            scope_level: Scope level (0 = global)
            
        Returns:
            Symbol if found, None otherwise
        """
        if 0 <= scope_level < len(self.scope_stack):
            return self.scope_stack[scope_level].get(name)
        return None
    
    def is_declared(self, name: str) -> bool:
        """Check if symbol is declared in any scope"""
        return self.lookup(name) is not None
    
    def is_declared_in_current_scope(self, name: str) -> bool:
        """Check if symbol is declared in current scope"""
        return self.lookup_in_current_scope(name) is not None
    
    def get_symbols_in_scope(self, scope_level: int = None) -> List[Symbol]:
        """
        Get all symbols in a scope.
        
        Args:
            scope_level: Scope level (None = current scope)
            
        Returns:
            List of symbols in the specified scope
        """
        if scope_level is None:
            scope_level = self.current_scope_level
        
        if 0 <= scope_level < len(self.scope_stack):
            return list(self.scope_stack[scope_level].values())
        return []
    
    def get_symbols_by_kind(self, kind: SymbolKind, 
                           scope_level: int = None) -> List[Symbol]:
        """
        Get all symbols of a specific kind in a scope.
        
        Args:
            kind: Symbol kind to filter
            scope_level: Scope level (None = current scope)
            
        Returns:
            List of symbols matching the kind
        """
        symbols = self.get_symbols_in_scope(scope_level)
        return [s for s in symbols if s.kind == kind]
    
    def get_all_symbols(self) -> Dict[int, List[Symbol]]:
        """
        Get all symbols organized by scope level.
        
        Returns:
            Dictionary mapping scope level to list of symbols
        """
        result = {}
        for level, scope in enumerate(self.scope_stack):
            result[level] = list(scope.values())
        return result
    
    def delete_scope(self, scope_level: int) -> None:
        """
        Delete all symbols in a scope (typically on scope exit).
        
        Args:
            scope_level: Scope level to delete
        """
        if 0 <= scope_level < len(self.scope_stack):
            self.scope_stack[scope_level].clear()
    
    def get_scope_level(self) -> int:
        """Get current scope level"""
        return self.current_scope_level
    
    def get_depth(self) -> int:
        """Get total scope depth"""
        return len(self.scope_stack)
    
    def print_table(self) -> str:
        """Generate formatted symbol table dump"""
        output = "Symbol Table\n"
        output += "=" * 100 + "\n\n"
        
        for level, scope in enumerate(self.scope_stack):
            scope_name = "Global Scope" if level == 0 else f"Scope Level {level}"
            output += f"{scope_name}:\n"
            output += "-" * 100 + "\n"
            
            if not scope:
                output += "  (empty)\n"
            else:
                # Header
                output += f"{'Name':<20} {'Kind':<15} {'Type':<15} {'Line':<8} {'Col':<8} {'Attributes':<20}\n"
                output += "-" * 100 + "\n"
                
                # Sort by name
                for symbol in sorted(scope.values(), key=lambda s: s.name):
                    attr_str = str(symbol.attributes)[:20] if symbol.attributes else "-"
                    output += (f"{symbol.name:<20} {symbol.kind.value:<15} "
                             f"{symbol.data_type.value:<15} {symbol.line_number:<8} "
                             f"{symbol.column_number:<8} {attr_str:<20}\n")
            
            output += "\n"
        
        output += "=" * 100 + "\n"
        output += f"Total Scopes: {len(self.scope_stack)}\n"
        output += f"Total Symbols: {sum(len(scope) for scope in self.scope_stack)}\n"
        
        return output
    
    def print_symbols_by_kind(self) -> str:
        """Generate report of symbols organized by kind"""
        output = "Symbols by Kind\n"
        output += "=" * 80 + "\n\n"
        
        kinds = {}
        for level, scope in enumerate(self.scope_stack):
            for symbol in scope.values():
                kind = symbol.kind.value
                if kind not in kinds:
                    kinds[kind] = []
                kinds[kind].append((level, symbol))
        
        for kind in sorted(kinds.keys()):
            output += f"{kind.upper()}S ({len(kinds[kind])}):\n"
            output += "-" * 80 + "\n"
            for level, symbol in sorted(kinds[kind], key=lambda x: (x[0], x[1].name)):
                scope_name = "global" if level == 0 else f"scope {level}"
                output += f"  {symbol.name:<20} [{scope_name}] at Line {symbol.line_number}\n"
            output += "\n"
        
        return output
    
    def get_statistics(self) -> Dict[str, int]:
        """Get symbol table statistics"""
        stats = {
            'total_symbols': 0,
            'total_scopes': len(self.scope_stack),
            'variables': 0,
            'functions': 0,
            'procedures': 0,
            'arrays': 0,
            'parameters': 0,
        }
        
        for scope in self.scope_stack:
            for symbol in scope.values():
                stats['total_symbols'] += 1
                if symbol.kind == SymbolKind.VARIABLE:
                    stats['variables'] += 1
                elif symbol.kind == SymbolKind.FUNCTION:
                    stats['functions'] += 1
                elif symbol.kind == SymbolKind.PROCEDURE:
                    stats['procedures'] += 1
                elif symbol.kind == SymbolKind.ARRAY:
                    stats['arrays'] += 1
                elif symbol.kind == SymbolKind.PARAMETER:
                    stats['parameters'] += 1
        
        return stats
    
    def export_to_dict(self) -> Dict:
        """Export entire symbol table as dictionary"""
        result = {}
        for level, scope in enumerate(self.scope_stack):
            scope_name = f"level_{level}"
            result[scope_name] = {
                name: symbol.to_dict()
                for name, symbol in scope.items()
            }
        return result


class ScopedSymbolTable:
    """
    High-level interface for scoped symbol table operations.
    Provides convenient methods for common operations.
    """
    
    def __init__(self):
        """Initialize scoped symbol table"""
        self.table = SymbolTable()
    
    def declare_variable(self, name: str, var_type: DataType,
                        line: int, column: int) -> Symbol:
        """Declare a variable"""
        symbol = Symbol(name, SymbolKind.VARIABLE, var_type, 
                       self.table.get_scope_level(), line, column)
        return self.table.insert_or_fail(symbol)
    
    def declare_function(self, name: str, return_type: DataType,
                        line: int, column: int) -> Symbol:
        """Declare a function"""
        symbol = Symbol(name, SymbolKind.FUNCTION, return_type,
                       self.table.get_scope_level(), line, column)
        return self.table.insert_or_fail(symbol)
    
    def declare_procedure(self, name: str, line: int, column: int) -> Symbol:
        """Declare a procedure"""
        symbol = Symbol(name, SymbolKind.PROCEDURE, DataType.UNDEFINED,
                       self.table.get_scope_level(), line, column)
        return self.table.insert_or_fail(symbol)
    
    def declare_array(self, name: str, element_type: DataType,
                     lower: int, upper: int,
                     line: int, column: int) -> Symbol:
        """Declare an array"""
        symbol = Symbol(name, SymbolKind.ARRAY, element_type,
                       self.table.get_scope_level(), line, column)
        symbol.set_array_info(element_type, lower, upper)
        return self.table.insert_or_fail(symbol)
    
    def lookup(self, name: str) -> Optional[Symbol]:
        """Look up a symbol"""
        return self.table.lookup(name)
    
    def enter_scope(self) -> None:
        """Enter a new scope"""
        self.table.enter_scope()
    
    def exit_scope(self) -> Dict[str, Symbol]:
        """Exit current scope"""
        return self.table.exit_scope()
    
    def get_symbols(self) -> Dict[int, List[Symbol]]:
        """Get all symbols by scope"""
        return self.table.get_all_symbols()
    
    def print_table(self) -> str:
        """Print symbol table"""
        return self.table.print_table()


if __name__ == '__main__':
    # Example usage
    st = ScopedSymbolTable()
    
    # Global declarations
    x = st.declare_variable("x", DataType.INTEGER, 1, 5)
    print(f"Declared: {x}")
    
    # Declare function
    gcd_func = st.declare_function("gcd", DataType.INTEGER, 5, 1)
    gcd_func.add_parameter("a", DataType.INTEGER)
    gcd_func.add_parameter("b", DataType.INTEGER)
    print(f"Declared: {gcd_func}")
    
    # Enter function scope
    st.enter_scope()
    param_a = st.declare_variable("a", DataType.INTEGER, 5, 15)
    param_b = st.declare_variable("b", DataType.INTEGER, 5, 20)
    print(f"Declared in function: {param_a}, {param_b}")
    
    # Look up variable
    found = st.lookup("x")
    print(f"Lookup 'x': {found}")
    
    # Exit function scope
    st.exit_scope()
    
    # Print table
    print(st.print_table())
    
    # Statistics
    stats = st.table.get_statistics()
    print(f"Statistics: {stats}")
