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

def test_unexpected_character():
    """Test that unknown characters emit ERROR tokens."""
    code = "x = @ 5"
    tokens = get_tokens(code)
    types = [t.type for t in tokens]
    
    assert TokenType.ERROR in types
    error_token = next(t for t in tokens if t.type == TokenType.ERROR)
    assert error_token.value == "Unexpected character '@'"

def test_unterminated_string_double():
    """Test string starting with double quote but hitting newline."""
    code = 's = "hello' # Missing closing quote
    tokens = get_tokens(code)
    # The lexer should emit ERROR when it hits newline/EOF
    assert tokens[-1].type == TokenType.ERROR
    assert tokens[-1].value == "Unterminated string literal"

def test_unterminated_string_single():
    """Test string starting with single quote but hitting newline."""
    code = "s = 'hello" 
    tokens = get_tokens(code)
    assert tokens[-1].type == TokenType.ERROR
    assert tokens[-1].value == "Unterminated string literal"

def test_unterminated_multiline_comment():
    """Test triple quote not closed before EOF."""
    code = '""" this is a comment that never ends'
    tokens = get_tokens(code)
    # Should emit ERROR at EOF
    assert len(tokens) == 1
    assert tokens[0].type == TokenType.ERROR
    assert tokens[0].value == "Unterminated multi-line comment"

def test_error_recovery():
    """Test that lexer continues after error."""
    code = "@ $"
    tokens = get_tokens(code)
    # Should be ERROR(@), ERROR($)
    assert len(tokens) == 2
    assert tokens[0].type == TokenType.ERROR
    assert tokens[1].type == TokenType.ERROR
