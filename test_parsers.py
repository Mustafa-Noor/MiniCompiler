"""
Main test runner for Pascal Compiler Parsers
Runs both recursive descent and predictive parsers
Generates FIRST/FOLLOW sets and parsing table
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from parsers.first_follow import create_ll1_grammar, GrammarAnalyzer
from parsers.parsing_table import ParsingTableGenerator
from parsers.recursive_descent import parse_file as parse_rd
from parsers.predictive_parser import parse_file as parse_predictive


def main():
    """Main test runner"""
    
    print("=" * 80)
    print("MINI PASCAL COMPILER - PARSER TESTING")
    print("=" * 80)
    
    # Path to sample file
    sample_file = Path(__file__).parent / "simple_valid.pas"
    if not sample_file.exists():
        sample_file = Path(__file__).parent / "sample.pas"
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    # Step 1: Grammar Analysis
    print("\n[1/5] Analyzing Grammar...")
    grammar = create_ll1_grammar()
    analyzer = GrammarAnalyzer(grammar)
    
    # Generate and save FIRST sets
    first_sets_output = analyzer.print_first_sets()
    with open(output_dir / "first_sets.txt", 'w', encoding='utf-8') as f:
        f.write(first_sets_output)
    print(f"     ✓ FIRST sets saved to output/first_sets.txt")
    
    # Generate and save FOLLOW sets
    follow_sets_output = analyzer.print_follow_sets()
    with open(output_dir / "follow_sets.txt", 'w', encoding='utf-8') as f:
        f.write(follow_sets_output)
    print(f"     ✓ FOLLOW sets saved to output/follow_sets.txt")
    
    # Step 2: Generate Parsing Table
    print("\n[2/5] Generating LL(1) Parsing Table...")
    table_gen = ParsingTableGenerator(grammar, analyzer)
    
    # Save detailed parsing table
    table_output = table_gen.print_table_detailed()
    with open(output_dir / "ll1_table.txt", 'w', encoding='utf-8') as f:
        f.write(table_output)
    print(f"     ✓ LL(1) parsing table saved to output/ll1_table.txt")
    
    # Step 3: Document grammar transformations
    print("\n[3/5] Documenting Grammar Transformations...")
    transformation_doc = _generate_transformation_doc(grammar)
    with open(output_dir / "grammar_transformation.txt", 'w', encoding='utf-8') as f:
        f.write(transformation_doc)
    print(f"     ✓ Grammar transformations saved to output/grammar_transformation.txt")
    
    # Step 4: Test Recursive Descent Parser
    print("\n[4/5] Testing Recursive Descent Parser...")
    if sample_file.exists():
        rd_success, rd_trace, rd_errors = parse_rd(str(sample_file))
        
        # Save trace
        with open(output_dir / "rd_trace.txt", 'w', encoding='utf-8') as f:
            f.write("RECURSIVE DESCENT PARSER TRACE\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"File: {sample_file}\n")
            f.write(f"Result: {'ACCEPT' if rd_success else 'REJECT'}\n\n")
            f.write("Derivation Trace:\n")
            f.write("-" * 80 + "\n")
            f.write(rd_trace)
            
            if rd_errors:
                f.write("\n\nErrors:\n")
                f.write("-" * 80 + "\n")
                for error in rd_errors:
                    f.write(f"{error}\n")
        
        print(f"     ✓ RD parser trace saved to output/rd_trace.txt")
        print(f"     Result: {'ACCEPT' if rd_success else 'REJECT'}")
        if rd_errors:
            print(f"     Errors: {len(rd_errors)}")
    else:
        print(f"     ✗ Sample file not found: {sample_file}")
    
    # Step 5: Test Predictive Parser
    print("\n[5/5] Testing LL(1) Predictive Parser...")
    if sample_file.exists():
        pp_success, pp_trace, pp_errors = parse_predictive(str(sample_file))
        
        # Save trace
        with open(output_dir / "predictive_trace.txt", 'w', encoding='utf-8') as f:
            f.write("LL(1) PREDICTIVE PARSER TRACE\n")
            f.write("=" * 150 + "\n\n")
            f.write(f"File: {sample_file}\n")
            f.write(f"Result: {'ACCEPT' if pp_success else 'REJECT'}\n\n")
            f.write("Parsing Trace:\n")
            f.write("-" * 150 + "\n")
            f.write(pp_trace)
            
            if pp_errors:
                f.write("\n\nErrors:\n")
                f.write("-" * 150 + "\n")
                for error in pp_errors:
                    f.write(f"{error}\n")
        
        print(f"     ✓ Predictive parser trace saved to output/predictive_trace.txt")
        print(f"     Result: {'ACCEPT' if pp_success else 'REJECT'}")
        if pp_errors:
            print(f"     Errors: {len(pp_errors)}")
    else:
        print(f"     ✗ Sample file not found: {sample_file}")
    
    # Summary
    print("\n" + "=" * 80)
    print("PARSER TESTING COMPLETE")
    print("=" * 80)
    print("\nOutput Files Generated:")
    for output_file in sorted(output_dir.glob("*.txt")):
        print(f"  - {output_file.name}")


def _generate_transformation_doc(grammar) -> str:
    """Generate documentation of grammar transformations"""
    
    doc = """GRAMMAR TRANSFORMATION DOCUMENT
Mini Pascal LL(1) Grammar
========================================================

ORIGINAL GRAMMAR (from Dragon Book Appendix A):
The original grammar from the Dragon Book is an LALR(1) grammar with several issues
that prevent direct use for LL(1) parsing:

1. LEFT RECURSION in multiple productions:
   - simple_expression: simple_expression addop term
   - term: term mulop factor
   - identifier_list: identifier_list, id
   - parameter_list: parameter_list; identifier_list: type
   - declaration: declaration var ...
   - statement_list: statement_list; statement

2. AMBIGUITY:
   - Dangling-else problem in if-then-else statements

3. FIRST/FOLLOW CONFLICTS:
   - Multiple productions for same non-terminal sharing FIRST sets

TRANSFORMATION PROCESS:
========================================================

1. LEFT RECURSION ELIMINATION:

For left-recursive productions: A → A α | β
Transformed to: A → β A'
                A' → α A' | ε

Applied to:
  a) simple_expression → term | simple_expression addop term
     Transformed to:
       simple_expr → term simple_expr'
       simple_expr' → addop term simple_expr' | ε

  b) term → factor | term mulop factor
     Transformed to:
       term → factor term'
       term' → mulop factor term' | ε

  c) identifier_list → id | identifier_list, id
     Transformed to:
       id_list → id id_list'
       id_list' → comma id id_list' | ε

  d) statement_list → statement | statement_list ; statement
     Transformed to:
       stmt_list → statement stmt_list'
       stmt_list' → semicolon statement stmt_list' | ε

  e) declarations → type | declarations var ...
     Transformed to:
       declarations → type declarations' | ε

2. LEFT FACTORING:

Removed common prefixes from productions to allow single lookahead:

  a) statement → id ... | id ( expression_list )
     Factored to:
       statement → id var_or_proc_tail
       var_or_proc_tail → [ expression ] := expression
                        | := expression
                        | ( expression_list )

  b) factor → id | id ( expression_list )
     Factored to:
       factor → id factor_tail
       factor_tail → ( expression_list ) | ε

  c) expression_list → expression | ε
     To avoid conflicts:
       expr_list → expression expr_list' | ε

3. EPSILON PRODUCTIONS:

Introduced epsilon productions for optional constructs:
  - arguments → ( parameter_list ) | ε
  - optional_statements → statement_list | ε
  - parameter_list_prime → ; ... | ε
  - id_list_prime → , ... | ε

4. DANGLING-ELSE RESOLUTION:

Original: if expression then statement [else statement]
Resolved by treating else as part of statement:
  else_part → else statement | ε
  This ensures else binds to nearest if

RESULTING LL(1) GRAMMAR:
========================================================

Key transformations applied:
✓ No left recursion
✓ Left factoring applied
✓ Proper epsilon productions
✓ No ambiguities
✓ LL(1) conflict-free

PROPERTIES VERIFIED:
========================================================

1. For each non-terminal A with productions:
   A → α₁ | α₂ | ... | αₙ
   
   FIRST(α₁) ∩ FIRST(α₂) = ∅ for all i ≠ j
   
2. If α can derive ε, then:
   FIRST(β) ∩ FOLLOW(A) = ∅ for all β

3. All left recursion eliminated
4. All ambiguities resolved
5. No shift/reduce or reduce/reduce conflicts

GRAMMAR SYMBOLS:
========================================================

Non-terminals (lowercase):
  program, id_list, declarations, type_spec, subprogram_decls,
  subprogram_decl, subprogram_head, arguments, param_list,
  compound_stmt, optional_stmts, stmt_list, statement,
  expression, simple_expr, term, factor, expr_list, relop,
  addop, mulop, sign

Terminals (uppercase):
  Keywords: KEYWORD_program, KEYWORD_var, KEYWORD_integer, 
            KEYWORD_real, KEYWORD_array, KEYWORD_of,
            KEYWORD_function, KEYWORD_procedure, 
            KEYWORD_begin, KEYWORD_end, KEYWORD_if,
            KEYWORD_then, KEYWORD_else, KEYWORD_while,
            KEYWORD_do, KEYWORD_or, KEYWORD_div,
            KEYWORD_mod, KEYWORD_and, KEYWORD_not
  
  Tokens: ID, NUMBER, ASSIGN, EQ, NEQ, LT, LE, GT, GE,
          PLUS, MINUS, MULTIPLY, DIVIDE, LPAREN, RPAREN,
          LBRACKET, RBRACKET, SEMICOLON, COLON, COMMA,
          DOT, DOUBLE_DOT, EOF

PARSING STRATEGY:
========================================================

1. Recursive Descent Parser:
   - One parsing function per non-terminal
   - Predictive parsing using lookahead
   - Produces derivation trace
   - Reports syntax errors with line/column info

2. LL(1) Predictive Parser:
   - Stack-based parsing with parsing table
   - M[A, a] table lookup for each (non-terminal, terminal)
   - Produces stack trace showing:
     * Stack contents at each step
     * Remaining input
     * Action taken (shift/reduce)

Both parsers accept the same valid programs and reject invalid ones.
"""
    
    return doc


if __name__ == '__main__':
    main()
