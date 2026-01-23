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

def test_keywords():
    """Test keywords like if, start, return."""
    code = "if start return"
    # Spaces are currently consumed/skipped by _handle_start
    tokens = get_tokens(code)
    types = [t.type for t in tokens]
    
    assert types == [TokenType.KW_IF, TokenType.KW_START, TokenType.KW_RETURN]

def test_reserved_words():
    """Test types and constants."""
    code = "String Int Boolean null hifi lofi"
    tokens = get_tokens(code)
    types = [t.type for t in tokens]
    
    assert types == [
        TokenType.RES_STRING, 
        TokenType.RES_INT, 
        TokenType.RES_BOOLEAN, 
        TokenType.NULL, 
        TokenType.RES_HIFI, 
        TokenType.RES_LOFI
    ]

def test_case_sensitivity():
    """Verify that identifiers are case sensitive (boolean vs Boolean)."""
    code = "boolean Boolean"
    tokens = get_tokens(code)
    types = [t.type for t in tokens]
    
    assert types == [TokenType.IDENTIFIER, TokenType.RES_BOOLEAN]
    
    # Correction: The spec in docs/wirescript.md lists "Boolean" (cap B) as reserved. 
    # "true", "false", "null" are lowercase constants.
    # Let's adjust test to strict spec if possible, or I'll see what passes.
    # For now testing what likely matches token map.

def test_identifiers():
    """Test standard identifiers."""
    code = "myVar _private var123"
    tokens = get_tokens(code)
    
    assert len(tokens) == 3
    assert tokens[0].type == TokenType.IDENTIFIER
    assert tokens[0].value == "myVar"
    assert tokens[1].type == TokenType.IDENTIFIER
    assert tokens[1].value == "_private"
    assert tokens[2].type == TokenType.IDENTIFIER
    assert tokens[2].value == "var123"

def test_noise_words_skipped():
    """Test that 'create', 'make', 'with' are ignored."""
    code = "create String s" 
    # Should be: RES_STRING, IDENTIFIER(s)
    # 'create' is skipped.
    
    tokens = get_tokens(code)
    types = [t.type for t in tokens]
    
    assert types == [TokenType.RES_STRING, TokenType.IDENTIFIER]
    assert tokens[1].value == "s"

def test_mixed_sentence():
    """Test a full declaration line."""
    # create submit_btn = Button(label="Submit")
    # For now we don't have Button as keyword, it's an ID.
    # We don't have String literals implemented yet (Milestone 5?), 
    # so "Submit" might fail or parse strange.
    # Let's test what we have:
    # make x = 10
    # make -> skipped
    # x -> ID
    # = -> OP_ASSIGN
    # 10 -> We don't have numbers yet? Or do we?
    # Milestone 4 includes identifiers/words. Spec says "Digits" are chars.
    # But this task is "Identifiers & Noise Words". 
    # Numbers likely next or part of this.
    # Let's stick to IDs for this test.
    
    code = "make x = y"
    tokens = get_tokens(code)
    types = [t.type for t in tokens]
    
    assert types == [TokenType.IDENTIFIER, TokenType.OP_ASSIGN, TokenType.IDENTIFIER]
