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

def test_layout_ops():
    """Test layout operators |, ^, >>, <<."""
    code = "| ^ >> <<"
    tokens = get_tokens(code)
    types = [t.type for t in tokens]
    
    assert types == [TokenType.OP_HOR, TokenType.OP_VER, TokenType.OP_NEST, TokenType.OP_DEEP_NEST]
