"""
Main Lexical Analyzer Driver for Mini Pascal Compiler

This script reads a Pascal source file, performs lexical analysis,
and outputs the token stream to a file.
"""

import sys
import os
from pathlib import Path
from src.lexer import Scanner, LexicalError, TokenType


def format_token_stream(tokens, style='compact'):
    """
    Format tokens for output
    
    Args:
        tokens (list): List of Token objects
        style (str): 'compact' or 'detailed'
        
    Returns:
        str: Formatted token string
    """
    if style == 'compact':
        return '\n'.join(str(token) for token in tokens)
    else:
        lines = []
        lines.append("Token Stream:")
        lines.append("=" * 70)
        for token in tokens:
            lines.append(
                f"Type: {token.token_type:20} "
                f"Lexeme: {token.lexeme:15} "
                f"Line: {token.line:4} Column: {token.column:4}"
            )
        lines.append("=" * 70)
        return '\n'.join(lines)


def analyze_source(source_file, output_file='output/tokens.txt', verbose=True):
    """
    Analyze a Pascal source file and save token stream
    
    Args:
        source_file (str): Path to source Pascal file
        output_file (str): Path to output tokens file
        verbose (bool): Print output to console
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not os.path.exists(source_file):
        print(f"Error: Source file '{source_file}' not found")
        return False
    
    try:
        print(f"Lexical Analysis: {source_file}")
        print("-" * 70)
        
        # Create scanner
        scanner = Scanner(source_file)
        
        # Scan all tokens
        tokens = scanner.scan()
        
        # Create output directory if needed
        os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', 
                   exist_ok=True)
        
        # Write tokens to output file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(format_token_stream(tokens, 'compact'))
        
        if verbose:
            print(format_token_stream(tokens, 'detailed'))
            print()
            print(f"Total tokens: {len(tokens)}")
            print(f"Output saved to: {output_file}")
        
        scanner.close()
        return True
    
    except LexicalError as e:
        print(f"Lexical Error: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def create_sample_pascal_file(filename='pascal.txt'):
    """
    Create a sample Pascal program for testing
    
    Args:
        filename (str): Name of file to create
    """
    sample_code = """program HelloWorld;
var
    x: integer;
    y: real;
    arr: array [1..10] of integer;
    
begin
    { This is a comment }
    x := 42;
    y := 3.14;
    
    if x > 0 then
        x := x + 1
    else
        x := x - 1;
    
    while x < 100 do
        x := x * 2;
    
    if (x = 10) and (y > 0) then
        y := y / 2
    else
        y := y mod 3;
        
end.
"""
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(sample_code)
    
    print(f"Sample Pascal program created: {filename}")


def main():
    """Main entry point"""
    
    # Get source file from command line or use default
    if len(sys.argv) > 1:
        source_file = sys.argv[1]
    else:
        source_file = 'pascal.txt'
    
    # Analyze the source file
    success = analyze_source(source_file)
    
    if not success:
        sys.exit(1)


if __name__ == '__main__':
    main()
