# Mini Pascal Lexical Analyzer

## Overview

A complete **Lexical Analyzer (Scanner)** module for a Mini Pascal Compiler written in Python. This implementation follows the Pascal subset defined in **Appendix A of the Dragon Book** (Compilers: Principles, Techniques and Tools).

## Features

✓ **Double Buffering**: Efficient input handling with two buffers and forward/lexemeBegin pointers  
✓ **Line & Column Tracking**: Maintains position information for error reporting  
✓ **Token Recognition**: Keywords, identifiers, numbers, operators, and punctuation  
✓ **Comment Handling**: Pascal-style comments `{ ... }`  
✓ **Error Reporting**: Detailed lexical error messages with line/column information  
✓ **Modular Design**: Reusable components for parser integration  
✓ **Comprehensive Testing**: Full test suite covering all token types  

## Project Structure

```
FinalProject/
├── src/
│   ├── __init__.py
│   └── lexer/
│       ├── __init__.py          # Package exports
│       ├── token.py              # Token class and types
│       ├── keywords.py           # Pascal keywords definition
│       ├── buffer.py             # Double buffering implementation
│       └── scanner.py            # Main lexical analyzer
├── main.py                       # Driver script
├── test_lexer.py                 # Comprehensive test suite
├── README.md                     # This file
└── output/
    └── tokens.txt               # Generated token stream
```

## Module Documentation

### 1. `token.py` - Token Representation

Defines the `Token` class and `TokenType` constants.

```python
class Token:
    def __init__(self, token_type, lexeme, line, column)
    def to_tuple()          # Returns (type, lexeme, line, column)
    def to_dict()           # Returns dictionary representation
```

**Token Types:**
- Keywords: `KEYWORD_PROGRAM`, `KEYWORD_VAR`, etc.
- Identifiers: `ID`
- Numbers: `NUMBER`
- Operators: `PLUS`, `MINUS`, `MULTIPLY`, `DIVIDE`, `ASSIGN`, etc.
- Punctuation: `LPAREN`, `RPAREN`, `SEMICOLON`, etc.

### 2. `keywords.py` - Keyword Recognition

```python
PASCAL_KEYWORDS = {
    'program': 'KEYWORD_PROGRAM',
    'var': 'KEYWORD_VAR',
    # ... all 20 keywords
}

is_keyword(word) -> (bool, token_type)
```

### 3. `buffer.py` - Double Buffering

Implements efficient input buffering with two buffers:

```python
class Buffer:
    def __init__(source_file, buffer_size=1024)
    def get_char()              # Get next character
    def peek_char()             # Look ahead one character
    def get_lexeme()            # Get current lexeme
    def mark_lexeme_begin()     # Mark token start
    def get_current_line()
    def get_current_column()
```

**Buffer Management:**
- Automatically switches between buffers when one is exhausted
- Reloads buffers from file as needed
- Tracks line and column numbers during character consumption

### 4. `scanner.py` - Main Lexical Analyzer

```python
class Scanner:
    def __init__(source_file)
    def get_next_token() -> Token           # Get one token
    def scan() -> list[Token]               # Scan entire file
    def get_errors() -> list[str]
```

**Methods:**
- `skip_whitespace()`: Skips spaces and tabs
- `skip_newline()`: Handles newline characters
- `skip_comment()`: Processes Pascal comments
- `read_number()`: Parses integers, reals, scientific notation
- `read_identifier()`: Parses identifiers and keywords

## Supported Pascal Subset

### Keywords (20 total)
```
program  var  integer  real  array  of  function  procedure
begin  end  if  then  else  while  do  not  div  mod  and  or
```

### Data Types
- `integer`
- `real`
- `array [low..high] of type`

### Identifiers
```
Format: [a-zA-Z][a-zA-Z0-9_]*
Examples: x, myVar, _internal, variable123
```

### Numbers
```
Integer:        123, 0, 999
Real:           45.67, 0.5, 3.14159
Scientific:     1E10, 1.5E-5, 2.0E+3
```

### Operators
```
Arithmetic:     +  -  *  /  div  mod
Comparison:     =  <>  <  <=  >  >=
Logical:        and  or  not
Assignment:     :=
Range:          ..
```

### Punctuation
```
Grouping:       (  )  [  ]
Delimiters:     ;  :  ,  .
```

### Comments
```
{ This is a comment }
{ Multi-line comments
  are also supported }
```

## Usage

### Basic Usage

```python
from src.lexer import Scanner, TokenType

# Create scanner
scanner = Scanner('source.pas')

# Get tokens one at a time
token = scanner.get_next_token()
while token.token_type != TokenType.EOF:
    print(token)
    token = scanner.get_next_token()

scanner.close()
```

### Scan Entire File

```python
from src.lexer import Scanner

scanner = Scanner('source.pas')
tokens = scanner.scan()

for token in tokens:
    print(f"{token.token_type}: {token.lexeme}")

scanner.close()
```

### Save to File

```python
from main import analyze_source

analyze_source('input.pas', 'output/tokens.txt', verbose=True)
```

### Run from Command Line

```bash
# Scan a file and save tokens
python main.py source.pas

# Run test suite
python test_lexer.py
```

## Token Output Format

Each token is output as:
```
(TokenType, "Lexeme", Line, Column)
```

### Example

Input Pascal code:
```pascal
program Test;
var x: integer;
begin
    x := 42;
end.
```

Output tokens:
```
(KEYWORD_PROGRAM, "program", 1, 1)
(ID, "Test", 1, 9)
(SEMICOLON, ";", 1, 13)
(KEYWORD_VAR, "var", 2, 1)
(ID, "x", 2, 5)
(COLON, ":", 2, 6)
(KEYWORD_INTEGER, "integer", 2, 7)
(SEMICOLON, ";", 2, 14)
(KEYWORD_BEGIN, "begin", 3, 1)
(ID, "x", 4, 5)
(ASSIGN, ":=", 4, 7)
(NUMBER, "42", 4, 10)
(SEMICOLON, ";", 4, 12)
(KEYWORD_END, "end", 5, 1)
(DOT, ".", 5, 4)
(EOF, "EOF", 5, 5)
```

## Error Handling

### Lexical Errors

The scanner detects and reports various lexical errors:

```python
try:
    scanner = Scanner('source.pas')
    tokens = scanner.scan()
except LexicalError as e:
    print(f"Error: {e}")
```

### Error Examples

```
Line 10 Column 15
Invalid character '@'

Line 5: Unterminated comment
```

## Double Buffering Implementation

### Key Design Features

1. **Two Buffers**: Each 1024 bytes (configurable)
2. **Forward Pointer**: Current position in active buffer
3. **Lexeme Begin**: Start of current token
4. **Automatic Switching**: Seamlessly switches between buffers
5. **Buffer Reloading**: Fetches next chunk from file

### Buffer Mechanism

```
Buffer1: [████████]  (exhausted)
Buffer2: [████████]  (active)
         ^forward
^lexeme_begin
         ├─ Switch buffers when forward reaches end
         └─ Reload exhausted buffer from file
```

## Test Suite

Run comprehensive tests:

```bash
python test_lexer.py
```

### Test Coverage

✓ Keyword Recognition  
✓ Identifier Recognition  
✓ Number Parsing (all formats)  
✓ Operator Recognition  
✓ Punctuation Recognition  
✓ Comment Handling  
✓ Line/Column Tracking  
✓ Whitespace Skipping  
✓ Complex Program Analysis  
✓ Error Handling  

## API Reference

### Scanner Class

```python
class Scanner:
    # Initialize
    def __init__(source_file: str)
    
    # Token retrieval
    def get_next_token() -> Token
    def scan() -> List[Token]
    
    # Error handling
    def get_errors() -> List[str]
    
    # Cleanup
    def close()
```

### Token Class

```python
class Token:
    def __init__(token_type: str, lexeme: str, line: int, column: int)
    
    @property
    def token_type: str
    
    @property
    def lexeme: str
    
    @property
    def line: int
    
    @property
    def column: int
    
    def to_tuple() -> Tuple[str, str, int, int]
    def to_dict() -> Dict
```

## Performance Considerations

- **Buffer Size**: Default 1024 bytes, adjustable for memory constraints
- **Character Lookahead**: Single character peek for efficient parsing
- **Linear Scan**: O(n) time complexity where n = total characters
- **Minimal Memory**: Two buffers + state variables (constant space)

## Integration with Parser

The lexical analyzer is designed to integrate seamlessly with parser modules:

```python
from src.lexer import Scanner, TokenType

scanner = Scanner('input.pas')

# Parser can call get_next_token() iteratively
token = scanner.get_next_token()
while token.token_type != TokenType.EOF:
    # Parser processes token
    process_token(token)
    token = scanner.get_next_token()
```

## Examples

### Example 1: Simple Variable Declaration

```pascal
var x: integer;
```

Tokens:
```
(KEYWORD_VAR, "var", 1, 1)
(ID, "x", 1, 5)
(COLON, ":", 1, 6)
(KEYWORD_INTEGER, "integer", 1, 7)
(SEMICOLON, ";", 1, 14)
```

### Example 2: If Statement with Operators

```pascal
if (x > 5) and (y <= 10) then
    z := x + y;
```

Tokens:
```
(KEYWORD_IF, "if", 1, 1)
(LPAREN, "(", 1, 4)
(ID, "x", 1, 5)
(GT, ">", 1, 7)
(NUMBER, "5", 1, 9)
(RPAREN, ")", 1, 10)
(KEYWORD_AND, "and", 1, 12)
(LPAREN, "(", 1, 16)
(ID, "y", 1, 17)
(LE, "<=", 1, 19)
(NUMBER, "10", 1, 22)
(RPAREN, ")", 1, 24)
(KEYWORD_THEN, "then", 1, 26)
(ID, "z", 2, 5)
(ASSIGN, ":=", 2, 7)
(ID, "x", 2, 10)
(PLUS, "+", 2, 12)
(ID, "y", 2, 14)
(SEMICOLON, ";", 2, 15)
```

## Troubleshooting

### File Not Found
```python
FileNotFoundError: Cannot open source file
```
→ Verify the source file path exists and is readable

### Unterminated Comment
```
LexicalError: Line 5: Unterminated comment
```
→ Check that all `{` comments are closed with `}`

### Invalid Character
```
LexicalError: Line 10 Column 15 - Invalid character '@'
```
→ Use only valid Pascal operators and characters

## License

Educational - For Compiler Construction Course

## Author Notes

This implementation prioritizes:
1. **Correctness**: Follows Dragon Book specifications
2. **Clarity**: Well-commented, modular code
3. **Reusability**: Clean API for parser integration
4. **Robustness**: Comprehensive error handling

## References

- Aho, Sethi, Ullman: "Compilers: Principles, Techniques and Tools" (Dragon Book)
- Appendix A: Pascal Subset Specification
- Chapter 3: Lexical Analysis
