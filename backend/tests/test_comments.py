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
    # Expected: NEWLINE (maybe?), IDENTIFIER(x), EQ, INT(1)
    # Actually, if comment is on its own line:
    # 1. # comment -> Skipped.
    # 2. \n -> NEWLINE -> INDENT_CHECK
    # 3. x...
    
    # Wait, does the comment consume the newline?
    # Usually single line comment consumes until newline, but does NOT consume the newline itself?
    # If it doesn't consume newline, the newline triggers NEWLINE token.
    # If it's the very first line and empty (just comment), maybe no newline token needed if file starts with it?
    # Start -> # -> Comment State -> Newline -> Start emits Newline.
    
    # Let's count tokens for:
    # # Comment\n
    # x
    
    # Output: NEWLINE, ID(x)... 
    assert tokens[0].type == TokenType.NEWLINE
    assert tokens[1].value == "x"
    assert tokens[3].value == 1

def test_inline_comment():
    """Test comment at end of line."""
    code = "x = 1 # Inline comment"
    tokens = get_tokens(code)
    # ID(x), EQ, INT(1). Comment skipped.
    assert len(tokens) == 3
    assert tokens[0].value == "x"
    assert tokens[2].value == 1

def test_multi_line_comment():
    """Test triple quoted comment."""
    code = '"""\nThis is a\nmulti-line comment\n"""\nx'
    tokens = get_tokens(code)
    # Should skip everything until closing """.
    # Then ID(x).
    # Since it spans lines, does it emit NEWLINEs?
    # Spec says "Comments ... are completely ignored".
    # So it should be treated as whitespace. No tokens.
    assert len(tokens) == 2 # NEWLINE (from inside string?), ID(x)
    # Wait, if multiline comment contains newlines, they shouldn't trigger correct indentation updates or NEWLINE tokens?
    # Typically multi-line strings/comments obscure newlines.
    # So "x" should be the first real token if we ignore the comment block.
    # But wait, if code is:
    # """ ... """
    # \n
    # x
    # Then we have newlines.
    # If code is """..."""x -> valid? Yes.
    
    # Let's assume purely ignored.
    # Check if x is found.
    assert tokens[-1].value == "x"

def test_comment_only_file():
    """File with only comments."""
    code = "# Just a comment"
    tokens = get_tokens(code)
    assert len(tokens) == 0 # Just EOF
