# Phase 1: Frozen Shared Interfaces

All team members and evaluators must use these exact specifications.

---

## 1. Token Object

Every parser consumes tokens in this exact format:

```python
class Token:
    def __init__(self, token_type, lexeme, line, column):
        self.token_type = token_type    # Type of token (string)
        self.lexeme = lexeme            # Actual text (string)
        self.line = line                # Line number (int, 1-based)
        self.column = column            # Column number (int, 1-based)
```

### Location
`src/lexer/token.py`

### Usage Examples

```python
# Token for integer 42
token = Token('NUMBER', '42', 5, 10)

# Token for keyword
token = Token('KEYWORD_PROGRAM', 'program', 1, 1)

# Token for identifier
token = Token('ID', 'variable_name', 3, 8)
```

### Verified ✓
- [x] Token class exists with exact signature
- [x] All 4 attributes present and initialized
- [x] String representation implemented
- [x] Used by all parsers consistently

---

## 2. Lexer API

Every lexer must expose this API:

```python
from src.lexer.scanner import Scanner

# Constructor
lexer = Scanner(filename)

# Method: Get next token
token = lexer.get_next_token()  # Returns Token or None (EOF)

# Method: Scan all tokens
tokens = lexer.scan()           # Returns List[Token]

# Method: Reset
lexer.reset()                   # Rewind to start
```

### Location
`src/lexer/scanner.py`

### Contract

| Method | Input | Returns | Purpose |
|--------|-------|---------|---------|
| `get_next_token()` | None | Token \| None | Get one token, advance position |
| `scan()` | None | List[Token] | Get all tokens until EOF |
| `reset()` | None | None | Rewind to file start |

### Critical Requirement
**No parser should directly access files.**  
Only the lexer reads source code.

### Verified ✓
- [x] Scanner class exists with exact API
- [x] `get_next_token()` returns Token objects
- [x] `scan()` returns complete token list
- [x] Consistent TokenType enum
- [x] File I/O only in lexer

---

## 3. Error Object

Every compiler component reports errors using this format:

```python
class CompilerError:
    def __init__(self, error_type, message, line, column):
        self.error_type = error_type    # ErrorType enum
        self.message = message          # Error message (string)
        self.line = line                # Line number (int, 1-based)
        self.column = column            # Column number (int, 1-based)
```

### Error Types (Enum)

```python
class ErrorType(Enum):
    LEXICAL = "Lexical Error"
    SYNTAX = "Syntax Error"
    SEMANTIC = "Semantic Error"
    TYPE_ERROR = "Type Error"
    SCOPE_ERROR = "Scope Error"
```

### Location
`src/error_handler/error_handler.py`

### Used By

| Component | Error Type |
|-----------|-----------|
| **Lexer** | LEXICAL (invalid characters, unclosed strings) |
| **RD Parser** | SYNTAX (unexpected tokens) |
| **LL(1) Parser** | SYNTAX (no entry in M table) |
| **SLR(1) Parser** | SYNTAX (shift-reduce/reduce-reduce conflicts) |
| **Symbol Table** | SEMANTIC, SCOPE_ERROR (duplicate symbols) |
| **Type Checker** | TYPE_ERROR (type mismatch) |

### Usage Examples

```python
# Lexer error
error = CompilerError(
    ErrorType.LEXICAL,
    "Invalid character '@'",
    line=5, column=8
)

# Syntax error
error = CompilerError(
    ErrorType.SYNTAX,
    "Expected ';'",
    line=10, column=15
)

# Semantic error
error = CompilerError(
    ErrorType.SEMANTIC,
    "Undeclared identifier: x",
    line=3, column=5
)
```

### Verified ✓
- [x] CompilerError class exists with exact signature
- [x] ErrorType enum covers all categories
- [x] Used consistently by all components
- [x] Proper error reporting and collection

---

## 4. Symbol Table API

All symbol table implementations must support this interface:

```python
from src.symbol_table.symbol_table import ScopedSymbolTable

st = ScopedSymbolTable()

# Core Operations
st.insert(symbol)               # Add symbol to current scope
symbol = st.lookup(name)        # Search current + parent scopes
symbol = st.lookup_in_current_scope(name)  # Search only current scope

# Scope Management
st.enter_scope()                # Begin nested scope
st.exit_scope()                 # End nested scope

# Utilities
is_declared = st.table.is_declared(name)           # Boolean check
symbols = st.table.get_symbols_in_scope()          # Get all in scope
stats = st.table.get_statistics()                  # Get counts

# Convenience Methods (HigherLevel)
symbol = st.declare_variable(name, type, line, col)
symbol = st.declare_function(name, return_type, line, col)
symbol = st.declare_procedure(name, line, col)
symbol = st.declare_array(name, elem_type, lower, upper, line, col)
```

### Location
`src/symbol_table/symbol_table.py`

### Symbol Structure

```python
from src.symbol_table.symbol import Symbol, SymbolKind, DataType

# Each symbol contains:
symbol = Symbol(
    name="x",                       # Identifier name
    kind=SymbolKind.VARIABLE,       # VARIABLE, FUNCTION, PROCEDURE, ARRAY, etc.
    data_type=DataType.INTEGER,     # INTEGER, REAL, BOOLEAN, UNDEFINED
    scope_level=0,                  # 0 = global, 1+ = nested
    line_number=5,                  # Declaration line
    column_number=8                 # Declaration column
)

# Optional attributes
symbol.set_attribute(key, value)
symbol.add_parameter(param_name, param_type)
symbol.set_array_info(element_type, lower_bound, upper_bound)
```

### Scope Management Contract

```
Global Scope (Level 0)
└── Variable: x (INTEGER)
└── Function: compute (REAL)
    └── Local Scope (Level 1) [enter_scope()]
        └── Parameter: a (INTEGER)
        └── Variable: result (REAL)
    [exit_scope()] - back to Global
```

### Verified ✓
- [x] SymbolTable class with exact API
- [x] Symbol class with all required attributes
- [x] enter_scope() / exit_scope() implemented
- [x] O(1) lookup using hash tables
- [x] Scope stack with nesting support
- [x] Statistics collection

---

## 5. Parser Output Format

All parsers must output results in this format:

### Success Case
```
[Parser Type]
========================================
Status: ACCEPT

```

### Failure Case
```
[Parser Type]
========================================
Status: REJECT

Errors:
  Error 1: description
  Error 2: description

```

### Trace (Optional, with --verbose)
```
Derivation Trace:
→ program
  → id_list
    ...
← program ✓
```

---

## 6. Interface Implementation Checklist

### Token ✓
- [x] Location: `src/lexer/token.py`
- [x] Class: `Token(token_type, lexeme, line, column)`
- [x] All attributes initialized in `__init__`
- [x] `__repr__()` and `__str__()` implemented
- [x] Used by all parsers

### Lexer ✓
- [x] Location: `src/lexer/scanner.py`
- [x] Class: `Scanner(filename)`
- [x] Method: `get_next_token()` → Token | None
- [x] Method: `scan()` → List[Token]
- [x] Only lexer reads files
- [x] All parsers use Scanner

### Error ✓
- [x] Location: `src/error_handler/error_handler.py`
- [x] Class: `CompilerError(error_type, message, line, column)`
- [x] Enum: `ErrorType` with 5 types
- [x] Class: `ErrorHandler` for collection
- [x] Used by all components
- [x] Consistent reporting

### Symbol Table ✓
- [x] Location: `src/symbol_table/symbol_table.py`
- [x] Class: `SymbolTable` with scope stack
- [x] Class: `ScopedSymbolTable` convenience interface
- [x] Methods: `insert()`, `lookup()`, `enter_scope()`, `exit_scope()`
- [x] Class: `Symbol` with attributes
- [x] Support for all symbol kinds
- [x] Nested scope management

---

## 7. Compliance Verification

Run this to verify all interfaces:

```bash
# Check Token
python -c "from src.lexer.token import Token; t = Token('ID', 'x', 1, 5); print('Token: OK')"

# Check Lexer
python -c "from src.lexer.scanner import Scanner; print('Lexer: OK')"

# Check Error
python -c "from src.error_handler.error_handler import CompilerError, ErrorType; print('Error: OK')"

# Check Symbol Table
python -c "from src.symbol_table.symbol_table import ScopedSymbolTable; st = ScopedSymbolTable(); print('SymbolTable: OK')"
```

---

## Summary

✓ **Token Interface**: Frozen, all parsers consume same format  
✓ **Lexer API**: Frozen, only file I/O here  
✓ **Error Object**: Frozen, consistent categorization  
✓ **Symbol Table API**: Frozen, unified scope management  

**All interfaces are production-ready and team-approved.**

For viva submission, reference this document to show interface consistency across all compiler components.
