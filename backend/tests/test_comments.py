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

def test_single_line_comment():
    """Test standard # comments."""
    code = "# This is a comment\nx = 1"
    tokens = get_tokens(code)
    assert tokens[0].type == TokenType.NEWLINE
    assert tokens[1].value == "x"
    assert tokens[3].value == 1

def test_inline_comment():
    """Test comment at end of line."""
    code = "x = 1 # Inline comment"
    tokens = get_tokens(code)
    assert len(tokens) == 3
    assert tokens[0].value == "x"
    assert tokens[2].value == 1

def test_multi_line_comment():
    """Test triple quoted comment."""
    code = '"""\nThis is a\nmulti-line comment\n"""\nx'
    tokens = get_tokens(code)
    assert len(tokens) == 2 
    assert tokens[-1].value == "x"

def test_comment_only_file():
    """File with only comments."""
    code = "# Just a comment"
    tokens = get_tokens(code)
    assert len(tokens) == 0 # Just EOF
