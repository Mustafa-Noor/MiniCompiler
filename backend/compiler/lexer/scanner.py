"""
Lexical Scanner (Lexer) for Mini Pascal Compiler
Main lexical analysis module implementing token recognition
"""

import re
from .token import Token, TokenType
from .keywords import is_keyword
from .buffer import Buffer


class LexicalError(Exception):
    """Exception for lexical errors with source location."""

    def __init__(self, message: str, line: int = 1, column: int = 1, lexeme: str = ""):
        super().__init__(message)
        self.line = line
        self.column = column
        self.lexeme = lexeme


class Scanner:
    """
    Lexical Scanner for Mini Pascal Compiler
    
    Reads source code and produces a stream of tokens.
    Handles:
    - Keywords and identifiers
    - Numbers (integers, reals, scientific notation)
    - Operators and punctuation
    - Comments
    - Whitespace and line tracking
    
    Attributes:
        buffer (Buffer): Double buffer for source input
        current_char (str): Current character being processed
        tokens (list): List of scanned tokens
        errors (list): List of lexical errors encountered
    """
    
    def __init__(self, source_file):
        """
        Initialize the scanner
        
        Args:
            source_file (str): Path to source code file
        """
        self.buffer = Buffer(source_file)
        self.current_char = self.buffer.get_char()
        self.tokens = []
        self.errors = []
    
    def skip_whitespace(self):
        """Skip spaces and tabs (not newlines)"""
        while self.current_char in (' ', '\t'):
            self.current_char = self.buffer.get_char()
    
    def skip_newline(self):
        """Skip newline character"""
        if self.current_char == '\n':
            self.current_char = self.buffer.get_char()
    
    def skip_comment(self):
        """
        Skip Pascal comments { ... }
        
        Raises:
            LexicalError: If comment is not properly closed
        """
        if self.current_char == '{':
            self.current_char = self.buffer.get_char()
            while self.current_char != '}' and self.current_char != '\0':
                self.current_char = self.buffer.get_char()
            
            if self.current_char == '\0':
                line = self.buffer.get_current_line()
                raise LexicalError(
                    "Unterminated comment",
                    line=line,
                    column=self.buffer.get_current_column(),
                )
            # Skip the closing '}'
            self.current_char = self.buffer.get_char()
    
    def read_number(self):
        """
        Read a number (integer, real, or scientific notation)
        
        Formats supported:
        - 123 (integer)
        - 45.67 (real)
        - 1E10 (scientific)
        - 1.2E-5 (scientific with decimal)
        
        Returns:
            str: The number string
        """
        num_str = ''
        
        # Read integer part
        while self.current_char.isdigit():
            num_str += self.current_char
            self.current_char = self.buffer.get_char()
        
        # Check for decimal point and fractional part
        if self.current_char == '.' and self.buffer.peek_char().isdigit():
            num_str += self.current_char
            self.current_char = self.buffer.get_char()
            while self.current_char.isdigit():
                num_str += self.current_char
                self.current_char = self.buffer.get_char()
        
        # Check for scientific notation
        if self.current_char in ('E', 'e'):
            num_str += self.current_char
            self.current_char = self.buffer.get_char()
            
            # Optional sign
            if self.current_char in ('+', '-'):
                num_str += self.current_char
                self.current_char = self.buffer.get_char()
            
            # Exponent digits
            if not self.current_char.isdigit():
                raise LexicalError(
                    "Invalid scientific notation",
                    line=self.buffer.get_current_line(),
                    column=self.buffer.get_current_column(),
                )
            while self.current_char.isdigit():
                num_str += self.current_char
                self.current_char = self.buffer.get_char()
        
        return num_str
    
    def read_identifier(self):
        """
        Read an identifier or keyword
        
        Format: [a-zA-Z][a-zA-Z0-9]*
        
        Returns:
            str: The identifier string
        """
        ident = ''
        while self.current_char.isalnum() or self.current_char == '_':
            ident += self.current_char
            self.current_char = self.buffer.get_char()
        return ident
    
    def get_next_token(self):
        """
        Get the next token from the source
        
        Returns:
            Token: The next token, or EOF token if at end of file
            
        Raises:
            LexicalError: If an invalid character is encountered
        """
        while True:
            # Skip whitespace and comments
            self.skip_whitespace()
            
            if self.current_char == '{':
                self.skip_comment()
                continue
            
            if self.current_char == '\n':
                self.skip_newline()
                continue
            
            break
        
        # Record token position
        line = self.buffer.get_current_line()
        column = self.buffer.get_current_column()
        
        # End of file
        if self.current_char == '\0':
            return Token(TokenType.EOF, 'EOF', line, column)
        
        # Numbers
        if self.current_char.isdigit():
            num = self.read_number()
            return Token(TokenType.NUMBER, num, line, column)
        
        # Identifiers and keywords
        if self.current_char.isalpha() or self.current_char == '_':
            ident = self.read_identifier()
            is_kw, token_type = is_keyword(ident)
            if is_kw:
                return Token(token_type, ident, line, column)
            return Token(TokenType.ID, ident, line, column)
        
        # Operators and punctuation
        char = self.current_char
        self.current_char = self.buffer.get_char()
        
        # Two-character operators
        if char == ':' and self.current_char == '=':
            self.current_char = self.buffer.get_char()
            return Token(TokenType.ASSIGN, ':=', line, column)
        elif char == '<' and self.current_char == '=':
            self.current_char = self.buffer.get_char()
            return Token(TokenType.LE, '<=', line, column)
        elif char == '<' and self.current_char == '>':
            self.current_char = self.buffer.get_char()
            return Token(TokenType.NEQ, '<>', line, column)
        elif char == '>' and self.current_char == '=':
            self.current_char = self.buffer.get_char()
            return Token(TokenType.GE, '>=', line, column)
        elif char == '.' and self.current_char == '.':
            self.current_char = self.buffer.get_char()
            return Token(TokenType.DOUBLE_DOT, '..', line, column)
        
        # Single-character operators and punctuation
        single_char_tokens = {
            '+': TokenType.PLUS,
            '-': TokenType.MINUS,
            '*': TokenType.MULTIPLY,
            '/': TokenType.DIVIDE,
            '=': TokenType.EQ,
            '<': TokenType.LT,
            '>': TokenType.GT,
            '(': TokenType.LPAREN,
            ')': TokenType.RPAREN,
            '[': TokenType.LBRACKET,
            ']': TokenType.RBRACKET,
            ';': TokenType.SEMICOLON,
            ':': TokenType.COLON,
            ',': TokenType.COMMA,
            '.': TokenType.DOT,
        }
        
        if char in single_char_tokens:
            return Token(single_char_tokens[char], char, line, column)
        
        # Invalid character
        raise LexicalError(
            f"Invalid character '{char}'",
            line=line,
            column=column,
            lexeme=char,
        )
    
    def scan(self):
        """
        Scan the entire source file and return all tokens
        
        Returns:
            list: List of Token objects
            
        Raises:
            LexicalError: If any lexical error is encountered
        """
        tokens = []
        try:
            while True:
                token = self.get_next_token()
                tokens.append(token)
                if token.token_type == TokenType.EOF:
                    break
        except LexicalError as e:
            self.errors.append(str(e))
            raise
        
        self.tokens = tokens
        return tokens
    
    def close(self):
        """Close the scanner and release resources"""
        self.buffer.close()
    
    def get_errors(self):
        """
        Get list of errors encountered during scanning
        
        Returns:
            list: List of error messages
        """
        return self.errors
    
    def __del__(self):
        """Destructor"""
        self.close()
