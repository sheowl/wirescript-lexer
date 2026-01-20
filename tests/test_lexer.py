import pytest
from wirescript.lexer.lexer import Lexer
from wirescript.lexer.tokens import TokenType

def test_lexer_initialization():
    """Verify lexer starts with correct default state."""
    lexer = Lexer("some code")
    assert lexer.pos == 0
    assert lexer.line == 1
    assert lexer.column == 1
    # Check private state if needed, or just public interface

def test_lexer_empty_eof():
    """Verify an empty string immediately returns EOF."""
    lexer = Lexer("")
    token = lexer.get_next_token()
    assert token.type == TokenType.EOF

def test_lexer_skip_unknown():
    """
    Feature 1 placeholder behavior: 
    Should consume characters and eventually return EOF 
    (since we haven't implemented other tokens yet).
    """
    lexer = Lexer("???")
    # First call: consumes '?', returns None internal -> loop -> same for '?' -> EOF
    token = lexer.get_next_token()
    assert token.type == TokenType.EOF
