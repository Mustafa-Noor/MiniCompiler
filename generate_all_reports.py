#!/usr/bin/env python3
"""
Generate all required reports for viva submission
Produces: FIRST, FOLLOW, LL(1) table, ACTION/GOTO tables, and sample traces
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from lexer.scanner import Scanner
from parsers.first_follow import create_ll1_grammar, GrammarAnalyzer
from parsers.parsing_table import ParsingTableGenerator
from parsers.recursive_descent import RecursiveDescentParser
from parsers.predictive_parser import PredictiveParser
from lr_parser.lr_parser import SLRParser
from error_handler.error_handler import ErrorHandler
from symbol_table.symbol_table import ScopedSymbolTable
from symbol_table.symbol import DataType


def generate_all_reports(output_dir: str = 'output') -> None:
    """Generate all required reports"""
    
    Path(output_dir).mkdir(exist_ok=True)
    
    print("[1/9] Generating FIRST sets...")
    generate_first_sets(output_dir)
    print("     -> first_sets.txt")
    
    print("[2/9] Generating FOLLOW sets...")
    generate_follow_sets(output_dir)
    print("     -> follow_sets.txt")
    
    print("[3/9] Generating LL(1) parsing table...")
    generate_ll1_table(output_dir)
    print("     -> ll1_table.txt")
    
    print("[4/9] Generating ACTION table...")
    print("[5/9] Generating GOTO table...")
    generate_slr_tables(output_dir)
    print("     -> action_table.txt")
    print("     -> goto_table.txt")
    
    print("[6/9] Generating RD parser trace...")
    generate_rd_trace(output_dir)
    print("     -> rd_trace.txt")
    
    print("[7/9] Generating Predictive parser trace...")
    generate_predictive_trace(output_dir)
    print("     -> predictive_trace.txt")
    
    print("[8/9] Generating SLR(1) parser trace...")
    generate_slr_trace(output_dir)
    print("     -> slr_trace.txt")
    
    print("[9/9] Generating symbol table dump...")
    generate_symbol_table_dump(output_dir)
    print("     -> symbol_table.txt")
    
    print("\n" + "="*70)
    print("All reports generated successfully!")
    print("="*70)
    print(f"\nOutput files in: {output_dir}/")
    print("Files created:")
    for f in sorted(Path(output_dir).glob("*.txt")):
        size = f.stat().st_size
        print(f"  - {f.name:30s} ({size:,d} bytes)")


def generate_first_sets(output_dir: str) -> None:
    """Generate FIRST sets"""
    grammar = create_ll1_grammar()
    analyzer = GrammarAnalyzer(grammar)
    
    output = "FIRST Sets\n"
    output += "=" * 80 + "\n\n"
    output += "FIRST(X) = {terminals that can appear first in any derivation from X}\n\n"
    
    for nt in sorted(grammar.keys()):
        first_set = analyzer.get_first_set(nt)
        output += f"FIRST({nt:20s}) = {first_set}\n"
    
    output += "\n" + "=" * 80 + "\n"
    output += f"Total non-terminals: {len(grammar)}\n"
    
    with open(f'{output_dir}/first_sets.txt', 'w', encoding='utf-8') as f:
        f.write(output)


def generate_follow_sets(output_dir: str) -> None:
    """Generate FOLLOW sets"""
    grammar = create_ll1_grammar()
    analyzer = GrammarAnalyzer(grammar)
    
    output = "FOLLOW Sets\n"
    output += "=" * 80 + "\n\n"
    output += "FOLLOW(X) = {terminals that can appear after X in any derivation}\n\n"
    
    for nt in sorted(grammar.keys()):
        follow_set = analyzer.get_follow_set(nt)
        output += f"FOLLOW({nt:20s}) = {follow_set}\n"
    
    output += "\n" + "=" * 80 + "\n"
    output += f"Total non-terminals: {len(grammar)}\n"
    
    with open(f'{output_dir}/follow_sets.txt', 'w', encoding='utf-8') as f:
        f.write(output)


def generate_ll1_table(output_dir: str) -> None:
    """Generate LL(1) M[A, a] table"""
    grammar = create_ll1_grammar()
    analyzer = GrammarAnalyzer(grammar)
    table_gen = ParsingTableGenerator(grammar, analyzer)
    
    with open(f'{output_dir}/ll1_table.txt', 'w', encoding='utf-8') as f:
        f.write(table_gen.print_table_detailed())


def generate_slr_tables(output_dir: str) -> None:
    """Generate SLR(1) ACTION and GOTO tables"""
    grammar = create_ll1_grammar()
    analyzer = GrammarAnalyzer(grammar)
    parser = SLRParser(grammar, analyzer)
    
    with open(f'{output_dir}/action_table.txt', 'w', encoding='utf-8') as f:
        f.write(parser.print_action_table())
    
    with open(f'{output_dir}/goto_table.txt', 'w', encoding='utf-8') as f:
        f.write(parser.print_goto_table())


def generate_rd_trace(output_dir: str) -> None:
    """Generate Recursive Descent parser trace"""
    output = "Recursive Descent Parser Trace\n"
    output += "=" * 80 + "\n\n"
    output += "File: simple_valid.pas\n"
    output += "-" * 80 + "\n\n"
    
    try:
        scanner = Scanner('simple_valid.pas')
        parser = RecursiveDescentParser(scanner)
        success = parser.parse_program()
        
        output += "Result: " + ("ACCEPT" if success else "REJECT") + "\n\n"
        output += "Derivation Trace:\n"
        output += "\n".join(parser.trace[:100]) + "\n"  # First 100 lines
        
        if len(parser.trace) > 100:
            output += f"\n... ({len(parser.trace) - 100} more lines) ...\n"
        
    except Exception as e:
        output += f"Error: {e}\n"
    
    with open(f'{output_dir}/rd_trace.txt', 'w', encoding='utf-8') as f:
        f.write(output)


def generate_predictive_trace(output_dir: str) -> None:
    """Generate LL(1) Predictive parser trace"""
    output = "LL(1) Predictive Parser Trace\n"
    output += "=" * 80 + "\n\n"
    output += "File: simple_valid.pas\n"
    output += "-" * 80 + "\n\n"
    
    try:
        scanner = Scanner('simple_valid.pas')
        parser = PredictiveParser(scanner)
        success, trace, errors = parser.parse()
        
        output += "Result: " + ("ACCEPT" if success else "REJECT") + "\n\n"
        output += "Parsing Trace:\n"
        output += trace[:2000] + "\n"  # First 2000 chars
        
        if len(trace) > 2000:
            output += f"\n... (trace truncated) ...\n"
        
    except Exception as e:
        output += f"Error: {e}\n"
    
    with open(f'{output_dir}/predictive_trace.txt', 'w', encoding='utf-8') as f:
        f.write(output)


def generate_slr_trace(output_dir: str) -> None:
    """Generate SLR(1) parser trace"""
    output = "SLR(1) Parser Trace\n"
    output += "=" * 80 + "\n\n"
    output += "File: simple_valid.pas\n"
    output += "-" * 80 + "\n\n"
    
    try:
        scanner = Scanner('simple_valid.pas')
        tokens = scanner.scan()
        
        grammar = create_ll1_grammar()
        analyzer = GrammarAnalyzer(grammar)
        parser = SLRParser(grammar, analyzer)
        
        success, trace, errors = parser.parse(tokens)
        
        output += "Result: " + ("ACCEPT" if success else "REJECT") + "\n\n"
        output += "Shift-Reduce Trace:\n"
        output += trace[:2000] + "\n"  # First 2000 chars
        
        if len(trace) > 2000:
            output += f"\n... (trace truncated) ...\n"
        
        if errors:
            output += "\nErrors:\n"
            for error in errors:
                output += f"  {error}\n"
        
    except Exception as e:
        output += f"Error: {e}\n"
    
    with open(f'{output_dir}/slr_trace.txt', 'w', encoding='utf-8') as f:
        f.write(output)


def generate_symbol_table_dump(output_dir: str) -> None:
    """Generate symbol table example"""
    from semantic_analyzer import SemanticAnalyzer
    
    output = "Symbol Table Example\n"
    output += "=" * 80 + "\n\n"
    
    # Create example symbol table
    eh = ErrorHandler()
    sa = SemanticAnalyzer(eh)
    
    # Global scope
    sa.declare_variable("x", DataType.INTEGER, 1, 5)
    sa.declare_variable("y", DataType.REAL, 2, 5)
    sa.declare_function("compute", DataType.REAL, 4, 1)
    
    # Function scope
    sa.enter_scope()
    sa.declare_variable("result", DataType.REAL, 5, 10)
    sa.declare_variable("temp", DataType.INTEGER, 6, 10)
    
    output += sa.symbol_table.print_table()
    
    output += "\n" + "=" * 80 + "\n"
    output += "Symbol Table Statistics:\n"
    stats = sa.symbol_table.table.get_statistics()
    for key, value in stats.items():
        output += f"  {key}: {value}\n"
    
    with open(f'{output_dir}/symbol_table.txt', 'w', encoding='utf-8') as f:
        f.write(output)


def generate_error_report(output_dir: str) -> None:
    """Generate error handling example"""
    output = "Error Handling Example\n"
    output += "=" * 80 + "\n\n"
    
    eh = ErrorHandler()
    
    # Add various errors
    eh.add_lexical_error(1, 5, "Invalid character: @", "@")
    eh.add_syntax_error(2, 10, "Expected semicolon", ";", "x")
    eh.add_semantic_error(3, 15, "Undeclared identifier", "foo", "Undefined")
    eh.add_type_error(4, 8, "Type mismatch", "integer", "real")
    
    output += eh.print_errors()
    
    with open(f'{output_dir}/errors_example.txt', 'w', encoding='utf-8') as f:
        f.write(output)


if __name__ == '__main__':
    generate_all_reports()
