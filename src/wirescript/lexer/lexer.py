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
        
    def get_next_token(self) -> Token:
        """
        Main Driver Loop.
        
        Returns the next valid Token or TokenType.EOF.
        Implementation detail:
        - Loops infinitely until a Token is found or EOF is reached.
        - Calls the appropriate `_handle_X` method based on `self.state`.
        - Handles the `Action` returned (CONSUME vs REPROCESS).
        """
        # TODO: Implement Feature 1 

    def _handle_start(self, char: str) -> Tuple[Optional[Token], Action]:
        """
        Handler for LexerState.START.
        Determines what kind of token starts with `char`.
        """
        # TODO: Switch to specific states based on char (e.g. if digit -> NUMBER)
        pass

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
