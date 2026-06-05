# Quick Start Guide - Mini Pascal Lexical Analyzer

## Installation & Setup

No installation needed! Just run the Python scripts directly.

### Requirements
- Python 3.6 or later
- No external dependencies

---

## Quick Start (5 Minutes)

### 1. Run Tests (Verify Everything Works)

```bash
python test_lexer.py
```

**Expected Output:**
```
✓ TEST 1: Keywords Recognition
✓ TEST 2: Identifier Recognition
✓ TEST 3: Number Recognition
✓ TEST 4: Operator Recognition
✓ TEST 5: Punctuation Recognition
✓ TEST 6: Comment Handling
✓ TEST 7: Line/Column Tracking
✓ TEST 8: Whitespace Handling
✓ TEST 9: Complex Program
✓ TEST 10: Error Handling

SUCCESS RATE: 100.0%
```

### 2. Analyze a Sample Program

```bash
python main.py sample.pas
```

**Output:** Generates `output/tokens.txt` with 133 tokens

### 3. Use in Your Code

```python
from src.lexer import Scanner

scanner = Scanner('myprogram.pas')
tokens = scanner.scan()

for token in tokens:
    print(token)  # (TokenType, "Lexeme", Line, Column)

scanner.close()
```

---

## Common Tasks

### Task 1: Get Next Token

```python
from src.lexer import Scanner, TokenType

scanner = Scanner('program.pas')

while True:
    token = scanner.get_next_token()
    if token.token_type == TokenType.EOF:
        break
    print(token)

scanner.close()
```

### Task 2: Count Token Types

```python
from src.lexer import Scanner, TokenType

scanner = Scanner('program.pas')
tokens = scanner.scan()

keywords = len([t for t in tokens if t.token_type.startswith('KEYWORD')])
identifiers = len([t for t in tokens if t.token_type == TokenType.ID])
numbers = len([t for t in tokens if t.token_type == TokenType.NUMBER])

print(f"Keywords: {keywords}")
print(f"Identifiers: {identifiers}")
print(f"Numbers: {numbers}")

scanner.close()
```

### Task 3: Handle Errors

```python
from src.lexer import Scanner, LexicalError

try:
    scanner = Scanner('program.pas')
    tokens = scanner.scan()
    scanner.close()
except LexicalError as e:
    print(f"Error: {e}")
```

### Task 4: Get Token Position

```python
from src.lexer import Scanner

scanner = Scanner('program.pas')
tokens = scanner.scan()

# Find tokens at specific lines
for token in tokens:
    if token.line == 5:
        print(f"Line 5, Col {token.column}: {token.lexeme}")

scanner.close()
```

---

## File Organization

```
src/lexer/
├── __init__.py      - Package exports
├── token.py         - Token class & types
├── keywords.py      - Keyword dictionary
├── buffer.py        - Double buffering system
└── scanner.py       - Main lexer
```

---

## Important Classes

### Scanner
Main class for lexical analysis

```python
scanner = Scanner(source_file)
token = scanner.get_next_token()  # Get one token
tokens = scanner.scan()           # Get all tokens
scanner.close()                   # Close file
```

### Token
Represents a single token

```python
token.token_type   # Type: 'KEYWORD', 'ID', 'NUMBER', etc.
token.lexeme       # Text: "program", "x", "42", etc.
token.line         # Line number
token.column       # Column number
str(token)         # Format: (Type, "Lexeme", Line, Col)
```

### TokenType
Token type constants

```python
from src.lexer import TokenType

TokenType.KEYWORD_PROGRAM   # "program"
TokenType.ID                # Identifier
TokenType.NUMBER            # Number
TokenType.PLUS              # "+"
TokenType.EOF               # End of file
```

---

## Supported Constructs

### Keywords (20 total)
```
program, var, integer, real, array, of
function, procedure, begin, end
if, then, else, while, do, not
div, mod, and, or
```

### Identifiers
```
x, myVar, _test, variable123
[a-zA-Z][a-zA-Z0-9_]*
```

### Numbers
```
123           - Integer
45.67         - Real
1E10          - Scientific
1.2E-5        - Scientific with decimal
```

### Operators
```
+, -, *, /, =, <>, <, <=, >, >=, :=, ..
div, mod, and, or, not
```

### Punctuation
```
(, ), [, ], ;, :, ,, .
```

### Comments
```
{ This is a comment }
```

---

## Token Format Examples

### Keyword Token
```
(KEYWORD_PROGRAM, "program", 1, 1)
    ↑ Type        ↑ Text    ↑Line ↑Col
```

### Identifier Token
```
(ID, "myVariable", 2, 10)
```

### Number Token
```
(NUMBER, "42", 3, 5)
```

### Operator Token
```
(ASSIGN, ":=", 4, 7)
```

### Punctuation Token
```
(SEMICOLON, ";", 5, 15)
```

---

## Error Messages

### Invalid Character
```
Lexical Error:
Line 10 Column 15
Invalid character '@'
```

### Unterminated Comment
```
Lexical Error:
Line 5: Unterminated comment
```

### Invalid Number
```
Lexical Error:
Line 3 Column 10: Invalid scientific notation
```

---

## Tips & Tricks

### Tip 1: Reuse Scanner in Parser
```python
class Parser:
    def __init__(self, source_file):
        self.scanner = Scanner(source_file)
        self.advance()
    
    def advance(self):
        self.current = self.scanner.get_next_token()
```

### Tip 2: Filter Tokens
```python
keywords = [t for t in tokens if t.token_type.startswith('KEYWORD')]
ops = [t for t in tokens if t.token_type in [TokenType.PLUS, TokenType.MINUS]]
```

### Tip 3: Get Token Statistics
```python
token_types = {}
for token in tokens:
    token_types[token.token_type] = token_types.get(token.token_type, 0) + 1

for token_type, count in sorted(token_types.items()):
    print(f"{token_type}: {count}")
```

### Tip 4: Save Tokens to File
```python
with open('tokens.txt', 'w') as f:
    for token in tokens:
        f.write(str(token) + '\n')
```

---

## Complete Example

```python
from src.lexer import Scanner, TokenType, LexicalError

def analyze_pascal_file(filename):
    """Analyze a Pascal file and display token statistics"""
    try:
        scanner = Scanner(filename)
        tokens = scanner.scan()
        scanner.close()
        
        # Display results
        print(f"File: {filename}")
        print(f"Total Tokens: {len(tokens)}")
        print()
        
        # Count by type
        stats = {}
        for token in tokens:
            ttype = token.token_type
            stats[ttype] = stats.get(ttype, 0) + 1
        
        print("Token Types:")
        for ttype in sorted(stats.keys()):
            print(f"  {ttype}: {stats[ttype]}")
        
        # Show first 10 tokens
        print("\nFirst 10 Tokens:")
        for token in tokens[:10]:
            print(f"  {token}")
        
    except LexicalError as e:
        print(f"Lexical Error: {e}")

if __name__ == '__main__':
    analyze_pascal_file('sample.pas')
```

---

## Project Structure

```
FinalProject/
├── src/
│   ├── __init__.py
│   └── lexer/
│       ├── __init__.py       # Export public API
│       ├── token.py          # Token class
│       ├── keywords.py       # Keywords dictionary
│       ├── buffer.py         # Double buffering
│       └── scanner.py        # Main lexer
├── output/
│   └── tokens.txt            # Generated output
├── main.py                   # CLI driver
├── test_lexer.py             # Test suite
├── sample.pas                # Example program
├── README.md                 # Full docs
├── SUMMARY.md                # Implementation summary
└── QUICK_START.md            # This file
```

---

## Troubleshooting

### Issue: "Module not found" error
```
ModuleNotFoundError: No module named 'src'
```

**Solution:** Run from the project root directory:
```bash
cd FinalProject
python test_lexer.py
```

### Issue: "Permission denied" error
```
PermissionError: [WinError 32] The process cannot access the file
```

**Solution:** Make sure no other program is using the file. Try closing it first.

### Issue: Scanner hangs
```
Seems to be stuck...
```

**Solution:** Check that the source file is readable and the path is correct.

---

## Next Steps

1. ✅ Run tests: `python test_lexer.py`
2. ✅ Analyze sample: `python main.py sample.pas`
3. ✅ Read full docs: See `README.md`
4. ✅ Integrate with parser
5. ✅ Build your compiler!

---

## Support

- **Full Documentation:** See `README.md`
- **Implementation Details:** See `SUMMARY.md`
- **Code Examples:** See `main.py` and `test_lexer.py`
- **Sample Program:** See `sample.pas`

---

**Happy Compiling! 🚀**
