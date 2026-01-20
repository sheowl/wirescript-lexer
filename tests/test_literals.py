import pytest
from wirescript.lexer.lexer import Lexer
from wirescript.lexer.tokens import TokenType, Token

def get_tokens(code):
    lexer = Lexer(code)
    tokens = []
    while True:
        tok = lexer.get_next_token()
        if tok.type == TokenType.EOF:
            break
        tokens.append(tok)
    return tokens

def test_integers():
    """Test integer literals."""
    code = "123 0 999"
    tokens = get_tokens(code)
    
    assert len(tokens) == 3
    assert tokens[0].type == TokenType.INTEGER
    assert tokens[0].value == 123
    assert tokens[1].value == 0
    assert tokens[2].value == 999

def test_floats():
    """Test float literals."""
    code = "3.14 0.5 10.0"
    tokens = get_tokens(code)
    
    # We might reuse INTEGER tokens for numbers if generic, but TokenTypes has INTEGER.
    # Spec doesn't explicitly listed FLOAT in tokens.py, only INTEGER.
    # But examples show 0.5.
    # Let's check tokens.py.
    # If no FLOAT, we might need to add it or just use INTEGER for all numbers (bad idea).
    # I'll check tokens.py content in a second. Assuming we need to add FLOAT.
    
    # Asserting types assuming I'll add FLOAT or use a generic NUMBER type.
    # Existing tokens.py had INTEGER. I will likely need to add FLOAT.
    assert tokens[0].value == 3.14
    assert tokens[1].value == 0.5

def test_string_double():
    """Test double quoted strings."""
    code = '"Hello World"'
    tokens = get_tokens(code)
    
    assert len(tokens) == 1
    assert tokens[0].type == TokenType.STRING
    assert tokens[0].value == "Hello World"

def test_string_single():
    """Test single quoted strings."""
    code = "'Single'"
    tokens = get_tokens(code)
    
    assert len(tokens) == 1
    assert tokens[0].type == TokenType.STRING
    assert tokens[0].value == "Single"

def test_mixed_expression():
    """Test assignment with literals."""
    code = 'val = 50 * 2.5'
    tokens = get_tokens(code)
    # ID, EQ, INT, MUL, FLOAT (or NUMBER)
    assert tokens[0].type == TokenType.IDENTIFIER
    assert tokens[2].value == 50
    assert tokens[4].value == 2.5
