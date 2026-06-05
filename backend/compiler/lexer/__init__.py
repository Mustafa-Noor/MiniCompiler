"""
Lexical Analyzer Package for Mini Pascal Compiler
"""

from .token import Token, TokenType
from .keywords import is_keyword, PASCAL_KEYWORDS
from .buffer import Buffer
from .scanner import Scanner, LexicalError

__all__ = [
    'Token',
    'TokenType',
    'Scanner',
    'Buffer',
    'LexicalError',
    'is_keyword',
    'PASCAL_KEYWORDS',
]
