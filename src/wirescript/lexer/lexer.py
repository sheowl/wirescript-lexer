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
            # Add other states here as we implement them (e.g., INDENT_CHECK)
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
            return Token(TokenType.EOF, line=self.line, column=self.column), Action.CONSUME
            
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
        # TODO: Implement Feature 2 (Indentation Logic
        pass
        
    def _is_noise_word(self, word: str) -> bool:
        """
        Helper to filter out noise words like 'create', 'make'.
        Returns True if the word should be ignored (no token emitted).
        """
        # TODO: Implement Feature 4 (Noise Words)
        pass
