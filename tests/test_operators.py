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

def test_single_char_ops():
    """Test simple operators like +, -, (, )."""
    code = "+ - ( )"
    tokens = get_tokens(code)
    types = [t.type for t in tokens]
    # Spaces are currently skipped in _handle_start? 
    # Wait, simple spaces/tabs need to be skipped in START to avoid getting stuck or emitting garbage.
    # We need to ensure we implement skipping whitespace in START first/concurrently.
    
    assert TokenType.OP_PLUS in types
    assert TokenType.OP_MINUS in types
    assert TokenType.LPAREN in types
    assert TokenType.RPAREN in types

def test_ambiguous_ops_gt():
    """Test > vs >> (Greater Than vs Nest)."""
    code = "> >> >"
    tokens = get_tokens(code)
    types = [t.type for t in tokens]
    
    assert types == [TokenType.OP_GT, TokenType.OP_NEST, TokenType.OP_GT]

def test_ambiguous_ops_pipe():
    """Test | vs || (Horizontal vs OR)."""
    code = "| ||"
    tokens = get_tokens(code)
    types = [t.type for t in tokens]
    
    assert types == [TokenType.OP_HOR, TokenType.OP_OR]

def test_inc_dec_ops():
    """Test ++ and --."""
    code = "++ --"
    tokens = get_tokens(code)
    types = [t.type for t in tokens]
    
    assert types == [TokenType.OP_INC, TokenType.OP_DEC]

    assert types == [TokenType.OP_INC, TokenType.OP_DEC]

def test_compound_assignment():
    """Test += -= *= /= %="""
    code = "+= -= *= /= %="
    tokens = get_tokens(code)
    types = [t.type for t in tokens]
    
    assert types == [
        TokenType.OP_PLUS_ASSIGN,
        TokenType.OP_MINUS_ASSIGN, 
        TokenType.OP_MUL_ASSIGN, 
        TokenType.OP_DIV_ASSIGN, 
        TokenType.OP_MOD_ASSIGN
    ]

def test_punctuation():
    """Test commas and dots."""
    code = ".,"
    tokens = get_tokens(code)
    types = [t.type for t in tokens]
    
    assert types == [TokenType.DOT, TokenType.COMMA]
