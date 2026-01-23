from enum import Enum, auto
from typing import Optional, Tuple, Any, List
from .tokens import Token, TokenType

class Action(Enum):
    """
    Determines what the main loop should do after a state handler returns.
    CONSUME: Advance the character pointer (accept the current character).
    REPROCESS: Do NOT advance. Retry the SAME character with a new state.
    """
    CONSUME = auto()
    REPROCESS = auto()

class LexerState(Enum):
    """
    Represents the current mode of the Lexer.
    """
    START = auto()          # Default state, looking for any token
    INDENT_CHECK = auto()   # Processing indentation at start of line
    IDENTIFIER = auto()     # Reading letters/numbers (could be keyword, type, or ID)
    NUMBER = auto()         # Reading digits (int or float)
    STRING_SINGLE = auto()  # Reading inside ''
    STRING_DOUBLE = auto()  # Reading inside ""
    COMMENT_SINGLE = auto() # Skipping single line comment #
    COMMENT_MULTI = auto()  # Skipping multi line comment """
    OPERATOR = auto()       # resolving generic operators
    # Specific Operator Lookahead States
    OP_GT = auto()          # Saw >
    OP_LT = auto()          # Saw <
    OP_PIPE = auto()        # Saw |
    OP_AMP = auto()         # Saw &
    OP_EQ = auto()          # Saw =
    OP_NOT = auto()         # Saw !
    OP_PLUS = auto()        # Saw +
    OP_MINUS = auto()       # Saw -
    OP_MUL = auto()         # Saw *
    OP_DIV = auto()         # Saw /
    OP_MOD = auto()         # Saw %

class Lexer:
    """
    WireScript Lexer (Indentation-Sensitive).
    
    Implements the State Machine Pattern:
    - State + Reprocess handling for lookahead.
    - Lazy Finalization for Noise Words.
    - Indent Stack for whitespace structure.
    """
    def __init__(self, source_code: str):
        self.source = source_code
        self.pos = 0
        self.line = 1
        self.column = 1
        
        # The indentation stack: starts with 0 (base level)
        self.indent_stack: List[int] = [0]
        # Helper to store calculated indent for the current line
        self.indent_level_found: Optional[int] = None
        
        # Current token value buffer (for identifiers/strings)
        self.current_token_value = ""
        
        self.state = LexerState.START
        
        # --- Tables ---
        self.KEYWORDS = {
            'start': TokenType.KW_START, 'define': TokenType.KW_DEFINE,
            'if': TokenType.KW_IF, 'elif': TokenType.KW_ELIF, 'else': TokenType.KW_ELSE,
            'for': TokenType.KW_FOR, 'foreach': TokenType.KW_FOREACH, 'while': TokenType.KW_WHILE,
            'break': TokenType.KW_BREAK, 'continue': TokenType.KW_CONTINUE,
            'return': TokenType.KW_RETURN, 'render': TokenType.KW_RENDER,
            'import': TokenType.KW_IMPORT, 'export': TokenType.KW_EXPORT
        }
        
        self.RESERVED_WORDS = {
            'lofi': TokenType.RES_LOFI, 'hifi': TokenType.RES_HIFI,
            'Screen': TokenType.RES_SCREEN, 'Component': TokenType.RES_COMPONENT, 'Container': TokenType.RES_CONTAINER,
            'String': TokenType.RES_STRING, 'Int': TokenType.RES_INT, 'Boolean': TokenType.RES_BOOLEAN,
            'null': TokenType.NULL, 'true': TokenType.BOOLEAN, 'false': TokenType.BOOLEAN
        }
        
        self.NOISE_WORDS = {
            'create', 'make', 'set', 
            'add', 'to', 'with', 'containing'
        }
        
    def peek(self) -> str:
        """Returns the character at current position or '' if EOF."""
        if self.pos >= len(self.source):
            return ''
        return self.source[self.pos]

    def advance(self):
        """Moves pos forward and updates line/column."""
        if self.pos < len(self.source):
            if self.source[self.pos] == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.pos += 1

    def get_next_token(self) -> Token:
        """
        Main Driver Loop.
        
        Returns the next valid Token or TokenType.EOF.
        Implementation detail:
        - Loops infinitely until a Token is found or EOF is reached.
        - Calls the appropriate `_handle_X` method based on `self.state`.
        - Handles the `Action` returned (CONSUME vs REPROCESS).
        """
        while True:
            char = self.peek()
            
            # Dispatch to handler based on state
            if self.state == LexerState.START:
                token, action = self._handle_start(char)
            elif self.state == LexerState.IDENTIFIER:
                token, action = self._handle_identifier(char)
            elif self.state == LexerState.NUMBER: token, action = self._handle_number(char)
            elif self.state == LexerState.STRING_SINGLE: token, action = self._handle_string_single(char)
            elif self.state == LexerState.STRING_DOUBLE: token, action = self._handle_string_double(char)
            elif self.state == LexerState.COMMENT_SINGLE: token, action = self._handle_comment_single(char)
            elif self.state == LexerState.COMMENT_MULTI: token, action = self._handle_comment_multi(char)
            elif self.state == LexerState.INDENT_CHECK:
                token, action = self._handle_indentation(char)
            # Operator States
            elif self.state == LexerState.OP_GT: token, action = self._handle_op_gt(char)
            elif self.state == LexerState.OP_LT: token, action = self._handle_op_lt(char)
            elif self.state == LexerState.OP_PIPE: token, action = self._handle_op_pipe(char)
            elif self.state == LexerState.OP_AMP: token, action = self._handle_op_amp(char)
            elif self.state == LexerState.OP_EQ: token, action = self._handle_op_eq(char)
            elif self.state == LexerState.OP_NOT: token, action = self._handle_op_not(char)
            elif self.state == LexerState.OP_PLUS: token, action = self._handle_op_plus(char)
            elif self.state == LexerState.OP_MINUS: token, action = self._handle_op_minus(char)
            elif self.state == LexerState.OP_MUL: token, action = self._handle_op_mul(char)
            elif self.state == LexerState.OP_DIV: token, action = self._handle_op_div(char)
            elif self.state == LexerState.OP_MOD: token, action = self._handle_op_mod(char)
            # Add other states here as we implement them
            else:
                raise NotImplementedError(f"State {self.state} not implemented")

            # Handle Action
            if action == Action.CONSUME:
                self.advance()
            
            # If token found, return it
            if token:
                return token
            
            # If no token, loop continues (state transition or skipped char)

    def _handle_start(self, char: str) -> Tuple[Optional[Token], Action]:
        """
        Handler for LexerState.START.
        Determines what kind of token starts with `char`.
        """
        # EOF check
        if char == '':
            if len(self.indent_stack) > 1:
                self.indent_stack.pop()
                return Token(TokenType.DEDENT, line=self.line, column=self.column), Action.REPROCESS
            return Token(TokenType.EOF, line=self.line, column=self.column), Action.CONSUME

        # Newline Check (Phase 2)
        if char == '\n':
            # Emit NEWLINE, switch to INDENT_CHECK
            self.state = LexerState.INDENT_CHECK
            return Token(TokenType.NEWLINE, line=self.line, column=self.column), Action.CONSUME
            

        # Whitespace (skip)
        if char in (' ', '\t', '\r'):
            return None, Action.CONSUME
            
        # Operators
        if char == '>': self.state = LexerState.OP_GT; return None, Action.CONSUME
        if char == '<': self.state = LexerState.OP_LT; return None, Action.CONSUME
        if char == '|': self.state = LexerState.OP_PIPE; return None, Action.CONSUME
        if char == '^': return Token(TokenType.OP_VER, line=self.line, column=self.column), Action.CONSUME
        if char == '&': self.state = LexerState.OP_AMP; return None, Action.CONSUME
        if char == '=': self.state = LexerState.OP_EQ; return None, Action.CONSUME
        if char == '!': self.state = LexerState.OP_NOT; return None, Action.CONSUME
        if char == '+': self.state = LexerState.OP_PLUS; return None, Action.CONSUME
        if char == '-': self.state = LexerState.OP_MINUS; return None, Action.CONSUME
        if char == '*': self.state = LexerState.OP_MUL; return None, Action.CONSUME
        if char == '/': self.state = LexerState.OP_DIV; return None, Action.CONSUME
        if char == '%': self.state = LexerState.OP_MOD; return None, Action.CONSUME
        if char == '(': return Token(TokenType.LPAREN, line=self.line, column=self.column), Action.CONSUME
        if char == ')': return Token(TokenType.RPAREN, line=self.line, column=self.column), Action.CONSUME
        if char == '{': return Token(TokenType.LBRACE, line=self.line, column=self.column), Action.CONSUME
        if char == '}': return Token(TokenType.RBRACE, line=self.line, column=self.column), Action.CONSUME
        if char == ',': return Token(TokenType.COMMA, line=self.line, column=self.column), Action.CONSUME
        if char == '.': return Token(TokenType.DOT, line=self.line, column=self.column), Action.CONSUME
        if char == ':': return Token(TokenType.COLON, line=self.line, column=self.column), Action.CONSUME
        
        # Identifiers / Keywords / Noise Words
        if char.isalpha() or char == '_':
            self.state = LexerState.IDENTIFIER
            self.current_token_value = char # Start buffer
            return None, Action.CONSUME

        # Numbers
        if char.isdigit():
            self.state = LexerState.NUMBER
            self.current_token_value = char
            return None, Action.CONSUME

        # Strings and Comments
        if char == '"':
            # Check for Triple Quote (Lookahead)
            if self.pos + 1 < len(self.source) and self.source[self.pos:self.pos+2] == '""':
                if self.pos + 2 < len(self.source) and self.source[self.pos+1] == '"' and self.source[self.pos+2] == '"':
                    # It is """
                    self.state = LexerState.COMMENT_MULTI
                    # Consume the other two quotes manually
                    self.advance() 
                    self.advance()
                    return None, Action.CONSUME
            
            self.state = LexerState.STRING_DOUBLE
            self.current_token_value = "" # Start empty buffer (don't include quote)
            return None, Action.CONSUME
            
        if char == "'":
            self.state = LexerState.STRING_SINGLE
            self.current_token_value = ""
            return None, Action.CONSUME
            
        # Comments (Single Line)
        if char == '#':
            self.state = LexerState.COMMENT_SINGLE
            return None, Action.CONSUME

        # Detect unknown characters
        return Token(TokenType.ERROR, value=f"Unexpected character '{char}'", line=self.line, column=self.column), Action.CONSUME

    # --- Literal Handlers ---
    def _handle_number(self, char: str) -> Tuple[Optional[Token], Action]:
        """
        Consumes digits. Handles optional decimal point for float.
        """
        if char.isdigit():
            self.current_token_value += char
            return None, Action.CONSUME
            
        if char == '.':
            # Check if we already have a dot
            if '.' in self.current_token_value:
                pass # Fall through to reprocess
            else:
                self.current_token_value += char
                return None, Action.CONSUME
        
        # End of Number
        val_str = self.current_token_value
        self.state = LexerState.START # Reset state needed before REPROCESS
        if '.' in val_str:
            # Float
            return Token(TokenType.FLOAT, value=float(val_str), line=self.line, column=self.column-len(val_str)), Action.REPROCESS
        else:
            return Token(TokenType.INTEGER, value=int(val_str), line=self.line, column=self.column-len(val_str)), Action.REPROCESS

    def _handle_string_double(self, char: str) -> Tuple[Optional[Token], Action]:
        """
        Consumes until closing "
        """
        if char == '"':
            # End of string
            val = self.current_token_value
            self.state = LexerState.START
            return Token(TokenType.STRING, value=val, line=self.line, column=self.column-len(val)-2), Action.CONSUME # -2 for quotes
        
        if char == '' or char == '\n':
            self.state = LexerState.START
            return Token(TokenType.ERROR, value="Unterminated string literal", line=self.line, column=self.column), Action.REPROCESS

        self.current_token_value += char
        return None, Action.CONSUME

    def _handle_string_single(self, char: str) -> Tuple[Optional[Token], Action]:
        """
        Consumes until closing '
        """
        if char == "'":
            val = self.current_token_value
            self.state = LexerState.START
            return Token(TokenType.STRING, value=val, line=self.line, column=self.column-len(val)-2), Action.CONSUME
            
        if char == '' or char == '\n':
            self.state = LexerState.START
            return Token(TokenType.ERROR, value="Unterminated string literal", line=self.line, column=self.column), Action.REPROCESS

        self.current_token_value += char
        return None, Action.CONSUME

    def _handle_identifier(self, char: str) -> Tuple[Optional[Token], Action]:
        """
        Handler for LexerState.IDENTIFIER.
        Accumulates chars until delimiter is hit.
        Then checks against Keywords/Reserved/Noise.
        """
        # Valid ID chars: Letter, Digit, Underscore
        if char.isalnum() or char == '_':
            self.current_token_value += char
            return None, Action.CONSUME
            
        # Hit Delimiter (char is NOT part of ID)
        word = self.current_token_value
        
        # 1. Check Keywords
        if word in self.KEYWORDS:
            self.state = LexerState.START
            return Token(self.KEYWORDS[word], value=word, line=self.line, column=self.column - len(word)), Action.REPROCESS
        
        # 2. Check Reserved Words
        if word in self.RESERVED_WORDS:
            self.state = LexerState.START
            return Token(self.RESERVED_WORDS[word], value=word, line=self.line, column=self.column - len(word)), Action.REPROCESS
            
        # 3. Check Noise Words
        if word in self.NOISE_WORDS:
            # Reset to START, REPROCESS the delimiter.
            # No token emitted.
            self.state = LexerState.START
            return None, Action.REPROCESS
            
        # 4. Identifier
        self.state = LexerState.START
        return Token(TokenType.IDENTIFIER, value=word, line=self.line, column=self.column - len(word)), Action.REPROCESS

    # --- Operator Handlers ---
    def _handle_op_gt(self, char: str) -> Tuple[Optional[Token], Action]:
        # Saw '>', next is char
        if char == '>': # >>
            self.state = LexerState.START
            return Token(TokenType.OP_NEST, line=self.line, column=self.column-1), Action.CONSUME
        if char == '=': # >=
            self.state = LexerState.START
            return Token(TokenType.OP_GTE, line=self.line, column=self.column-1), Action.CONSUME
        # Else >
        self.state = LexerState.START
        return Token(TokenType.OP_GT, line=self.line, column=self.column-1), Action.REPROCESS

    def _handle_op_lt(self, char: str) -> Tuple[Optional[Token], Action]:
        if char == '<': # <<
            self.state = LexerState.START
            return Token(TokenType.OP_DEEP_NEST, line=self.line, column=self.column-1), Action.CONSUME
        if char == '=': # <=
            self.state = LexerState.START
            return Token(TokenType.OP_LTE, line=self.line, column=self.column-1), Action.CONSUME
        self.state = LexerState.START
        return Token(TokenType.OP_LT, line=self.line, column=self.column-1), Action.REPROCESS

    def _handle_op_pipe(self, char: str) -> Tuple[Optional[Token], Action]:
        if char == '|': # ||
            self.state = LexerState.START
            return Token(TokenType.OP_OR, line=self.line, column=self.column-1), Action.CONSUME
        self.state = LexerState.START
        return Token(TokenType.OP_HOR, line=self.line, column=self.column-1), Action.REPROCESS

    def _handle_op_amp(self, char: str) -> Tuple[Optional[Token], Action]:
        if char == '&': # &&
            self.state = LexerState.START
            return Token(TokenType.OP_AND, line=self.line, column=self.column-1), Action.CONSUME
            
        # Single & is not a valid operator
        self.state = LexerState.START
        return None, Action.REPROCESS 

    def _handle_op_eq(self, char: str) -> Tuple[Optional[Token], Action]:
        if char == '=': # ==
            self.state = LexerState.START
            return Token(TokenType.OP_EQ, line=self.line, column=self.column-1), Action.CONSUME
        self.state = LexerState.START
        return Token(TokenType.OP_ASSIGN, line=self.line, column=self.column-1), Action.REPROCESS

    def _handle_op_not(self, char: str) -> Tuple[Optional[Token], Action]:
        if char == '=': # !=
            self.state = LexerState.START
            return Token(TokenType.OP_NEQ, line=self.line, column=self.column-1), Action.CONSUME
        self.state = LexerState.START
        return Token(TokenType.OP_NOT, line=self.line, column=self.column-1), Action.REPROCESS

    def _handle_op_plus(self, char: str) -> Tuple[Optional[Token], Action]:
        if char == '+': # ++
            self.state = LexerState.START
            return Token(TokenType.OP_INC, line=self.line, column=self.column-1), Action.CONSUME
        if char == '=': # +=
            self.state = LexerState.START
            return Token(TokenType.OP_PLUS_ASSIGN, line=self.line, column=self.column-1), Action.CONSUME
        self.state = LexerState.START
        return Token(TokenType.OP_PLUS, line=self.line, column=self.column-1), Action.REPROCESS

    def _handle_op_minus(self, char: str) -> Tuple[Optional[Token], Action]:
        if char == '-': # --
            self.state = LexerState.START
            return Token(TokenType.OP_DEC, line=self.line, column=self.column-1), Action.CONSUME
        if char == '=': # -=
            self.state = LexerState.START
            return Token(TokenType.OP_MINUS_ASSIGN, line=self.line, column=self.column-1), Action.CONSUME
        self.state = LexerState.START
        return Token(TokenType.OP_MINUS, line=self.line, column=self.column-1), Action.REPROCESS

    def _handle_op_mul(self, char: str) -> Tuple[Optional[Token], Action]:
        if char == '=': # *=
            self.state = LexerState.START
            return Token(TokenType.OP_MUL_ASSIGN, line=self.line, column=self.column-1), Action.CONSUME
        self.state = LexerState.START
        return Token(TokenType.OP_MUL, line=self.line, column=self.column-1), Action.REPROCESS

    def _handle_op_div(self, char: str) -> Tuple[Optional[Token], Action]:
        if char == '=': # /=
            self.state = LexerState.START
            return Token(TokenType.OP_DIV_ASSIGN, line=self.line, column=self.column-1), Action.CONSUME
        self.state = LexerState.START
        return Token(TokenType.OP_DIV, line=self.line, column=self.column-1), Action.REPROCESS

    def _handle_op_mod(self, char: str) -> Tuple[Optional[Token], Action]:
        if char == '=': # %=
            self.state = LexerState.START
            return Token(TokenType.OP_MOD_ASSIGN, line=self.line, column=self.column-1), Action.CONSUME
        self.state = LexerState.START
        return Token(TokenType.OP_MOD, line=self.line, column=self.column-1), Action.REPROCESS

    def _handle_indentation(self, char: str) -> Tuple[Optional[Token], Action]:
        """
        Handler for LexerState.INDENT_CHECK.
        
        Logic:
        - Count spaces/tabs since newline.
        - Compare to self.indent_stack[-1].
        - Emit INDENT, DEDENT, or nothing.
        """
        # 1. Count Spaces (if not already done)
        if self.indent_level_found is None:
            indent_count = 0
            curr = char
            
            # Consume all spaces/tabs
            while curr in (' ', '\t'):
                indent_count += 1
                self.advance()
                curr = self.peek()
            
            # Check if empty line
            # If newline, empty line -> ignore indent -> REPROCESS from top to consume it
            if curr == '\n':
                # Empty line; reset to START to let main loop handle the newline
                self.state = LexerState.START
                return None, Action.REPROCESS
                
            if curr == '#':
                # Comment line behaves like empty line
                # Skip until newline
                while curr != '\n' and curr != '':
                    self.advance()
                    curr = self.peek()
                self.state = LexerState.START
                return None, Action.REPROCESS

            if curr == '': 
                 # EOF after spaces
                 indent_count = 0

            self.indent_level_found = indent_count
            return None, Action.REPROCESS

        # 2. Compare Indent Level
        current_level = self.indent_level_found
        top = self.indent_stack[-1]

        if current_level > top:
            # Indent
            self.indent_stack.append(current_level)
            self.indent_level_found = None
            self.state = LexerState.START
            return Token(TokenType.INDENT, line=self.line, column=self.column), Action.REPROCESS
        
        elif current_level < top:
            # Dedent
            self.indent_stack.pop()
            return Token(TokenType.DEDENT, line=self.line, column=self.column), Action.REPROCESS
            
        else:
            # Equal
            self.indent_level_found = None
            self.state = LexerState.START
            return None, Action.REPROCESS
        
    def _handle_comment_single(self, char: str) -> Tuple[Optional[Token], Action]:
        """
        Skip until newline.
        """
        if char == '\n':
            self.state = LexerState.START
            # Reprocess newline to be handled by START state
            return None, Action.REPROCESS
            
        if char == '': # EOF
            self.state = LexerState.START
            return None, Action.REPROCESS

        return None, Action.CONSUME

    def _handle_comment_multi(self, char: str) -> Tuple[Optional[Token], Action]:
        """
        Skip until \"\"\"
        """
        if char == '"':
            # Check for 3 quotes
            if self.pos + 1 < len(self.source) and self.source[self.pos:self.pos+2] == '""':
                 # Check manually for strict triple quote match
                 if self.pos + 2 < len(self.source) and self.source[self.pos+1] == '"' and self.source[self.pos+2] == '"':
                     # Closing """
                     self.advance()
                     self.advance()
                     self.state = LexerState.START
                     return None, Action.CONSUME
        
        # EOF Case
        if char == '':
             self.state = LexerState.START
             return Token(TokenType.ERROR, value="Unterminated multi-line comment", line=self.line, column=self.column), Action.CONSUME

        # Consume everything else
        return None, Action.CONSUME
