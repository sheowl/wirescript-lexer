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
    # Add specific operator states here if needed (e.g. OP_GREATER for > vs >>)

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
            
        # TODO: Implement rest of logic (Indentation, Identifier, etc.)
        # For now, just skip unknown chars to prevent infinite loop in tests
        return None, Action.CONSUME

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
