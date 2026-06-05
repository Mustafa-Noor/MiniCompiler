"""
Error Handler for Mini Pascal Compiler
Manages lexical, syntax, and semantic errors with comprehensive reporting
"""

from typing import List, Dict, Tuple, Optional
from enum import Enum


class ErrorType(Enum):
    """Classification of compiler errors"""
    LEXICAL = "Lexical Error"
    SYNTAX = "Syntax Error"
    SEMANTIC = "Semantic Error"
    TYPE_ERROR = "Type Error"
    SCOPE_ERROR = "Scope Error"


class CompilerError:
    """
    Represents a single compiler error with location and context information.
    
    Attributes:
        error_type (ErrorType): Classification of error
        line (int): Line number where error occurred
        column (int): Column number where error occurred
        message (str): Detailed error message
        lexeme (str): The problematic token/lexeme
        context (str): Additional context information
    """
    
    def __init__(self, error_type: ErrorType, line: int, column: int, 
                 message: str, lexeme: str = "", context: str = ""):
        """
        Initialize a compiler error.
        
        Args:
            error_type: Classification of error
            line: Line number (1-based)
            column: Column number (1-based)
            message: Error description
            lexeme: The problematic token
            context: Additional context
        """
        self.error_type = error_type
        self.line = line
        self.column = column
        self.message = message
        self.lexeme = lexeme
        self.context = context
    
    def __str__(self) -> str:
        """Return formatted error message"""
        lexeme_part = f" ('{self.lexeme}')" if self.lexeme else ""
        context_part = f" - {self.context}" if self.context else ""
        return f"{self.error_type.value} at Line {self.line}, Column {self.column}: {self.message}{lexeme_part}{context_part}"
    
    def to_dict(self) -> Dict:
        """Convert error to dictionary"""
        return {
            'type': self.error_type.value,
            'line': self.line,
            'column': self.column,
            'message': self.message,
            'lexeme': self.lexeme,
            'context': self.context
        }


class ErrorHandler:
    """
    Central error management system for the compiler.
    
    Features:
    - Collects and categorizes errors
    - Provides panic-mode recovery
    - Generates comprehensive error reports
    - Tracks error statistics
    """
    
    def __init__(self):
        """Initialize the error handler"""
        self.errors: List[CompilerError] = []
        self.error_limit = 100  # Maximum errors before stopping
        self.current_line = 1
        self.current_column = 1
    
    def add_error(self, error_type: ErrorType, line: int, column: int,
                  message: str, lexeme: str = "", context: str = "") -> None:
        """
        Add an error to the error list.
        
        Args:
            error_type: Type of error
            line: Line number
            column: Column number
            message: Error message
            lexeme: Problematic token
            context: Additional context
        """
        error = CompilerError(error_type, line, column, message, lexeme, context)
        self.errors.append(error)
        
        if len(self.errors) >= self.error_limit:
            self.add_error(ErrorType.LEXICAL, line, column,
                         f"Too many errors (limit: {self.error_limit}). Compilation halted.")
    
    def add_lexical_error(self, line: int, column: int, message: str, 
                         lexeme: str = "") -> None:
        """Add a lexical error"""
        self.add_error(ErrorType.LEXICAL, line, column, message, lexeme)
    
    def add_syntax_error(self, line: int, column: int, message: str,
                        expected: str = "", found: str = "") -> None:
        """
        Add a syntax error.
        
        Args:
            line: Line number
            column: Column number
            message: Error message
            expected: Expected token
            found: Found token
        """
        context = ""
        if expected and found:
            context = f"Expected {expected}, found {found}"
        self.add_error(ErrorType.SYNTAX, line, column, message, context=context)
    
    def add_semantic_error(self, line: int, column: int, message: str,
                          identifier: str = "", error_kind: str = "") -> None:
        """
        Add a semantic error.
        
        Args:
            line: Line number
            column: Column number
            message: Error message
            identifier: The problematic identifier
            error_kind: Kind of semantic error
        """
        context = error_kind if error_kind else ""
        self.add_error(ErrorType.SEMANTIC, line, column, message, identifier, context)
    
    def add_type_error(self, line: int, column: int, message: str,
                      expected_type: str = "", actual_type: str = "") -> None:
        """
        Add a type error.
        
        Args:
            line: Line number
            column: Column number
            message: Error message
            expected_type: Expected type
            actual_type: Actual type
        """
        context = ""
        if expected_type and actual_type:
            context = f"Expected {expected_type}, got {actual_type}"
        self.add_error(ErrorType.TYPE_ERROR, line, column, message, context=context)
    
    def add_scope_error(self, line: int, column: int, message: str,
                       identifier: str = "") -> None:
        """
        Add a scope error.
        
        Args:
            line: Line number
            column: Column number
            message: Error message
            identifier: The problematic identifier
        """
        self.add_error(ErrorType.SCOPE_ERROR, line, column, message, identifier)
    
    def has_errors(self) -> bool:
        """Check if any errors were recorded"""
        return len(self.errors) > 0
    
    def has_critical_errors(self) -> bool:
        """Check if critical errors (syntax) were recorded"""
        return any(e.error_type == ErrorType.SYNTAX for e in self.errors)
    
    def get_error_count(self) -> int:
        """Get total number of errors"""
        return len(self.errors)
    
    def get_error_count_by_type(self) -> Dict[str, int]:
        """Get error count by type"""
        counts = {}
        for error in self.errors:
            error_type = error.error_type.value
            counts[error_type] = counts.get(error_type, 0) + 1
        return counts
    
    def get_errors(self) -> List[CompilerError]:
        """Get all errors"""
        return self.errors
    
    def get_errors_by_type(self, error_type: ErrorType) -> List[CompilerError]:
        """Get errors of a specific type"""
        return [e for e in self.errors if e.error_type == error_type]
    
    def clear(self) -> None:
        """Clear all errors"""
        self.errors = []
    
    def print_errors(self) -> str:
        """Generate formatted error report"""
        if not self.errors:
            return "No errors found.\n"
        
        output = f"Compilation Report\n"
        output += "=" * 80 + "\n\n"
        
        # Group errors by line
        errors_by_line = {}
        for error in self.errors:
            line = error.line
            if line not in errors_by_line:
                errors_by_line[line] = []
            errors_by_line[line].append(error)
        
        # Print errors grouped by line
        for line in sorted(errors_by_line.keys()):
            for error in errors_by_line[line]:
                output += str(error) + "\n"
        
        # Summary statistics
        output += "\n" + "=" * 80 + "\n"
        output += f"Total Errors: {self.get_error_count()}\n"
        
        error_counts = self.get_error_count_by_type()
        for error_type, count in sorted(error_counts.items()):
            output += f"  {error_type}: {count}\n"
        
        output += "=" * 80 + "\n"
        
        return output
    
    def export_errors(self) -> List[Dict]:
        """Export errors as list of dictionaries"""
        return [error.to_dict() for error in self.errors]


class RecoveryStrategy:
    """
    Implements error recovery strategies for different parser types.
    """
    
    @staticmethod
    def panic_mode_recovery(error_handler: ErrorHandler, current_token, 
                           follow_set: set) -> None:
        """
        Panic-mode recovery: Skip tokens until reaching a token in FOLLOW set.
        Used for LL(1) parsers.
        
        Args:
            error_handler: Error handler instance
            current_token: Current token
            follow_set: Set of tokens that can follow
        """
        while current_token not in follow_set and current_token.token_type != 'EOF':
            # Skip token
            pass
    
    @staticmethod
    def shift_reduce_recovery(error_handler: ErrorHandler, state_stack: List[int],
                             symbol_stack: List[str], input_symbol: str) -> bool:
        """
        Shift-reduce recovery: Try to recover from error state.
        Used for LR parsers.
        
        Args:
            error_handler: Error handler instance
            state_stack: Current state stack
            symbol_stack: Current symbol stack
            input_symbol: Current input symbol
            
        Returns:
            True if recovery successful, False otherwise
        """
        # Try to pop states/symbols until we can make progress
        while state_stack:
            # Try to find a state that can process current symbol
            # This is simplified; actual implementation would check parse table
            state_stack.pop()
            if symbol_stack:
                symbol_stack.pop()
        
        return False


class CompilationStatus:
    """
    Represents the overall compilation status.
    """
    
    def __init__(self, error_handler: ErrorHandler):
        """
        Initialize compilation status.
        
        Args:
            error_handler: Error handler instance
        """
        self.error_handler = error_handler
    
    def is_success(self) -> bool:
        """Check if compilation succeeded"""
        return not self.error_handler.has_critical_errors()
    
    def get_status(self) -> str:
        """Get compilation status summary"""
        if self.is_success():
            warning_count = len(self.error_handler.get_errors_by_type(ErrorType.SEMANTIC))
            if warning_count == 0:
                return "Compilation successful with no errors"
            else:
                return f"Compilation successful with {warning_count} warning(s)"
        else:
            error_count = self.error_handler.get_error_count()
            return f"Compilation failed with {error_count} error(s)"


if __name__ == '__main__':
    # Example usage
    error_handler = ErrorHandler()
    
    # Add various types of errors
    error_handler.add_lexical_error(1, 5, "Illegal character", "@")
    error_handler.add_syntax_error(5, 10, "Unexpected token", "SEMICOLON", "LPAREN")
    error_handler.add_semantic_error(10, 3, "Undeclared identifier", "foo")
    error_handler.add_type_error(15, 7, "Type mismatch in assignment", "integer", "real")
    
    # Print errors
    print(error_handler.print_errors())
    
    # Export errors
    errors_json = error_handler.export_errors()
    print("Exported errors:", errors_json)
