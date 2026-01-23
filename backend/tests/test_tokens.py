import pytest
from wirescript.lexer.tokens import TokenType, Token

def test_token_creation():
    """Test basic Token instantiation."""
    tok = Token(TokenType.IDENTIFIER, "myVar", 10, 5)
    assert tok.type == TokenType.IDENTIFIER
    assert tok.value == "myVar"
    assert tok.line == 10
    assert tok.column == 5

def test_token_repr():
    """Test string representation of Token."""
    tok = Token(TokenType.KW_START, line=1, column=1)
    assert "Token(KW_START, line=1, col=1)" in repr(tok)
    
    tok_val = Token(TokenType.INTEGER, 123, 2, 4)
    assert "Token(INTEGER, value=123, line=2, col=4)" in repr(tok_val)

def test_keywords_existence():
    """Verify essential keywords exist in TokenType."""
    assert TokenType.KW_START
    assert TokenType.KW_IF
    assert TokenType.KW_RENDER

def test_operators_existence():
    """Verify essential operators exist in TokenType."""
    assert TokenType.OP_HOR  # |
    assert TokenType.OP_NEST # >>
    assert TokenType.OP_EQ   # ==
