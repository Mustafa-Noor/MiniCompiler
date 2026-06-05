"""
Comprehensive Test Suite for Lexical Analyzer
Tests all token types, error handling, and edge cases
"""

import sys
import os
from io import StringIO
from src.lexer import Scanner, LexicalError, TokenType, Token


class TestSuite:
    """Comprehensive test suite for the lexical analyzer"""
    
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
    
    def create_test_file(self, content, filename='test_input.txt'):
        """Create a test file with given content"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        return filename
    
    def test_keywords(self):
        """Test keyword recognition"""
        print("\n" + "="*70)
        print("TEST 1: Keywords Recognition")
        print("="*70)
        
        code = """program var integer real array of 
                 function procedure begin end
                 if then else while do not div mod and or"""
        
        test_file = self.create_test_file(code, 'test_keywords.txt')
        
        try:
            scanner = Scanner(test_file)
            tokens = scanner.scan()
            scanner.close()
            
            # Count keywords
            keywords = [t for t in tokens if t.token_type.startswith('KEYWORD')]
            
            print(f"✓ Found {len(keywords)} keywords")
            for token in keywords[:5]:
                print(f"  {token}")
            print("  ...")
            
            self.tests_passed += 1
        except Exception as e:
            print(f"✗ Failed: {e}")
            self.tests_failed += 1
        finally:
            try:
                os.remove(test_file)
            except:
                pass
        
        self.tests_run += 1
    
    def test_identifiers(self):
        """Test identifier recognition"""
        print("\n" + "="*70)
        print("TEST 2: Identifier Recognition")
        print("="*70)
        
        code = "x y1 myVar _test variable123"
        test_file = self.create_test_file(code, 'test_identifiers.txt')
        
        try:
            scanner = Scanner(test_file)
            tokens = scanner.scan()
            scanner.close()
            
            ids = [t for t in tokens if t.token_type == TokenType.ID]
            
            print(f"✓ Found {len(ids)} identifiers:")
            for token in ids:
                print(f"  {token}")
            
            self.tests_passed += 1
        except Exception as e:
            print(f"✗ Failed: {e}")
            self.tests_failed += 1
        finally:
            try:
                os.remove(test_file)
            except:
                pass
        
        self.tests_run += 1
    
    def test_numbers(self):
        """Test number recognition (integers, reals, scientific notation)"""
        print("\n" + "="*70)
        print("TEST 3: Number Recognition")
        print("="*70)
        
        code = "123 45.67 0 1E10 1.2E-5 9.99E+3"
        test_file = self.create_test_file(code, 'test_numbers.txt')
        
        try:
            scanner = Scanner(test_file)
            tokens = scanner.scan()
            scanner.close()
            
            numbers = [t for t in tokens if t.token_type == TokenType.NUMBER]
            
            print(f"✓ Found {len(numbers)} numbers:")
            for token in numbers:
                print(f"  {token}")
            
            self.tests_passed += 1
        except Exception as e:
            print(f"✗ Failed: {e}")
            self.tests_failed += 1
        finally:
            try:
                os.remove(test_file)
            except:
                pass
        
        self.tests_run += 1
    
    def test_operators(self):
        """Test operator recognition"""
        print("\n" + "="*70)
        print("TEST 4: Operator Recognition")
        print("="*70)
        
        code = "+ - * / = <> < <= > >= := .. div mod and or not"
        test_file = self.create_test_file(code, 'test_operators.txt')
        
        try:
            scanner = Scanner(test_file)
            tokens = scanner.scan()
            scanner.close()
            
            # Filter operators
            operators = [t for t in tokens if t.token_type in [
                TokenType.PLUS, TokenType.MINUS, TokenType.MULTIPLY, 
                TokenType.DIVIDE, TokenType.EQ, TokenType.NEQ, TokenType.LT, 
                TokenType.LE, TokenType.GT, TokenType.GE, TokenType.ASSIGN, 
                TokenType.DOUBLE_DOT
            ]]
            
            print(f"✓ Found {len(operators)} operators:")
            for token in operators:
                print(f"  {token}")
            
            self.tests_passed += 1
        except Exception as e:
            print(f"✗ Failed: {e}")
            self.tests_failed += 1
        finally:
            try:
                os.remove(test_file)
            except:
                pass
        
        self.tests_run += 1
    
    def test_punctuation(self):
        """Test punctuation recognition"""
        print("\n" + "="*70)
        print("TEST 5: Punctuation Recognition")
        print("="*70)
        
        code = "( ) [ ] ; : , . .."
        test_file = self.create_test_file(code, 'test_punctuation.txt')
        
        try:
            scanner = Scanner(test_file)
            tokens = scanner.scan()
            scanner.close()
            
            punct = [t for t in tokens if t.token_type in [
                TokenType.LPAREN, TokenType.RPAREN, TokenType.LBRACKET,
                TokenType.RBRACKET, TokenType.SEMICOLON, TokenType.COLON,
                TokenType.COMMA, TokenType.DOT, TokenType.DOUBLE_DOT
            ]]
            
            print(f"✓ Found {len(punct)} punctuation tokens:")
            for token in punct:
                print(f"  {token}")
            
            self.tests_passed += 1
        except Exception as e:
            print(f"✗ Failed: {e}")
            self.tests_failed += 1
        finally:
            try:
                os.remove(test_file)
            except:
                pass
        
        self.tests_run += 1
    
    def test_comments(self):
        """Test comment handling"""
        print("\n" + "="*70)
        print("TEST 6: Comment Handling")
        print("="*70)
        
        code = """x := 5; { this is a comment }
        y := 10; { another comment }
        z := x + y;"""
        
        test_file = self.create_test_file(code, 'test_comments.txt')
        
        try:
            scanner = Scanner(test_file)
            tokens = scanner.scan()
            scanner.close()
            
            # Comments should not appear in token stream
            has_comments = any('{' in t.lexeme or '}' in t.lexeme for t in tokens)
            
            if not has_comments:
                print("✓ Comments correctly skipped")
                print(f"  Tokens: {len(tokens)} (EOF not counted)")
            else:
                print("✗ Comments not properly skipped")
                self.tests_failed += 1
            
            self.tests_passed += 1
        except Exception as e:
            print(f"✗ Failed: {e}")
            self.tests_failed += 1
        finally:
            try:
                os.remove(test_file)
            except:
                pass
        
        self.tests_run += 1
    
    def test_line_column_tracking(self):
        """Test line and column number tracking"""
        print("\n" + "="*70)
        print("TEST 7: Line and Column Tracking")
        print("="*70)
        
        code = """x := 5;
y := 10;"""
        
        test_file = self.create_test_file(code, 'test_line_col.txt')
        
        try:
            scanner = Scanner(test_file)
            tokens = scanner.scan()
            scanner.close()
            
            # Find 'y' token - should be on line 2
            y_token = None
            for token in tokens:
                if token.lexeme == 'y':
                    y_token = token
                    break
            
            if y_token and y_token.line == 2:
                print(f"✓ Correct line tracking: y at {y_token}")
            else:
                print(f"✗ Incorrect line tracking")
                self.tests_failed += 1
            
            self.tests_passed += 1
        except Exception as e:
            print(f"✗ Failed: {e}")
            self.tests_failed += 1
        finally:
            try:
                os.remove(test_file)
            except:
                pass
        
        self.tests_run += 1
    
    def test_whitespace_handling(self):
        """Test whitespace skipping"""
        print("\n" + "="*70)
        print("TEST 8: Whitespace Handling")
        print("="*70)
        
        code = "   x    :=    5   ;   "
        test_file = self.create_test_file(code, 'test_whitespace.txt')
        
        try:
            scanner = Scanner(test_file)
            tokens = scanner.scan()
            scanner.close()
            
            # Should have: ID, ASSIGN, NUMBER, SEMICOLON, EOF
            expected = [TokenType.ID, TokenType.ASSIGN, TokenType.NUMBER, 
                       TokenType.SEMICOLON, TokenType.EOF]
            actual = [t.token_type for t in tokens]
            
            if actual == expected:
                print("✓ Whitespace correctly skipped")
                for token in tokens[:-1]:  # Exclude EOF
                    print(f"  {token}")
            else:
                print(f"✗ Incorrect token sequence")
                self.tests_failed += 1
            
            self.tests_passed += 1
        except Exception as e:
            print(f"✗ Failed: {e}")
            self.tests_failed += 1
        finally:
            try:
                os.remove(test_file)
            except:
                pass
        
        self.tests_run += 1
    
    def test_complex_program(self):
        """Test a complete Pascal program"""
        print("\n" + "="*70)
        print("TEST 9: Complex Program")
        print("="*70)
        
        code = """program Example;
var
    x, y: integer;
    z: real;
    arr: array [1..100] of integer;
    
begin
    x := 10;
    y := 20;
    z := 3.14159;
    
    if x < y then
        x := x + 1
    else
        x := x - 1;
    
    while x <= 100 do
    begin
        x := x * 2;
        y := y div 2
    end;
    
end."""
        
        test_file = self.create_test_file(code, 'test_complex.txt')
        
        try:
            scanner = Scanner(test_file)
            tokens = scanner.scan()
            scanner.close()
            
            print(f"✓ Successfully parsed complex program")
            print(f"  Total tokens: {len(tokens)}")
            print(f"  First 10 tokens:")
            for token in tokens[:10]:
                print(f"    {token}")
            
            self.tests_passed += 1
        except Exception as e:
            print(f"✗ Failed: {e}")
            self.tests_failed += 1
        finally:
            try:
                os.remove(test_file)
            except:
                pass
        
        self.tests_run += 1
    
    def test_error_handling(self):
        """Test error handling for invalid characters"""
        print("\n" + "="*70)
        print("TEST 10: Error Handling")
        print("="*70)
        
        code = "x := 5 @ 10;"  # @ is invalid
        test_file = self.create_test_file(code, 'test_error.txt')
        
        try:
            scanner = Scanner(test_file)
            try:
                tokens = scanner.scan()
                scanner.close()
            except LexicalError:
                scanner.close()
                raise
            print("✗ Should have raised an error")
            self.tests_failed += 1
        except LexicalError as e:
            print(f"✓ Correctly caught error:")
            print(f"  {e}")
            self.tests_passed += 1
        except Exception as e:
            print(f"✗ Unexpected error: {e}")
            self.tests_failed += 1
        finally:
            try:
                os.remove(test_file)
            except:
                pass
        
        self.tests_run += 1
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "█" * 70)
        print("LEXICAL ANALYZER TEST SUITE")
        print("█" * 70)
        
        self.test_keywords()
        self.test_identifiers()
        self.test_numbers()
        self.test_operators()
        self.test_punctuation()
        self.test_comments()
        self.test_line_column_tracking()
        self.test_whitespace_handling()
        self.test_complex_program()
        self.test_error_handling()
        
        # Summary
        print("\n" + "█" * 70)
        print("TEST SUMMARY")
        print("█" * 70)
        print(f"Total Tests:  {self.tests_run}")
        print(f"Passed:       {self.tests_passed} ✓")
        print(f"Failed:       {self.tests_failed} ✗")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        print("█" * 70 + "\n")
        
        return self.tests_failed == 0


def main():
    """Run the test suite"""
    suite = TestSuite()
    success = suite.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
