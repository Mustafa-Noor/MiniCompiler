"""
Mini Pascal Compiler - Parser System Documentation and Testing
Complete implementation of LL(1) Recursive Descent and Predictive Parsers
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from parsers.first_follow import create_ll1_grammar, GrammarAnalyzer
from parsers.parsing_table import ParsingTableGenerator


def generate_documentation():
    """Generate comprehensive documentation"""
    
    doc = """
================================================================================
MINI PASCAL COMPILER - PARSER SYSTEM
Complete Implementation of Recursive Descent and LL(1) Predictive Parsers
================================================================================

PROJECT OVERVIEW
================================================================================

This project implements a complete parser system for a Mini Pascal subset based on
the Dragon Book's Appendix A grammar. The system includes:

1. GRAMMAR TRANSFORMATION MODULE (first_follow.py)
   - Converts LALR(1) grammar to LL(1) form
   - Removes left recursion
   - Applies left factoring
   - Computes FIRST and FOLLOW sets

2. PARSING TABLE GENERATOR (parsing_table.py)
   - Constructs LL(1) predictive parsing table
   - M[non_terminal, terminal] entries
   - Handles LL(1) conflicts detection

3. RECURSIVE DESCENT PARSER (recursive_descent.py)
   - Top-down predictive parsing
   - One parsing function per non-terminal
   - Produces derivation trace
   - Reports syntax errors with line/column information

4. LL(1) PREDICTIVE PARSER (predictive_parser.py)
   - Stack-driven bottom-up parsing
   - Uses M[A, a] parsing table
   - Produces detailed parse trace
   - Reports parse state at each step

PART A: GRAMMAR TRANSFORMATION
================================================================================

ORIGINAL GRAMMAR ISSUES:
- Left recursion in multiple productions (simple_expression, term, identifier_list, etc.)
- Ambiguous if-then-else statements (dangling-else problem)
- FIRST/FOLLOW set conflicts requiring multiple lookahead

TRANSFORMATIONS APPLIED:

1. LEFT RECURSION ELIMINATION:
   Pattern: A → A α | β  becomes  A → β A', A' → α A' | ε
   
   Applied to:
   - simple_expression: term → (term addop)* = term simple_expr'
   - term: factor → (factor mulop)* = factor term'
   - statement_list: statement → (statement;)* = statement stmt_list'
   - identifier_list: id → (id,)* = id id_list'
   - parameter_list: id_list:type → (;id_list:type)* = id_list:type param_list'

2. LEFT FACTORING:
   Pattern: A → α β | α γ  becomes  A → α A', A' → β | γ
   
   Applied to:
   - statement: id assignop expr | id ( expr_list ) | id [ expr ]
     Factored to: statement → id var_or_proc_tail
   - factor: id | id ( expr_list )
     Factored to: factor → id factor_tail
   - expression_list: expr | ε
     Factored to: expr_list → expr expr_list' | ε

3. AMBIGUITY RESOLUTION:
   Dangling-else: Resolved by left-associating else to nearest if
   - if expr then stmt [else stmt]
   - Handled by: if expr then stmt else_part
   - else_part → else stmt | ε

RESULTING GRAMMAR:
- No left recursion ✓
- Left factors applied ✓
- Single lookahead sufficient ✓
- Epsilon productions for optional constructs ✓

FIRST AND FOLLOW SETS:
================================================================================

FIRST Sets computed for all non-terminals:
- program: Computed
- declarations: {var, EPSILON}
- type_spec: {integer, real, array}
- statement_list: {ID}
- expression: {ID, NUMBER, LPAREN, sign}
- term: {factor}
- factor: {ID, NUMBER, LPAREN, not, sign}

FOLLOW Sets computed for all non-terminals:
- program: {EOF}
- declarations: {BEGIN, FUNCTION, PROCEDURE}
- type_spec: {SEMICOLON, RPAREN, COMMA}
- statement_list: {END, SEMICOLON}
- expression: {THEN, DO, SEMICOLON, RPAREN, RBRACKET, COMMA}

PART B: RECURSIVE DESCENT PARSER
================================================================================

IMPLEMENTATION DETAILS:

Structure:
- Class: RecursiveDescentParser
- Initialization: RecursiveDescentParser(scanner)
- Main method: parse_program() returns bool

Parsing Functions (one per non-terminal):
- parse_program(): Main entry point
- parse_declarations(): Variable declarations
- parse_type_spec(): Type specifications
- parse_subprogram_declarations(): Function/procedure declarations
- parse_compound_statement(): begin...end blocks
- parse_statement(): Individual statements
- parse_expression(): Arithmetic/relational expressions
- parse_term(): Multiplicative expressions
- parse_factor(): Atomic expressions

Features:
1. Predictive Lookahead:
   - Checks current token to determine which production to use
   - No backtracking required
   
2. Error Reporting:
   - Syntax errors with line and column numbers
   - Shows expected token vs. actual token
   - Continues to find multiple errors
   
3. Derivation Trace:
   - Shows entry/exit for each non-terminal
   - Shows token matches
   - Indentation indicates parse depth
   - Marks success/failure with ✓/✗

4. Return Value:
   - ACCEPT: Program parsed successfully
   - REJECT: Syntax errors found

Example Usage:
    scanner = Scanner("program.pas")
    parser = RecursiveDescentParser(scanner)
    success = parser.parse_program()
    trace = parser.get_trace()
    errors = parser.get_errors()

PART C: LL(1) PREDICTIVE PARSER
================================================================================

IMPLEMENTATION DETAILS:

Structure:
- Class: PredictiveParser
- Initialization: PredictiveParser(scanner)
- Algorithm: Stack-driven parsing using M[A, a] table

Algorithm:
    stack = [EOF, Start_Symbol]
    input_pos = 0
    
    while stack not empty:
        top = pop(stack)
        current = input[input_pos]
        
        if top == EOF:
            if current == EOF: ACCEPT
            else: ERROR
        
        if isTerminal(top):
            if top matches current:
                advance input
            else: ERROR
        
        else:  // isNonTerminal(top)
            production = M[top, current]
            if production exists:
                push production (reversed) onto stack
            else: ERROR

Stack Contents:
- Bottom: EOF (end-of-input marker)
- Next: Start symbol (program)
- Others: Symbols awaiting processing

Parsing Trace Output:
    Step | Stack | Input | Action
    -----+-------+-------+--------
     1  | [EOF program ...] | [program id ( ...] | EXPAND program → ...
     2  | [EOF expr ...] | [id ( ...] | MATCH id
     3  | [EOF expr] | [( ...] | EXPAND expr → ...

Features:
1. Parsing Table:
   - M[non_terminal, terminal] = production
   - EPSILON entries for optional constructs
   - Handles all LL(1) conflicts
   
2. Token Mapping:
   - Converts lexer tokens to grammar symbols
   - Handles keyword token types
   - Maps operators and punctuation
   
3. Detailed Trace:
   - Shows stack state at each step
   - Shows remaining input
   - Shows action performed
   - Reports errors with context
   
4. Return Value:
   - ACCEPT: Input successfully parsed
   - REJECT: Parsing errors encountered

Example Usage:
    scanner = Scanner("program.pas")
    parser = PredictiveParser(scanner)
    success, trace, errors = parser.parse()
    print(trace)

OUTPUT FILES
================================================================================

Generated files (in output/ directory):

1. first_sets.txt
   - FIRST sets for all non-terminals
   - Format: FIRST(non_terminal) = {terminal1, terminal2, ...}
   - Includes EPSILON for nullable symbols

2. follow_sets.txt
   - FOLLOW sets for all non-terminals
   - Format: FOLLOW(non_terminal) = {terminal1, terminal2, ...}
   - Includes EOF for start symbol

3. ll1_table.txt
   - LL(1) parsing table entries
   - Format: M[non_terminal, terminal] -> production_symbols
   - One entry per line
   - All table entries listed

4. grammar_transformation.txt
   - Documentation of grammar transformations
   - Lists left recursion elimination steps
   - Shows left factoring rules
   - Documents ambiguity resolution
   - Lists all symbols in grammar

5. rd_trace.txt
   - Recursive descent parser trace on sample input
   - Shows derivation tree as execution proceeds
   - Reports all syntax errors found
   - Indicates final ACCEPT/REJECT result

6. predictive_trace.txt
   - Predictive parser trace on sample input
   - Shows stack contents at each step
   - Shows remaining input at each step
   - Lists action taken (shift, expand, match)
   - Reports all parse errors found

GRAMMAR REFERENCE
================================================================================

Main Production (Start Symbol):
    program → PROGRAM ID ( id_list ) ; declarations subprogram_decls compound_stmt .

Key Non-Terminals:
    declarations → VAR id_list : type_spec ; declarations | ε
    type_spec → INTEGER | REAL | ARRAY [ NUMBER .. NUMBER ] OF type_spec
    
    subprogram_decls → subprogram_decl ; subprogram_decls | ε
    subprogram_decl → subprogram_head declarations compound_stmt
    subprogram_head → FUNCTION ID arguments : type_spec ;
                    | PROCEDURE ID arguments ;
    
    compound_stmt → BEGIN optional_stmts END
    optional_stmts → statement_list | ε
    
    statement → ID var_or_proc_tail
              | compound_stmt
              | IF expression THEN statement else_part
              | WHILE expression DO statement
    
    expression → simple_expr (relop simple_expr)?
    simple_expr → (sign)? term (addop term)*
    term → factor (mulop factor)*
    factor → ID (( expr_list ))?
           | NUMBER
           | ( expression )
           | NOT factor
           | sign factor

TESTING THE PARSERS
================================================================================

Valid Program Example (simple_valid.pas):
    program simple(input, output);
    var
        x: integer;
    begin
        read(x);
        write(x)
    end.

Expected Result: ACCEPT

Invalid Programs (for testing error handling):

1. Missing semicolon:
    program test(input, output)
    begin end.
    Error: Expected ; after identifier_list

2. Invalid type:
    var x: float;
    Error: Invalid type specification

3. Missing end:
    begin
        x := 1
    (no end)
    Error: Expected END

4. Invalid expression:
    x := * 5;
    Error: Invalid factor

IMPLEMENTATION NOTES
================================================================================

1. Token Type Mapping:
   - Lexer produces tokens with types like KEYWORD_PROGRAM, ID, NUMBER
   - Grammar symbols match these types for direct comparison
   - Operators have specific token types (PLUS, MINUS, MULTIPLY, etc.)

2. Error Recovery:
   - Recursive descent parser reports first error and stops
   - Predictive parser continues parsing entire table
   - Both provide line/column information for errors

3. Performance:
   - Recursive descent: O(n) where n = input length
   - Predictive parser: O(n) with LL(1) table lookup
   - No backtracking required

4. Grammar Completeness:
   - Supports full Pascal subset from Dragon Book
   - Includes procedures, functions, arrays
   - Supports all basic statements and expressions
   - Handles recursive procedures

REFERENCES
================================================================================

Dragon Book: "Compilers: Principles, Techniques, and Tools"
- Appendix A: Programming Project (Mini Pascal Specification)
- Section 2.3: Syntax Directed Translation
- Section 4.3: LL Parsing (Predictive Parsing)
- Section 4.4: LL(1) Grammars

Aho, Sethi, Ullman (1986) - Original authors

================================================================================
"""
    
    return doc


def create_readme():
    """Create README for the project"""
    
    readme = """# Mini Pascal Compiler - Parser System

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
"""
    
    return readme


def main():
    """Generate and save documentation"""
    
    doc_dir = Path(__file__).parent
    
    # Generate main documentation
    doc = generate_documentation()
    with open(doc_dir / "PARSER_DOCUMENTATION.md", 'w', encoding='utf-8') as f:
        f.write(doc)
    
    # Generate README
    readme = create_readme()
    with open(doc_dir / "README.md", 'w', encoding='utf-8') as f:
        f.write(readme)
    
    print("Documentation generated successfully!")
    print(f"  - PARSER_DOCUMENTATION.md")
    print(f"  - README.md")


if __name__ == '__main__':
    main()
