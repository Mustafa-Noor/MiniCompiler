# Mini Pascal Compiler - Parser System

Complete implementation of Recursive Descent and LL(1) Predictive Parsers for a Mini Pascal subset.

## Directory Structure

```
project/
├── src/
│   ├── lexer/           # Lexical analyzer
│   │   ├── __init__.py
│   │   ├── buffer.py    # Double-buffered input
│   │   ├── keywords.py  # Reserved keywords
│   │   ├── scanner.py   # Lexical scanner
│   │   └── token.py     # Token definitions
│   └── parsers/         # Parser modules
│       ├── __init__.py
│       ├── first_follow.py       # FIRST/FOLLOW computation
│       ├── parsing_table.py      # LL(1) table construction
│       ├── recursive_descent.py  # Recursive descent parser
│       └── predictive_parser.py  # LL(1) predictive parser
├── output/              # Generated output files
│   ├── first_sets.txt          # FIRST sets
│   ├── follow_sets.txt         # FOLLOW sets
│   ├── ll1_table.txt           # LL(1) parsing table
│   ├── grammar_transformation.txt # Grammar changes
│   ├── rd_trace.txt            # RD parser trace
│   └── predictive_trace.txt    # Predictive parser trace
├── test_parsers.py    # Main test runner
├── simple_valid.pas   # Valid test program
├── sample.pas         # Sample program
└── README.md          # This file
```

## Grammar Transformation

The implementation converts the LALR(1) grammar from the Dragon Book into LL(1) form by:

1. **Removing Left Recursion**
   - Pattern: A → A α | β → A → β A', A' → α A' | ε
   - Applied to: expressions, terms, statement lists, identifier lists

2. **Left Factoring**
   - Removes common prefixes to enable single-token lookahead
   - Applied to: statements, factors

3. **Ambiguity Resolution**
   - Dangling-else handled by left-associating to nearest if
   - Operator precedence preserved through grammar structure

## Parser Components

### Recursive Descent Parser
- Top-down predictive parsing
- One function per non-terminal
- Produces derivation tree trace
- Reports syntax errors with line/column numbers

### LL(1) Predictive Parser
- Stack-driven parsing algorithm
- Uses precomputed M[A, a] parsing table
- Produces detailed parse stack trace
- Reports error location and expected vs. actual tokens

## Output Files

| File | Description |
|------|-------------|
| first_sets.txt | FIRST sets for all non-terminals |
| follow_sets.txt | FOLLOW sets for all non-terminals |
| ll1_table.txt | LL(1) parsing table entries |
| grammar_transformation.txt | Grammar transformation documentation |
| rd_trace.txt | Recursive descent parser trace |
| predictive_trace.txt | LL(1) predictive parser trace |

## Usage

```python
from src.parsers import RecursiveDescentParser, PredictiveParser
from src.lexer import Scanner

# Parse with recursive descent parser
scanner = Scanner("program.pas")
parser = RecursiveDescentParser(scanner)
success = parser.parse_program()
print(parser.get_trace())

# Parse with predictive parser
scanner = Scanner("program.pas")
parser = PredictiveParser(scanner)
success, trace, errors = parser.parse()
print(trace)
```

## Running Tests

```bash
python test_parsers.py
```

This generates all output files and tests both parsers on a sample program.

## Language Specification

The Mini Pascal subset includes:

**Programs**: Global declarations + procedures/functions + main statement block

**Data Types**: Integer, Real, Arrays

**Statements**: 
- Assignment
- Procedure calls
- If-then-else
- While loops
- Compound statements (begin...end)

**Expressions**: Arithmetic, relational, logical operators with proper precedence

## Key Features

✓ Complete LL(1) grammar transformation
✓ FIRST and FOLLOW set computation
✓ Recursive descent parser with derivation trace
✓ LL(1) predictive parser with stack trace
✓ Comprehensive error reporting
✓ Detailed documentation

## Verification

Both parsers:
- Accept all valid Mini Pascal programs
- Reject all invalid programs with error messages
- Produce identical results for the same input
- Generate detailed parse traces for verification
