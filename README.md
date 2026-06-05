# Mini Pascal Compiler

A complete compiler front-end for the Mini Pascal subset defined in **Appendix A of the Dragon Book** (*Compilers: Principles, Techniques, and Tools*). Implements lexical analysis, multiple parsing strategies (recursive descent, LL(1), SLR(1)), symbol table management, semantic analysis, and centralized error handling.

**Compiler Construction Lab — Semester 6**

---

## Requirements

- Python 3.6+
- No external dependencies (pure Python)

Run all commands from the project root directory.

---

## Quick Start

### 1. Verify the lexer

```bash
python test_lexer.py
```

Runs 10 tests covering keywords, identifiers, numbers, operators, comments, position tracking, and error handling.

### 2. Tokenize a program

```bash
python main.py sample.pas
```

Writes the token stream to `output/tokens.txt`.

### 3. Compile with a parser

```bash
python main_compiler.py sample.pas --parser rd
python main_compiler.py sample.pas --parser ll1
python main_compiler.py sample.pas --parser slr
python main_compiler.py sample.pas --parser rd --verbose
```

Parser choices: `rd` (recursive descent), `ll1` (predictive), `slr` (shift-reduce).

### 4. Generate all analysis reports (viva / submission)

```bash
python generate_all_reports.py
```

Produces FIRST/FOLLOW sets, LL(1) table, ACTION/GOTO tables, parser traces, grammar transformation notes, and symbol table output under `output/`.

### 5. Run full test suites

```bash
python test_lexer.py          # Lexical analyzer (10 tests)
python test_parsers.py        # Parser modules
python test_all_modules.py    # Symbol table, errors, semantic, SLR
python test_integration.py    # End-to-end integration
python verify_project.py      # File and output verification
```

---

## Project Structure

```
FinalProject/
├── src/
│   ├── lexer/                  # Lexical analyzer
│   │   ├── buffer.py           # Double-buffered input
│   │   ├── keywords.py         # Reserved keywords
│   │   ├── scanner.py          # Token scanner
│   │   └── token.py            # Token types and Token class
│   ├── parsers/                # LL(1) grammar and parsers
│   │   ├── first_follow.py     # Grammar, FIRST/FOLLOW sets
│   │   ├── parsing_table.py    # LL(1) table construction
│   │   ├── recursive_descent.py
│   │   └── predictive_parser.py
│   ├── lr_parser/              # SLR(1) shift-reduce parser
│   │   └── lr_parser.py
│   ├── symbol_table/           # Scoped symbol table
│   │   ├── symbol.py
│   │   └── symbol_table.py
│   ├── error_handler/          # Centralized error reporting
│   │   └── error_handler.py
│   └── semantic_analyzer.py    # Semantic analysis
├── output/                     # Generated reports and traces
├── tests/                      # Valid/invalid test programs
├── docs/                       # Grammar analysis and interface notes
├── main.py                     # Lexer CLI driver
├── main_compiler.py            # Full compiler driver (all parsers)
├── generate_all_reports.py     # Batch report generator
├── sample.pas                  # GCD sample program
├── simple_valid.pas            # Minimal valid program
└── pascal.txt                  # Dragon Book Appendix A reference
```

---

## Language Subset

### Keywords (20)

```
program  var  integer  real  array  of
function  procedure  begin  end
if  then  else  while  do  not
div  mod  and  or
```

### Constructs

| Category | Details |
|----------|---------|
| Types | `integer`, `real`, `array [low..high] of type` |
| Identifiers | `[a-zA-Z][a-zA-Z0-9_]*` |
| Numbers | Integers, reals, scientific notation (`1E10`, `1.2E-5`) |
| Operators | `+ - * / div mod and or not = <> < <= > >= := ..` |
| Punctuation | `( ) [ ] ; : , .` |
| Comments | `{ ... }` (Pascal style) |

### Program structure

Programs include global declarations, optional procedures/functions, and a main `begin...end` block. Statements support assignment, calls, `if-then-else`, `while-do`, and compound blocks. Expressions follow standard arithmetic, relational, and logical precedence.

---

## Usage Examples

### Lexical analysis

```python
from src.lexer import Scanner, TokenType, LexicalError

scanner = Scanner("sample.pas")
tokens = scanner.scan()
for token in tokens:
    print(token)  # (TokenType, "Lexeme", Line, Column)
scanner.close()
```

Token-by-token scanning for parser integration:

```python
scanner = Scanner("program.pas")
token = scanner.get_next_token()
while token.token_type != TokenType.EOF:
    # process token
    token = scanner.get_next_token()
scanner.close()
```

### Recursive descent parser

```python
from src.lexer import Scanner
from src.parsers import RecursiveDescentParser

scanner = Scanner("simple_valid.pas")
parser = RecursiveDescentParser(scanner)
success = parser.parse_program()
print(parser.get_trace())
```

### LL(1) predictive parser

```python
from src.lexer import Scanner
from src.parsers import PredictiveParser

scanner = Scanner("simple_valid.pas")
parser = PredictiveParser(scanner)
success, trace, errors = parser.parse()
```

### Symbol table and semantic analysis

```python
from src.error_handler.error_handler import ErrorHandler
from src.symbol_table.symbol_table import ScopedSymbolTable
from src.symbol_table.symbol import DataType
from src.semantic_analyzer import SemanticAnalyzer

eh = ErrorHandler()
st = ScopedSymbolTable()
sa = SemanticAnalyzer(eh, st)

sa.declare_variable("x", DataType.INTEGER, 1, 5)
sa.check_variable_access("x", 5, 10)
```

---

## Output Files

Generated by `generate_all_reports.py` or individual test runners:

| File | Description |
|------|-------------|
| `output/tokens.txt` | Token stream from lexer |
| `output/first_sets.txt` | FIRST sets (32 non-terminals) |
| `output/follow_sets.txt` | FOLLOW sets |
| `output/ll1_table.txt` | LL(1) parsing table M[A, a] |
| `output/grammar_transformation.txt` | Left recursion removal, factoring |
| `output/rd_trace.txt` | Recursive descent derivation trace |
| `output/predictive_trace.txt` | LL(1) stack trace |
| `output/action_table.txt` | SLR(1) ACTION table |
| `output/goto_table.txt` | SLR(1) GOTO table |
| `output/slr_trace.txt` | SLR(1) parse trace |
| `output/symbol_table.txt` | Symbol table dump |

---

## Compiler Pipeline

```
Source (.pas)
    │
    ▼
Lexer (Scanner) ──► Tokens
    │
    ▼
Parser (RD / LL(1) / SLR)
    │
    ▼
Semantic Analyzer ◄──► Symbol Table
    │
    ▼
Error Handler (lexical / syntax / semantic / type / scope)
```

---

## Key Features

- **Lexer**: Double buffering, line/column tracking, 35+ token types, lexical error reporting
- **Grammar**: LALR(1) → LL(1) transformation (left recursion elimination, left factoring, dangling-else resolution)
- **Parsers**: Recursive descent with derivation trace; LL(1) stack parser; SLR(1) with 158 states
- **Symbol table**: Nested scopes, O(1) lookup, shadowing, duplicate detection
- **Semantic analyzer**: Declaration checks, type compatibility (int → real), call arity validation
- **Error handler**: Categorized errors with recovery strategies for LL and LR parsers

---

## Troubleshooting

**`ModuleNotFoundError: No module named 'src'`**  
Run commands from the project root (`FinalProject/`), not from inside `src/`.

**Output files missing**  
Run `python generate_all_reports.py` to regenerate all reports.

**File access errors on Windows**  
Close any program that has `output/*.txt` open before regenerating reports.

---

## Further Reading

See **[DOCUMENTATION.md](DOCUMENTATION.md)** for grammar transformation details, parser algorithms, module APIs, test results, and implementation notes.

See **`docs/`** for grammar analysis (`GRAMMAR_ANALYSIS.md`) and phase interfaces (`PHASE_1_INTERFACES.md`).

Reference grammar: `pascal.txt` (Dragon Book Appendix A).
