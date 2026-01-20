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
    # Expected: ID(start), NEWLINE, INDENT, ID(next)
    # Note: ID parsing isn't implemented yet, so "start" might come out as unknown chars skipped 
    # but NEWLINE and INDENT logic should work if we handle newlines.
    # Actually, if we don't have ID parsing, 'start' will interpret 's','t','a'... as skipped?
    # Wait, my `_handle_start` currently returns None, CONSUME for unknown.
    # So "start" will be skipped.
    # "\n" will trigger NEWLINE.
    # "  " will trigger INDENT.
    # "next" will be skipped.
    
    tokens = get_tokens(code)
    types = [t.type for t in tokens]
    
    assert TokenType.NEWLINE in types
    assert TokenType.INDENT in types
    
    # Precise order: NEWLINE -> INDENT
    nl_index = types.index(TokenType.NEWLINE)
    assert types[nl_index + 1] == TokenType.INDENT

def test_dedent_logic():
    code = "\n  x\n"
    # NEWLINE -> INDENT -> x(skipped) -> NEWLINE -> DEDENT -> EOF
    # 1. \n -> NEWLINE
    # 2. "  x" -> INDENT (2 > 0)
    # 3. x -> skipped
    # 4. \n -> NEWLINE
    # 5. EOF -> DEDENT (auto dedent from 2 to 0) -> EOF
    
    tokens = get_tokens(code)
    types = [t.type for t in tokens]
    
    # Filter only relevant tokens for this check
    relevant = [t for t in types if t in (TokenType.NEWLINE, TokenType.INDENT, TokenType.DEDENT)]
    assert relevant == [TokenType.NEWLINE, TokenType.INDENT, TokenType.NEWLINE, TokenType.DEDENT]

def test_multiple_dedent():
    code = "\n    \n"
    # 1. \n -> NEWLINE
    # 2. "    " -> INDENT (4 > 0). Stack [0, 4]
    # 3. \n -> NEWLINE
    # 4. Empty line (0). 0 < 4 -> DEDENT. Stack [0].
    # Wait, if we had nested:
    # \n  \n    \n  \n
    # NEWLINE, INDENT(2), NEWLINE, INDENT(4), NEWLINE, DEDENT(to 2), NEWLINE...
    pass # TODO: implement a complex case when basic one pass
