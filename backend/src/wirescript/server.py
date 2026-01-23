from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Any
from wirescript.lexer.lexer import Lexer
from wirescript.lexer.tokens import TokenType

app = FastAPI(title="WireScript Lexer API")

# Allow CORS for Frontend integration
import os
origins_str = os.getenv("ALLOWED_ORIGINS", "")
origins = [origin.strip() for origin in origins_str.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)

class TokenResponse(BaseModel):
    type: str
    value: Optional[Any] = None
    line: int
    column: int

class CodeRequest(BaseModel):
    code: str

@app.get("/health")
def health_check():
    return {"status": "ok", "version": "0.1.0"}

@app.post("/tokenize", response_model=List[TokenResponse])
def tokenize(request: CodeRequest):
    try:
        lexer = Lexer(request.code)
        tokens = []
        while True:
            token = lexer.get_next_token()
            if token.type == TokenType.EOF:
                break
            tokens.append(token.to_dict())
        return tokens
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
