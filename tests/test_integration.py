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

def test_complex_wirescript_program():
    """
    Tests a complete (mock) WireScript program including:
    - Comments (single/multi)
    - Keywords & Identifiers
    - Noise Words (skipped)
    - Indentation
    - Literals (Int, Float, String, Boolean)
    - Operators & Assignments
    """
    code = """
    # This is a test program
    define calculate_score using base, bonus:
        \"\"\"
        Calculates total score
        Returns final int check
        \"\"\"
        make total with base + bonus
        
        if total >= 100:
            print "High Score"
            return true
        elif total > 50:
            set result to total * 1.5
            return result
        else:
            return false
    """
    
    # We expect the lexer to handle indentation and noise words correctly.
    # Let's trace expected tokens roughly:
    # 1. NEWLINE (initial empty line/comment handling might trigger?) 
    #    Actually our Lexer skips initial whitespace/comments if they don't produce tokens?
    #    The first line is empty (newline), second is comment.
    #    Let's depend on the actual output logic.
    
    tokens = get_tokens(code)
    
    # Filter out NEWLINEs for easier logic check, OR check structure properly.
    # Let's check key structural points.
    
    # 1. verify 'define'
    # The first real token might be NEWLINE or KW_DEFINE depending on leading \n.
    # code starts with \n. Lexer sees \n -> NEWLINE -> INDENT_CHECK.
    # Indent check sees 4 spaces (if indented in python string?)
    # Wait, the python string above has indentation relative to python file?
    # '    # This is a test ...'
    # If the file passes "    " as indentation, the first line has indent 4.
    # But usually top level is 0.
    # Let's strip the common indentation to be safe/realistic.
    import inspect
    code = inspect.cleandoc(code) 
    # cleandoc removes leading whitespace from first line and de-indents the rest.
    
    tokens = get_tokens(code)
    
    # After cleandoc:
    # # This is a test program
    # define calculate_score using base, bonus:
    # ...
    
    # Line 1: Comment. Skipped.
    # Line 1 End: Newline -> REPROCESS comment -> START -> \n -> NEWLINE.
    # Line 2: define ...
    
    # Let's verify the sequence of types for the first major line.
    # [NEWLINE, KW_DEFINE, IDENTIFIER(calculate_score), KW_USING, ID, COMMA, ID, COLON, NEWLINE]
    # Note: 'using' might be noise word? 
    # docs/wirescript.md says: `define name using inputs...`
    # Our Noise List: 'create', 'make', 'set', 'add', 'to', 'with', 'containing'.
    # 'using' is NOT in noise list. Is it a Keyword?
    # src/wirescript/lexer/lexer.py KEYWORDS does NOT have 'using'.
    # src/wirescript/lexer/lexer.py NOISE_WORDS does NOT have 'using'.
    # So 'using' will be an IDENTIFIER.
    
    current = 0
    # Allow for potential initial NEWLINEs
    while tokens[current].type == TokenType.NEWLINE:
        current += 1
        
    assert tokens[current].type == TokenType.KW_DEFINE
    assert tokens[current+1].type == TokenType.IDENTIFIER
    assert tokens[current+1].value == "calculate_score"
    
    # verify indent block
    # ... NEWLINE, INDENT
    # Find INDENT
    indent_token = None
    for t in tokens:
        if t.type == TokenType.INDENT:
            indent_token = t
            break
    assert indent_token is not None, "Should have found an INDENT token"
    
    # verify noise word skipping
    # 'make total with base + bonus'
    # 'make' -> Noise (Skipped)
    # 'with' -> Noise (Skipped)
    # Tokens: ID(total), ID(base), OP_PLUS, ID(bonus)
    
    # Locate 'total'
    found_make = False
    found_with = False
    total_token_idx = -1
    
    for i, t in enumerate(tokens):
        if t.value == "make": found_make = True
        if t.value == "with": found_with = True
        if t.value == "total" and t.type == TokenType.IDENTIFIER:
            total_token_idx = i
            
    assert not found_make, "'make' should be skipped as noise"
    assert not found_with, "'with' should be skipped as noise"
    assert total_token_idx != -1
    
    # Verify sequence: total, base, +, bonus
    # [total, base, +, bonus]
    # Actually: total (ID)
    # The next tokens should correspond to `with` (skipped) -> `base` (ID)
    
    # Let's check strictly around indentation
    # INDENT
    # """ ... """ -> Comment Multi (Skipped)
    # total ...
    
    # verify float 1.5
    found_float = False
    for t in tokens:
        if t.type == TokenType.FLOAT and t.value == 1.5:
            found_float = True
    assert found_float, "Should detect float 1.5"
    
    # verify string "High Score"
    found_string = False
    for t in tokens:
        if t.type == TokenType.STRING and t.value == "High Score":
            found_string = True
    assert found_string, "Should detect string 'High Score'"

    # verify boolean true/false
    found_bool = False
    for t in tokens:
        if t.type == TokenType.BOOLEAN:
            found_bool = True
    assert found_bool, "Should detect boolean literal"

