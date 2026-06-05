"""
Semantic Analyzer for Mini Pascal Compiler
Performs semantic checking and type analysis
"""

from typing import Optional
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from error_handler.error_handler import ErrorHandler, ErrorType
from symbol_table.symbol_table import ScopedSymbolTable
from symbol_table.symbol import SymbolKind, DataType


class SemanticAnalyzer:
    """
    Semantic analyzer for Mini Pascal.
    
    Performs:
    - Scope analysis
    - Type checking
    - Declaration verification
    - Function/procedure correctness checking
    """
    
    def __init__(self, error_handler: ErrorHandler):
        """
        Initialize semantic analyzer.
        
        Args:
            error_handler: Error handler for reporting errors
        """
        self.error_handler = error_handler
        self.symbol_table = ScopedSymbolTable()
    
    def check_identifier_declared(self, name: str, line: int, column: int) -> bool:
        """
        Check if identifier is declared.
        
        Args:
            name: Identifier name
            line: Line number
            column: Column number
            
        Returns:
            True if declared, False otherwise
        """
        symbol = self.symbol_table.lookup(name)
        
        if symbol is None:
            self.error_handler.add_semantic_error(
                line, column,
                f"Undeclared identifier: {name}",
                name,
                "Undeclared identifier"
            )
            return False
        
        return True
    
    def check_duplicate_declaration(self, name: str, line: int, 
                                   column: int) -> bool:
        """
        Check if identifier is already declared in current scope.
        
        Args:
            name: Identifier name
            line: Line number
            column: Column number
            
        Returns:
            True if not duplicate, False if duplicate
        """
        if self.symbol_table.table.is_declared_in_current_scope(name):
            existing = self.symbol_table.table.lookup_in_current_scope(name)
            self.error_handler.add_semantic_error(
                line, column,
                f"Duplicate declaration of identifier: {name}",
                name,
                "Duplicate declaration"
            )
            return False
        
        return True
    
    def check_variable_access(self, name: str, line: int, column: int) -> bool:
        """
        Check if variable is accessible.
        
        Args:
            name: Variable name
            line: Line number
            column: Column number
            
        Returns:
            True if accessible, False otherwise
        """
        symbol = self.symbol_table.lookup(name)
        
        if symbol is None:
            self.error_handler.add_semantic_error(
                line, column,
                f"Variable '{name}' not declared",
                name,
                "Undefined variable"
            )
            return False
        
        if symbol.kind not in (SymbolKind.VARIABLE, SymbolKind.PARAMETER,
                              SymbolKind.ARRAY):
            self.error_handler.add_semantic_error(
                line, column,
                f"'{name}' is not a variable",
                name,
                "Invalid variable access"
            )
            return False
        
        return True
    
    def check_function_call(self, name: str, arg_count: int,
                           line: int, column: int) -> bool:
        """
        Check if function can be called.
        
        Args:
            name: Function name
            arg_count: Number of arguments provided
            line: Line number
            column: Column number
            
        Returns:
            True if valid, False otherwise
        """
        symbol = self.symbol_table.lookup(name)
        
        if symbol is None:
            self.error_handler.add_semantic_error(
                line, column,
                f"Function '{name}' not declared",
                name,
                "Undefined function"
            )
            return False
        
        if symbol.kind != SymbolKind.FUNCTION:
            self.error_handler.add_semantic_error(
                line, column,
                f"'{name}' is not a function",
                name,
                "Invalid function call"
            )
            return False
        
        # Check parameter count
        expected_count = len(symbol.get_parameters())
        if arg_count != expected_count:
            self.error_handler.add_semantic_error(
                line, column,
                f"Function '{name}' expects {expected_count} arguments, "
                f"got {arg_count}",
                name,
                "Argument count mismatch"
            )
            return False
        
        return True
    
    def check_procedure_call(self, name: str, line: int, column: int) -> bool:
        """
        Check if procedure can be called.
        
        Args:
            name: Procedure name
            line: Line number
            column: Column number
            
        Returns:
            True if valid, False otherwise
        """
        symbol = self.symbol_table.lookup(name)
        
        if symbol is None:
            self.error_handler.add_semantic_error(
                line, column,
                f"Procedure '{name}' not declared",
                name,
                "Undefined procedure"
            )
            return False
        
        if symbol.kind != SymbolKind.PROCEDURE:
            self.error_handler.add_semantic_error(
                line, column,
                f"'{name}' is not a procedure",
                name,
                "Invalid procedure call"
            )
            return False
        
        return True
    
    def check_array_access(self, name: str, line: int, column: int) -> bool:
        """
        Check if array is accessible.
        
        Args:
            name: Array name
            line: Line number
            column: Column number
            
        Returns:
            True if valid, False otherwise
        """
        symbol = self.symbol_table.lookup(name)
        
        if symbol is None:
            self.error_handler.add_semantic_error(
                line, column,
                f"Array '{name}' not declared",
                name,
                "Undefined array"
            )
            return False
        
        if symbol.kind != SymbolKind.ARRAY:
            self.error_handler.add_semantic_error(
                line, column,
                f"'{name}' is not an array",
                name,
                "Invalid array access"
            )
            return False
        
        return True
    
    def check_type_compatibility(self, actual_type: DataType,
                                expected_type: DataType,
                                line: int, column: int) -> bool:
        """
        Check if types are compatible.
        
        Args:
            actual_type: Actual type
            expected_type: Expected type
            line: Line number
            column: Column number
            
        Returns:
            True if compatible, False otherwise
        """
        # Allow exact match
        if actual_type == expected_type:
            return True
        
        # Allow integer to real conversion
        if expected_type == DataType.REAL and actual_type == DataType.INTEGER:
            return True
        
        # Otherwise incompatible
        self.error_handler.add_type_error(
            line, column,
            f"Type mismatch in expression",
            expected_type.value,
            actual_type.value
        )
        return False
    
    def declare_variable(self, name: str, var_type: DataType,
                        line: int, column: int) -> bool:
        """
        Declare a variable.
        
        Args:
            name: Variable name
            var_type: Variable type
            line: Line number
            column: Column number
            
        Returns:
            True if successful, False if duplicate
        """
        if not self.check_duplicate_declaration(name, line, column):
            return False
        
        try:
            self.symbol_table.declare_variable(name, var_type, line, column)
            return True
        except RuntimeError as e:
            self.error_handler.add_semantic_error(line, column, str(e), name)
            return False
    
    def declare_function(self, name: str, return_type: DataType,
                        line: int, column: int) -> bool:
        """
        Declare a function.
        
        Args:
            name: Function name
            return_type: Return type
            line: Line number
            column: Column number
            
        Returns:
            True if successful, False if duplicate
        """
        if not self.check_duplicate_declaration(name, line, column):
            return False
        
        try:
            self.symbol_table.declare_function(name, return_type, line, column)
            return True
        except RuntimeError as e:
            self.error_handler.add_semantic_error(line, column, str(e), name)
            return False
    
    def declare_procedure(self, name: str, line: int, column: int) -> bool:
        """
        Declare a procedure.
        
        Args:
            name: Procedure name
            line: Line number
            column: Column number
            
        Returns:
            True if successful, False if duplicate
        """
        if not self.check_duplicate_declaration(name, line, column):
            return False
        
        try:
            self.symbol_table.declare_procedure(name, line, column)
            return True
        except RuntimeError as e:
            self.error_handler.add_semantic_error(line, column, str(e), name)
            return False
    
    def enter_scope(self) -> None:
        """Enter a new scope"""
        self.symbol_table.enter_scope()
    
    def exit_scope(self) -> None:
        """Exit current scope"""
        self.symbol_table.exit_scope()
    
    def get_symbol_table_dump(self) -> str:
        """Get symbol table dump"""
        return self.symbol_table.print_table()


if __name__ == '__main__':
    from error_handler import ErrorHandler
    
    # Example usage
    error_handler = ErrorHandler()
    analyzer = SemanticAnalyzer(error_handler)
    
    # Declare variable
    analyzer.declare_variable("x", DataType.INTEGER, 1, 5)
    print("Declared x as integer")
    
    # Try duplicate declaration
    analyzer.declare_variable("x", DataType.REAL, 2, 5)
    print("Attempted duplicate declaration of x")
    
    # Check variable access
    analyzer.check_variable_access("x", 5, 10)
    print("x is declared")
    
    # Check undeclared
    analyzer.check_variable_access("y", 10, 5)
    print("y is not declared")
    
    # Print errors
    print("\nErrors:")
    print(error_handler.print_errors())
