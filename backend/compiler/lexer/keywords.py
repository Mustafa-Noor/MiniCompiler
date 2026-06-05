"""
Pascal Keywords Definition
Defines all reserved keywords for the Mini Pascal Compiler
Following the Pascal subset from Appendix A of the Dragon Book
"""

# Pascal reserved keywords (case-insensitive)
PASCAL_KEYWORDS = {
    'program': 'KEYWORD_PROGRAM',
    'var': 'KEYWORD_VAR',
    'integer': 'KEYWORD_INTEGER',
    'real': 'KEYWORD_REAL',
    'array': 'KEYWORD_ARRAY',
    'of': 'KEYWORD_OF',
    'function': 'KEYWORD_FUNCTION',
    'procedure': 'KEYWORD_PROCEDURE',
    'begin': 'KEYWORD_BEGIN',
    'end': 'KEYWORD_END',
    'if': 'KEYWORD_IF',
    'then': 'KEYWORD_THEN',
    'else': 'KEYWORD_ELSE',
    'while': 'KEYWORD_WHILE',
    'do': 'KEYWORD_DO',
    'not': 'KEYWORD_NOT',
    'div': 'KEYWORD_DIV',
    'mod': 'KEYWORD_MOD',
    'and': 'KEYWORD_AND',
    'or': 'KEYWORD_OR',
}

def is_keyword(word):
    """
    Check if a word is a Pascal keyword (case-insensitive)
    
    Args:
        word (str): The word to check
        
    Returns:
        tuple: (True, token_type) if keyword, (False, None) otherwise
    """
    word_lower = word.lower()
    if word_lower in PASCAL_KEYWORDS:
        return True, PASCAL_KEYWORDS[word_lower]
    return False, None
