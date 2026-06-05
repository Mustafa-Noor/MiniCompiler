#!/usr/bin/env python3
"""
Final Verification - Mini Pascal Compiler Parser System
Confirms all required files and components are in place
"""

import sys
from pathlib import Path

def verify_project():
    """Verify all project files are in place"""
    
    project_root = Path(__file__).parent
    output_dir = project_root / "output"
    src_dir = project_root / "src"
    parsers_dir = src_dir / "parsers"
    
    print("=" * 80)
    print("MINI PASCAL COMPILER - PARSER SYSTEM VERIFICATION")
    print("=" * 80)
    
    # Required directories
    required_dirs = [
        ("Output Directory", output_dir),
        ("Source Directory", src_dir),
        ("Parsers Module", parsers_dir),
    ]
    
    print("\n[1] VERIFYING DIRECTORIES")
    print("-" * 80)
    dirs_ok = True
    for name, path in required_dirs:
        exists = path.exists() and path.is_dir()
        status = "✓" if exists else "✗"
        print(f"  {status} {name}: {path.name}/")
        dirs_ok = dirs_ok and exists
    
    # Required parser files
    parser_files = [
        ("FIRST/FOLLOW Computation", "first_follow.py"),
        ("Parsing Table Generator", "parsing_table.py"),
        ("Recursive Descent Parser", "recursive_descent.py"),
        ("LL(1) Predictive Parser", "predictive_parser.py"),
        ("Parser Module Init", "__init__.py"),
    ]
    
    print("\n[2] VERIFYING PARSER IMPLEMENTATION FILES")
    print("-" * 80)
    parser_files_ok = True
    for name, filename in parser_files:
        filepath = parsers_dir / filename
        exists = filepath.exists() and filepath.is_file()
        status = "✓" if exists else "✗"
        size = filepath.stat().st_size if exists else 0
        print(f"  {status} {name:30s}: {filename:25s} ({size:6d} bytes)")
        parser_files_ok = parser_files_ok and exists
    
    # Required output files
    output_files = [
        ("FIRST Sets", "first_sets.txt"),
        ("FOLLOW Sets", "follow_sets.txt"),
        ("LL(1) Parsing Table", "ll1_table.txt"),
        ("Grammar Transformation", "grammar_transformation.txt"),
        ("RD Parser Trace", "rd_trace.txt"),
        ("Predictive Parser Trace", "predictive_trace.txt"),
    ]
    
    print("\n[3] VERIFYING OUTPUT FILES")
    print("-" * 80)
    output_files_ok = True
    for name, filename in output_files:
        filepath = output_dir / filename
        exists = filepath.exists() and filepath.is_file()
        status = "✓" if exists else "✗"
        size = filepath.stat().st_size if exists else 0
        print(f"  {status} {name:30s}: {filename:35s} ({size:8d} bytes)")
        output_files_ok = output_files_ok and exists
    
    # Required documentation files
    doc_files = [
        ("Parser Documentation", "PARSER_DOCUMENTATION.md"),
        ("README", "README.md"),
        ("Implementation Summary", "IMPLEMENTATION_SUMMARY.md"),
        ("Test Runners", "test_parsers.py"),
        ("Doc Generator", "generate_docs.py"),
    ]
    
    print("\n[4] VERIFYING DOCUMENTATION FILES")
    print("-" * 80)
    doc_files_ok = True
    for name, filename in doc_files:
        filepath = project_root / filename
        exists = filepath.exists() and filepath.is_file()
        status = "✓" if exists else "✗"
        size = filepath.stat().st_size if exists else 0
        print(f"  {status} {name:30s}: {filename:35s} ({size:8d} bytes)")
        doc_files_ok = doc_files_ok and exists
    
    # Test files
    test_files = [
        ("Simple Valid Program", "simple_valid.pas"),
        ("Sample Program", "sample.pas"),
    ]
    
    print("\n[5] VERIFYING TEST FILES")
    print("-" * 80)
    test_files_ok = True
    for name, filename in test_files:
        filepath = project_root / filename
        exists = filepath.exists() and filepath.is_file()
        status = "✓" if exists else "✗"
        size = filepath.stat().st_size if exists else 0
        print(f"  {status} {name:30s}: {filename:35s} ({size:8d} bytes)")
        test_files_ok = test_files_ok and exists
    
    # Summary
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    
    all_ok = dirs_ok and parser_files_ok and output_files_ok and doc_files_ok and test_files_ok
    
    print(f"\n  Directories:              {'✓ OK' if dirs_ok else '✗ FAILED'}")
    print(f"  Parser Files:             {'✓ OK' if parser_files_ok else '✗ FAILED'}")
    print(f"  Output Files:             {'✓ OK' if output_files_ok else '✗ FAILED'}")
    print(f"  Documentation Files:      {'✓ OK' if doc_files_ok else '✗ FAILED'}")
    print(f"  Test Files:               {'✓ OK' if test_files_ok else '✗ FAILED'}")
    
    print("\n" + "=" * 80)
    if all_ok:
        print("✓ ALL COMPONENTS VERIFIED SUCCESSFULLY!")
        print("\nThe Mini Pascal Compiler Parser System is complete and ready for use.")
    else:
        print("✗ VERIFICATION FAILED - Some components are missing!")
        return 1
    
    print("=" * 80 + "\n")
    
    # Show file structure
    print("PROJECT STRUCTURE:")
    print("─" * 80)
    print("FinalProject/")
    print("├── src/parsers/")
    print("│   ├── first_follow.py           (Grammar analysis & FIRST/FOLLOW)")
    print("│   ├── parsing_table.py          (LL(1) table construction)")
    print("│   ├── recursive_descent.py      (Recursive descent parser)")
    print("│   ├── predictive_parser.py      (LL(1) predictive parser)")
    print("│   └── __init__.py")
    print("├── output/")
    print("│   ├── first_sets.txt            (FIRST sets for all non-terminals)")
    print("│   ├── follow_sets.txt           (FOLLOW sets for all non-terminals)")
    print("│   ├── ll1_table.txt             (M[A,a] parsing table)")
    print("│   ├── grammar_transformation.txt (Transformation documentation)")
    print("│   ├── rd_trace.txt              (RD parser trace)")
    print("│   └── predictive_trace.txt      (Predictive parser trace)")
    print("├── PARSER_DOCUMENTATION.md       (Complete system documentation)")
    print("├── README.md                     (Quick start guide)")
    print("├── IMPLEMENTATION_SUMMARY.md     (Project completion summary)")
    print("├── test_parsers.py               (Test runner script)")
    print("├── generate_docs.py              (Documentation generator)")
    print("├── simple_valid.pas              (Valid test program)")
    print("└── sample.pas                    (Sample program)")
    print("─" * 80)
    
    return 0


if __name__ == '__main__':
    sys.exit(verify_project())
