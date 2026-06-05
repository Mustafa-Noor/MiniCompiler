"""
Token Class Definition
Represents a single token in the Mini Pascal language
"""

class Token:
    """
    Represents a lexical token in Mini Pascal
    
    Attributes:
        token_type (str): Type of token (e.g., 'KEYWORD', 'ID', 'NUMBER', etc.)
        lexeme (str): The actual text of the token
        line (int): Line number where token appears
        column (int): Column number where token begins
    """
    
    def __init__(self, token_type, lexeme, line, column):
        """
        Initialize a Token
        
        Args:
            token_type (str): Type of token
            lexeme (str): The actual text
            line (int): Line number (1-based)
            column (int): Column number (1-based)
        """
        self.token_type = token_type
        self.lexeme = lexeme
        self.line = line
        self.column = column
    
    def __repr__(self):
        """Return a string representation of the token"""
        return f"({self.token_type}, \"{self.lexeme}\", {self.line}, {self.column})"
    
    def __str__(self):
        """Return a formatted string representation"""
        return self.__repr__()
    
    def to_tuple(self):
        """Return token as a tuple"""
        return (self.token_type, self.lexeme, self.line, self.column)
    
    def to_dict(self):
        """Return token as a dictionary"""
        return {
            'type': self.token_type,
            'lexeme': self.lexeme,
            'line': self.line,
            'column': self.column
        }


# Token type constants
class TokenType:
    """Token type constants"""
    
    # Keywords
    KEYWORD = 'KEYWORD'
    
    # Identifiers and Numbers
    ID = 'ID'
    NUMBER = 'NUMBER'
    
    # Operators
    PLUS = 'PLUS'
    MINUS = 'MINUS'
    MULTIPLY = 'MULTIPLY'
    DIVIDE = 'DIVIDE'
    INT_DIV = 'INT_DIV'
    MOD = 'MOD'
    ASSIGN = 'ASSIGN'
    EQ = 'EQ'
    NEQ = 'NEQ'
    LT = 'LT'
    LE = 'LE'
    GT = 'GT'
    GE = 'GE'
    AND = 'AND'
    OR = 'OR'
    NOT = 'NOT'
    
    # Punctuation
    LPAREN = 'LPAREN'
    RPAREN = 'RPAREN'
    LBRACKET = 'LBRACKET'
    RBRACKET = 'RBRACKET'
    SEMICOLON = 'SEMICOLON'
    COLON = 'COLON'
    COMMA = 'COMMA'
    DOT = 'DOT'
    DOUBLE_DOT = 'DOUBLE_DOT'
    
    # Special
    EOF = 'EOF'
    NEWLINE = 'NEWLINE'
