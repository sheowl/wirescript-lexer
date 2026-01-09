from enum import Enum, auto
from dataclasses import dataclass
from typing import Any, Optional

class TokenType(Enum):
    # --- Structural ---
    EOF = auto()
    NEWLINE = auto()
    INDENT = auto()
    DEDENT = auto()
    
    # --- Identifiers & Literals ---
    IDENTIFIER = auto()
    STRING = auto()
    INTEGER = auto()
    BOOLEAN = auto()  # true/false
    NULL = auto()
    
    # --- Keywords (Control Flow) ---
    KW_START = auto()   # start
    KW_DEFINE = auto()  # define
    KW_IF = auto()      # if
    KW_ELIF = auto()    # elif
    KW_ELSE = auto()    # else
    KW_FOR = auto()     # for
    KW_FOREACH = auto() # foreach
    KW_WHILE = auto()   # while
    KW_BREAK = auto()   # break
    KW_CONTINUE = auto()# continue
    KW_RETURN = auto()  # return
    KW_RENDER = auto()  # render
    KW_IMPORT = auto()  # import
    KW_EXPORT = auto()  # export
    
    # --- Reserved Words (System Constants) ---
    RES_LOFI = auto()         # lofi
    RES_HIFI = auto()         # hifi
    RES_SCREEN = auto()       # Screen
    RES_COMPONENT = auto()    # Component
    RES_CONTAINER = auto()    # Container
    RES_STRING = auto()       # String
    RES_INT = auto()          # Int
    RES_BOOLEAN = auto()      # Boolean
    
    # --- Layout Operators (Combinators) ---
    OP_HOR = auto()      # |
    OP_VER = auto()      # ^
    OP_NEST = auto()     # >>
    OP_DEEP_NEST = auto() # <<
    
    # --- Arithmetic Operators ---
    OP_PLUS = auto()     # +
    OP_MINUS = auto()    # -
    OP_MUL = auto()      # *
    OP_DIV = auto()      # /
    OP_MOD = auto()      # %
    
    # --- Relational Operators ---
    OP_EQ = auto()       # ==
    OP_NEQ = auto()      # !=
    OP_LT = auto()       # <
    OP_GT = auto()       # >
    OP_LTE = auto()      # <=
    OP_GTE = auto()      # >=
    
    # --- Logical Operators ---
    OP_AND = auto()      # &&
    OP_OR = auto()       # ||
    OP_NOT = auto()      # !
    
    # --- Unary/Assignment ---
    OP_INC = auto()      # ++
    OP_DEC = auto()      # --
    OP_ASSIGN = auto()   # =
    
    # --- Punctuators ---
    LPAREN = auto()      # (
    RPAREN = auto()      # )
    COMMA = auto()       # ,
    DOT = auto()         # .
    COLON = auto()       # :
    
@dataclass
class Token:
    type: TokenType
    value: Any = None
    line: int = 1
    column: int = 1
    
    def __repr__(self):
        val_str = f", value={self.value!r}" if self.value is not None else ""
        return f"Token({self.type.name}{val_str}, line={self.line}, col={self.column})"
