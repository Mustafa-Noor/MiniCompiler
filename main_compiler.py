#!/usr/bin/env python3
"""
Mini Pascal Compiler - Main Driver
Supports: Recursive Descent, LL(1) Predictive, and SLR(1) Parsers
"""

import sys
import argparse
from pathlib import Path
from typing import Tuple

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from lexer.scanner import Scanner
from lexer.token import TokenType
from parsers.first_follow import create_ll1_grammar, GrammarAnalyzer
from parsers.parsing_table import ParsingTableGenerator
from parsers.recursive_descent import RecursiveDescentParser
from parsers.predictive_parser import PredictiveParser
from lr_parser.lr_parser import SLRParser
from error_handler.error_handler import ErrorHandler, ErrorType
from symbol_table.symbol_table import ScopedSymbolTable
from semantic_analyzer import SemanticAnalyzer


class MiniPascalCompiler:
    """
    Main compiler driver supporting multiple parsing strategies.
    
    Supported parsers:
    - rd: Recursive Descent
    - ll1: LL(1) Predictive
    - slr: SLR(1) Shift-Reduce
    """
    
    def __init__(self, source_file: str, parser_type: str = 'rd', verbose: bool = False):
        """
        Initialize compiler.
        
        Args:
            source_file: Path to .pas file
            parser_type: 'rd', 'll1', or 'slr'
            verbose: Print detailed output
        """
        self.source_file = source_file
        self.parser_type = parser_type.lower()
        self.verbose = verbose
        self.errors = []
        self.trace = ""
        self.success = False
    
    def compile(self) -> Tuple[bool, str]:
        """
        Compile the source file.
        
        Returns:
            Tuple of (success: bool, output: str)
        """
        if self.parser_type == 'rd':
            return self._compile_rd()
        elif self.parser_type == 'll1':
            return self._compile_ll1()
        elif self.parser_type == 'slr':
            return self._compile_slr()
        else:
            return False, f"Unknown parser: {self.parser_type}"
    
    def _compile_rd(self) -> Tuple[bool, str]:
        """Compile using Recursive Descent Parser"""
        output = f"[Recursive Descent Parser]\n{'='*70}\n"
        
        try:
            scanner = Scanner(self.source_file)
            parser = RecursiveDescentParser(scanner)
            
            success = parser.parse_program()
            self.success = success
            self.trace = '\n'.join(parser.trace) if hasattr(parser, 'trace') else ""
            self.errors = parser.errors if hasattr(parser, 'errors') else []
            
            if success:
                output += "Status: ACCEPT\n"
            else:
                output += "Status: REJECT\n"
                if self.errors:
                    output += f"Errors:\n"
                    for error in self.errors:
                        output += f"  {error}\n"
            
            if self.verbose and self.trace:
                output += f"\nTrace:\n{self.trace}\n"
            
            return success, output
        
        except Exception as e:
            return False, f"RD Parser Error: {e}"
    
    def _compile_ll1(self) -> Tuple[bool, str]:
        """Compile using LL(1) Predictive Parser"""
        output = f"[LL(1) Predictive Parser]\n{'='*70}\n"
        
        try:
            # Create scanner
            scanner = Scanner(self.source_file)
            
            # Create and run parser
            parser = PredictiveParser(scanner)
            success, trace, errors = parser.parse()
            self.success = success
            self.trace = trace
            self.errors = errors
            
            if success:
                output += "Status: ACCEPT\n"
            else:
                output += "Status: REJECT\n"
                if self.errors:
                    output += f"Errors:\n"
                    for error in self.errors:
                        output += f"  {error}\n"
            
            if self.verbose and self.trace:
                output += f"\nTrace:\n{self.trace}\n"
            
            return success, output
        
        except Exception as e:
            return False, f"LL(1) Parser Error: {e}"
    
    def _compile_slr(self) -> Tuple[bool, str]:
        """Compile using SLR(1) Shift-Reduce Parser"""
        output = f"[SLR(1) Parser]\n{'='*70}\n"
        
        try:
            # Get tokens
            scanner = Scanner(self.source_file)
            tokens = scanner.scan()
            
            # Create parser
            grammar = create_ll1_grammar()
            analyzer = GrammarAnalyzer(grammar)
            parser = SLRParser(grammar, analyzer)
            
            # Parse
            success, trace, errors = parser.parse(tokens)
            self.success = success
            self.trace = trace
            self.errors = errors
            
            if success:
                output += "Status: ACCEPT\n"
            else:
                output += "Status: REJECT\n"
                if self.errors:
                    output += f"Errors:\n"
                    for error in self.errors:
                        output += f"  {error}\n"
            
            if self.verbose and self.trace:
                output += f"\nTrace:\n{self.trace}\n"
            
            return success, output
        
        except Exception as e:
            return False, f"SLR Parser Error: {e}"


def generate_reports(source_file: str, output_dir: str = 'output') -> None:
    """
    Generate all required reports for the submission.
    
    Creates:
    - First and Follow sets
    - LL(1) parsing table
    - ACTION and GOTO tables
    - Grammar documentation
    """
    print("Generating reports...")
    
    Path(output_dir).mkdir(exist_ok=True)
    
    # Generate grammar analysis
    grammar = create_ll1_grammar()
    analyzer = GrammarAnalyzer(grammar)
    
    # Save FIRST sets
    with open(f'{output_dir}/first_sets.txt', 'w', encoding='utf-8') as f:
        f.write("FIRST Sets\n")
        f.write("=" * 80 + "\n\n")
        for nt in sorted(grammar.keys()):
            first_set = analyzer.get_first_set(nt)
            f.write(f"FIRST({nt}) = {first_set}\n")
    
    # Save FOLLOW sets
    with open(f'{output_dir}/follow_sets.txt', 'w', encoding='utf-8') as f:
        f.write("FOLLOW Sets\n")
        f.write("=" * 80 + "\n\n")
        for nt in sorted(grammar.keys()):
            follow_set = analyzer.get_follow_set(nt)
            f.write(f"FOLLOW({nt}) = {follow_set}\n")
    
    # Save LL(1) table
    table_gen = ParsingTableGenerator(analyzer)
    with open(f'{output_dir}/ll1_table.txt', 'w', encoding='utf-8') as f:
        f.write(table_gen.print_table_detailed())
    
    # Save SLR(1) tables
    slr_parser = SLRParser(grammar, analyzer)
    
    with open(f'{output_dir}/action_table.txt', 'w', encoding='utf-8') as f:
        f.write(slr_parser.print_action_table())
    
    with open(f'{output_dir}/goto_table.txt', 'w', encoding='utf-8') as f:
        f.write(slr_parser.print_goto_table())
    
    print(f"Reports generated in {output_dir}/")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Mini Pascal Compiler with Multiple Parser Support',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py sample.pas --parser rd
  python main.py sample.pas --parser ll1
  python main.py sample.pas --parser slr
  python main.py sample.pas --parser rd --verbose
  python main.py sample.pas --generate-reports
        """
    )
    
    parser.add_argument(
        'source_file',
        help='Pascal source file to compile'
    )
    
    parser.add_argument(
        '--parser',
        choices=['rd', 'll1', 'slr'],
        default='rd',
        help='Parser type (default: rd)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Print verbose output including traces'
    )
    
    parser.add_argument(
        '--generate-reports',
        action='store_true',
        help='Generate all analysis reports'
    )
    
    parser.add_argument(
        '--output-dir',
        default='output',
        help='Output directory for reports (default: output)'
    )
    
    args = parser.parse_args()
    
    # Check file exists
    if not Path(args.source_file).exists():
        print(f"Error: File not found: {args.source_file}", file=sys.stderr)
        sys.exit(1)
    
    # Generate reports if requested
    if args.generate_reports:
        generate_reports(args.source_file, args.output_dir)
        return
    
    # Compile
    compiler = MiniPascalCompiler(
        args.source_file,
        args.parser,
        args.verbose
    )
    
    success, output = compiler.compile()
    
    print(output)
    
    if not success:
        sys.exit(1)


if __name__ == '__main__':
    main()
