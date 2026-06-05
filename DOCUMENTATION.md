# Mini Pascal Compiler — Technical Documentation

Implementation reference for the lexer, parsers, symbol table, semantic analyzer, error handler, and SLR(1) infrastructure.

---

## Table of Contents

1. [Lexer](#1-lexer)
2. [Grammar Transformation](#2-grammar-transformation)
3. [Recursive Descent Parser](#3-recursive-descent-parser)
4. [LL(1) Predictive Parser](#4-ll1-predictive-parser)
5. [SLR(1) Parser](#5-slr1-parser)
6. [Symbol Table](#6-symbol-table)
7. [Error Handler](#7-error-handler)
8. [Semantic Analyzer](#8-semantic-analyzer)
9. [Testing and Verification](#9-testing-and-verification)
10. [File Reference](#10-file-reference)

---

## 1. Lexer

### Architecture

```
Scanner
  ├── Buffer (double buffering, 1024-byte buffers)
  ├── Keywords (20 Pascal keywords, case-insensitive)
  └── Token (type, lexeme, line, column)
```

### Components

| Module | Role |
|--------|------|
| `buffer.py` | Two-buffer I/O with `forward` and `lexeme_begin` pointers; automatic reload and EOF detection |
| `token.py` | `Token` class and `TokenType` constants (35+ types); `to_tuple()`, `to_dict()` |
| `keywords.py` | `PASCAL_KEYWORDS` dict and `is_keyword()` lookup |
| `scanner.py` | `get_next_token()`, `scan()`; raises `LexicalError` on invalid input |

### Token format

```
(TokenType, "Lexeme", Line, Column)
```

Example:

```
(KEYWORD_PROGRAM, "program", 1, 1)
(ID, "GCD", 1, 9)
(NUMBER, "42", 4, 10)
(EOF, "EOF", 5, 5)
```

### Lexer test results

| Test | Coverage |
|------|----------|
| Keywords | 20 keywords |
| Identifiers | Pattern validation |
| Numbers | Integer, real, scientific |
| Operators | All arithmetic, relational, logical |
| Punctuation | All delimiters |
| Comments | Skipped; unterminated detected |
| Position | Line/column across buffers |
| Whitespace | Skipped |
| Complex program | Full program tokenization |
| Errors | Invalid characters reported |

**Success rate: 10/10 (100%)**

### Performance

| Metric | Value |
|--------|-------|
| Time complexity | O(n) |
| Space complexity | O(1) — two fixed buffers |
| Buffer size | 1024 bytes |
| Lookahead | 1 character |

---

## 2. Grammar Transformation

The original LALR(1) grammar from Appendix A is converted to LL(1) form.

### Left recursion elimination

Pattern: `A → A α | β` becomes `A → β A'`, `A' → α A' | ε`

Applied to:

- `simple_expression` → `term simple_expr'`
- `term` → `factor term'`
- `statement_list` → `statement stmt_list'`
- `identifier_list` → `id id_list'`
- `parameter_list` → `id_list:type param_list'`

### Left factoring

Pattern: `A → α β | α γ` becomes `A → α A'`, `A' → β | γ`

Applied to:

- `statement` → `id var_or_proc_tail`
- `factor` → `id factor_tail`
- `expression_list` → `expr expr_list' | ε`

### Ambiguity resolution

Dangling-else resolved by nearest-`if` binding:

```
if expr then stmt else_part
else_part → else stmt | ε
```

### Grammar statistics

| Property | Count |
|----------|-------|
| Non-terminals | 32 |
| Left recursion removed | 6 productions |
| Left factoring groups | 3 |
| Epsilon productions added | 8 |
| LL(1) conflicts | None detected |

### Key classes

- **`GrammarAnalyzer`** (`first_follow.py`): Computes FIRST and FOLLOW sets; validates LL(1) properties
- **`ParsingTableGenerator`** (`parsing_table.py`): Builds M[A, a] table; 48+ entries

### Sample FIRST/FOLLOW

```
FIRST(declarations)  = {var, EPSILON}
FIRST(expression)    = {ID, LPAREN, NUMBER, sign}
FOLLOW(program)      = {EOF}
FOLLOW(expression)   = {THEN, DO, SEMICOLON, RPAREN, RBRACKET, COMMA, ...}
```

Full sets: `output/first_sets.txt`, `output/follow_sets.txt`

---

## 3. Recursive Descent Parser

**Class:** `RecursiveDescentParser` (`recursive_descent.py`)

### Design

- One method per non-terminal (`parse_program`, `parse_statement`, `parse_expression`, etc.)
- Consumes tokens via `scanner.get_next_token()`
- Predictive lookahead — no backtracking
- Returns ACCEPT/REJECT

### Trace format

- Entry/exit for each non-terminal
- Token matches with indentation by depth
- Success (✓) and failure (✗) markers

### Error reporting

```
Line 5, Column 11: Expected keyword begin, found x
```

### Example

```python
scanner = Scanner("simple_valid.pas")
parser = RecursiveDescentParser(scanner)
success = parser.parse_program()
trace = parser.get_trace()
errors = parser.get_errors()
```

Output: `output/rd_trace.txt`

---

## 4. LL(1) Predictive Parser

**Class:** `PredictiveParser` (`predictive_parser.py`)

### Algorithm

```
stack = [EOF, program]
while stack not empty:
    top = pop(stack)
    if top is terminal:
        match with input or ERROR
    else:
        production = M[top, current_terminal]
        push production (reversed) or ERROR
```

### Trace columns

| Column | Content |
|--------|---------|
| Step | Step number |
| Stack | Current stack contents |
| Input | Remaining tokens |
| Action | MATCH, EXPAND, ACCEPT, ERROR |

### Token mapping

Lexer types (`KEYWORD_PROGRAM`, `ID`, `NUMBER`, etc.) map to grammar terminals for table lookup.

Output: `output/ll1_table.txt`, `output/predictive_trace.txt`

---

## 5. SLR(1) Parser

**Class:** `SLRParser` (`lr_parser/lr_parser.py`)

### LR infrastructure

| Class | Purpose |
|-------|---------|
| `LRItem` | LR(0) item `[A → α • β]` with dot position |
| `LRItemSet` | State = set of items; `closure()`, `goto()` |
| `SLRParser` | Builds automaton and ACTION/GOTO tables |

### Table construction

1. **Item sets**: Augmented grammar `S' → S`; closure and GOTO until fixed point
2. **Shift**: For `[A → α • aβ]`, shift on terminal `a`
3. **Reduce**: For `[A → α •]`, reduce on all `a ∈ FOLLOW(A)`
4. **Accept**: For `[S' → S •]` on EOF

### Scale (Mini Pascal grammar)

| Metric | Value |
|--------|-------|
| Parser states | 158 |
| ACTION entries | 290 |
| GOTO entries | 171 |
| Productions | 72 |

Output: `output/action_table.txt`, `output/goto_table.txt`, `output/slr_trace.txt`

---

## 6. Symbol Table

**Modules:** `src/symbol_table/symbol.py`, `symbol_table.py`

### Symbol

| Attribute | Description |
|-----------|-------------|
| `name` | Identifier |
| `kind` | Variable, function, procedure, array, parameter, type |
| `data_type` | `DataType` enum (INTEGER, REAL, etc.) |
| `scope_level` | 0 = global |
| `line_number`, `column_number` | Declaration site |
| `attributes` | Extensible metadata (parameters, array bounds) |

### SymbolTable

- Hash-table lookup with scope stack
- `enter_scope()` / `exit_scope()` for nesting
- `insert()`, `lookup()`, `lookup_in_current_scope()`
- Duplicate detection and shadowing support
- `print_table()`, `get_statistics()`

### ScopedSymbolTable

Convenience API: `declare_variable()`, `declare_function()`, `declare_procedure()`, `declare_array()`

### SymbolBuilder

Fluent builder: `SymbolBuilder(...).with_type(...).with_parameter(...).build()`

---

## 7. Error Handler

**Module:** `src/error_handler/error_handler.py`

### Error types

| Type | Use |
|------|-----|
| `LEXICAL` | Invalid characters, bad numbers |
| `SYNTAX` | Grammar violations |
| `SEMANTIC` | Undeclared identifiers, bad usage |
| `TYPE_ERROR` | Type mismatches |
| `SCOPE_ERROR` | Visibility violations |

### CompilerError fields

Line, column, message, lexeme, optional context.

### ErrorHandler API

`add_lexical_error()`, `add_syntax_error()`, `add_semantic_error()`, `add_type_error()`, `add_scope_error()`, `has_errors()`, `get_error_count_by_type()`, `print_errors()`

### Recovery strategies

- **`panic_mode_recovery()`** — skip tokens to sync point (LL)
- **`shift_reduce_recovery()`** — find valid action in LR state

### CompilationStatus

Tracks success, error count, current phase, duration.

---

## 8. Semantic Analyzer

**Module:** `src/semantic_analyzer.py`

Integrates `ErrorHandler` and `ScopedSymbolTable`.

### Checks

| Method | Validates |
|--------|-----------|
| `check_identifier_declared()` | Symbol exists |
| `check_duplicate_declaration()` | No redeclaration in scope |
| `check_variable_access()` | Variable visible |
| `check_function_call()` | Name and arity |
| `check_procedure_call()` | Name and arity |
| `check_array_access()` | Array declared and accessible |
| `check_type_compatibility()` | Types match (int → real allowed) |

### Declarations

`declare_variable()`, `declare_function()`, `declare_procedure()` with scope management via `enter_scope()` / `exit_scope()`.

---

## 9. Testing and Verification

### Test runners

| Script | Scope |
|--------|-------|
| `test_lexer.py` | 10 lexer tests |
| `test_parsers.py` | FIRST/FOLLOW, RD, predictive parsers |
| `test_all_modules.py` | Symbol table, errors, semantic, SLR (5 tests) |
| `test_integration.py` | End-to-end pipeline |
| `verify_project.py` | Required files and output artifacts |

### Integration test results (`test_all_modules.py`)

1. Symbol table with scoping — PASS
2. Error handler categories — PASS
3. Semantic analysis — PASS
4. SLR(1) parser infrastructure — PASS
5. Full module integration — PASS

### Sample programs

| File | Purpose |
|------|---------|
| `sample.pas` | GCD program (arrays, functions, control flow) |
| `simple_valid.pas` | Minimal valid program for parser traces |
| `tests/valid_*.pas` | Additional valid programs |
| `tests/invalid_*.pas` | Lexical, syntax, semantic error cases |

### Generate all reports

```bash
python generate_all_reports.py
```

Steps: FIRST → FOLLOW → LL(1) table → ACTION/GOTO → RD trace → predictive trace → SLR trace → grammar notes → symbol table.

---

## 10. File Reference

### Source modules

| Path | Lines (approx.) | Description |
|------|-----------------|-------------|
| `src/lexer/token.py` | 380+ | Token types |
| `src/lexer/buffer.py` | 280+ | Double buffering |
| `src/lexer/scanner.py` | 350+ | Main lexer |
| `src/parsers/first_follow.py` | — | Grammar and FIRST/FOLLOW |
| `src/parsers/recursive_descent.py` | — | RD parser |
| `src/parsers/predictive_parser.py` | — | LL(1) parser |
| `src/lr_parser/lr_parser.py` | 500+ | SLR parser |
| `src/symbol_table/symbol_table.py` | 400+ | Scoped symbol table |
| `src/error_handler/error_handler.py` | 350+ | Error management |
| `src/semantic_analyzer.py` | 300+ | Semantic checks |

### Entry points

| Script | Role |
|--------|------|
| `main.py` | Lexer-only CLI |
| `main_compiler.py` | Full compiler (`--parser rd\|ll1\|slr`) |
| `generate_all_reports.py` | Batch report generation |
| `generate_docs.py` | Regenerate parser documentation sections |
| `verify_project.py` | Project completeness check |

### Grammar reference

`pascal.txt` — Dragon Book Appendix A LALR(1) grammar and program structure.

`docs/GRAMMAR_ANALYSIS.md` — Detailed grammar analysis.

`docs/PHASE_1_INTERFACES.md` — Module interface contracts.

---

## Module dependency graph

```
ErrorHandler
    ├── SemanticAnalyzer
    └── Parsers (RD, LL(1), SLR)

SymbolTable
    └── SemanticAnalyzer

GrammarAnalyzer
    ├── ParsingTableGenerator (LL(1))
    └── SLRParser
```

---

## References

- Aho, Sethi, Ullman — *Compilers: Principles, Techniques, and Tools* (Dragon Book)
  - Appendix A: Mini Pascal specification
  - §4.3–4.4: LL parsing
  - LR parsing (SLR construction)

---

*Compiler Construction Lab — Semester 6*
