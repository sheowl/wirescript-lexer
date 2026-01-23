import pytest
from wirescript.lexer.lexer import Lexer
from wirescript.lexer.tokens import TokenType

def get_tokens(code):
    lexer = Lexer(code)
    tokens = []
    while True:
        tok = lexer.get_next_token()
        if tok.type == TokenType.EOF:
            break
        tokens.append(tok)
    return tokens

def test_complex_wirescript_program():
    """
    Tests a complete (mock) WireScript program including:
    - Comments (single/multi)
    - Keywords & Identifiers
    - Noise Words (skipped)
    - Indentation
    - Literals (Int, Float, String, Boolean)
    - Operators & Assignments
    """
    code = """
    # This is a test program
    define calculate_score using base, bonus:
        \"\"\"
        Calculates total score
        Returns final int check
        \"\"\"
        make total with base + bonus
        
        if total >= 100:
            print "High Score"
            return true
        elif total > 50:
            set result to total * 1.5
            return result
        else:
            return false
    """
    tokens = get_tokens(code)
    
    import inspect
    code = inspect.cleandoc(code) 
    
    tokens = get_tokens(code)
    
    current = 0
    while tokens[current].type == TokenType.NEWLINE:
        current += 1
        
    assert tokens[current].type == TokenType.KW_DEFINE
    assert tokens[current+1].type == TokenType.IDENTIFIER
    assert tokens[current+1].value == "calculate_score"
    
    indent_token = None
    for t in tokens:
        if t.type == TokenType.INDENT:
            indent_token = t
            break
    assert indent_token is not None, "Should have found an INDENT token"
    
    found_make = False
    found_with = False
    total_token_idx = -1
    
    for i, t in enumerate(tokens):
        if t.value == "make": found_make = True
        if t.value == "with": found_with = True
        if t.value == "total" and t.type == TokenType.IDENTIFIER:
            total_token_idx = i
            
    assert not found_make, "'make' should be skipped as noise"
    assert not found_with, "'with' should be skipped as noise"
    assert total_token_idx != -1
    
    found_float = False
    for t in tokens:
        if t.type == TokenType.FLOAT and t.value == 1.5:
            found_float = True
    assert found_float, "Should detect float 1.5"
    
    found_string = False
    for t in tokens:
        if t.type == TokenType.STRING and t.value == "High Score":
            found_string = True
    assert found_string, "Should detect string 'High Score'"

    found_bool = False
    for t in tokens:
        if t.type == TokenType.BOOLEAN:
            found_bool = True
    assert found_bool, "Should detect boolean literal"

