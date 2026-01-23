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

def test_simple_indent():
    code = "start\n  next"
    tokens = get_tokens(code)
    types = [t.type for t in tokens]
    
    assert TokenType.NEWLINE in types
    assert TokenType.INDENT in types
    
    # Precise order: NEWLINE -> INDENT
    nl_index = types.index(TokenType.NEWLINE)
    assert types[nl_index + 1] == TokenType.INDENT

def test_dedent_logic():
    code = "\n  x\n"
    tokens = get_tokens(code)
    types = [t.type for t in tokens]
    
    # Filter only relevant tokens for this check
    relevant = [t for t in types if t in (TokenType.NEWLINE, TokenType.INDENT, TokenType.DEDENT)]
    assert relevant == [TokenType.NEWLINE, TokenType.INDENT, TokenType.NEWLINE, TokenType.DEDENT]
