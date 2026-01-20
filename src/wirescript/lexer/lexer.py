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
    NUMBER = auto()         # Reading digits
    STRING = auto()         # Reading inside quotes
    COMMENT = auto()        # Skipping comment text
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
        
        self.state = LexerState.START
        
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
            
        # Newline Check (Phase 2)
        if char == '\n':
            # Emit NEWLINE, switch to INDENT_CHECK
            self.state = LexerState.INDENT_CHECK
            return Token(TokenType.NEWLINE, line=self.line, column=self.column), Action.CONSUME
            
        # Whitespace (skip)
        if char in (' ', '\t'):
            return None, Action.CONSUME
            
        # Operators (Phase 3)
        if char == '>': self.state = LexerState.OP_GT; return None, Action.CONSUME
        if char == '<': self.state = LexerState.OP_LT; return None, Action.CONSUME
        if char == '|': self.state = LexerState.OP_PIPE; return None, Action.CONSUME
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
        if char == ',': return Token(TokenType.COMMA, line=self.line, column=self.column), Action.CONSUME
        if char == '.': return Token(TokenType.DOT, line=self.line, column=self.column), Action.CONSUME
        if char == ':': return Token(TokenType.COLON, line=self.line, column=self.column), Action.CONSUME
        
        # TODO: Identifiers/Numbers
        # For now, just skip unknown chars to prevent infinite loop in tests
        return None, Action.CONSUME

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
        # Single & not in basic specific, maybe error or just single token if defined. 
        # Spec says OP_AND is &&. Does it have Bitwise AND? Spec doesn't say.
        # Assuming just error or skip for now if single not defined, 
        # BUT spec doesn't list SINGLE & as operator. 
        # Let's emit an Error or just Unknown?
        # Actually, let's treat it as unknown/skip for single, but returning None here loops REPROCESS endlessly if we resets to START?
        # If we reset to START and REPROCESS, START sees '&' again -> Infinite Loop.
        # So we MUST consume it if invalid.
        self.state = LexerState.START
        # Just return nothing (skip) for invalid single char
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
        - If DEDENT, we might need to emit multiple tokens (unwind stack).
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
            
            # Check if empty line (newline or EOF or comment?)
            # If newline, it's an empty line -> ignore indent -> REPROCESS from top to consume it
            if curr == '\n':
                # We do NOT consume the newline here?
                # If we don't, next loop sees \n.
                # If we are in INDENT_CHECK, and see \n:
                # We should probably just treat it as another newline to consume?
                # But _handle_start does that.
                # So we let REPROCESS handle it, but we must stay in INDENT_CHECK?
                # Or reset to START and let START find \n?
                # If we reset to START: START sees \n -> Emits NEWLINE -> INDENT_CHECK.
                # Result: NEWLINE NEWLINE. This is correct for empty lines.
                self.state = LexerState.START
                return None, Action.REPROCESS
                
            if curr == '#':
                # Comment line behaves like empty line
                # We skip until newline
                while curr != '\n' and curr != '':
                    self.advance()
                    curr = self.peek()
                self.state = LexerState.START
                return None, Action.REPROCESS

            if curr == '': 
                 # EOF after spaces. behave as 0 indent?
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
            # Determine if we need more dedents (stay in loop, keep indent_level_found)
            return Token(TokenType.DEDENT, line=self.line, column=self.column), Action.REPROCESS
            
        else:
            # Equal
            self.indent_level_found = None
            self.state = LexerState.START
            return None, Action.REPROCESS
        
    def _is_noise_word(self, word: str) -> bool:
        """
        Helper to filter out noise words like 'create', 'make'.
        Returns True if the word should be ignored (no token emitted).
        """
        # TODO: Implement Feature 4 (Noise Words)
        pass
