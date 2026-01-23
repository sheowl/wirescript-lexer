# WireScript Lexical Playground

This project is a full-stack implementation of the **WireScript** Domain-Specific Language (DSL) Lexer, featuring a Python backend and a React frontend for real-time visualization.

## Prerequisites

Before running the project, ensure you have the following installed:

- **[Python 3.13+](https://www.python.org/downloads/)** (for Backend)
- **[Node.js 22+ & npm](https://nodejs.org/en/download/)** (for Frontend)
- **[Git](https://git-scm.com/downloads)** (for version control)

## Project Structure

- **`backend/`**: Contains the core Python implementation of the WireScript Lexer and a FastAPI server.
- **`frontend/`**: A React application (Vite) that provides a web-based playground to type WireScript code and view tokenized output.

## Getting Started

### Backend Setup (Python)

The backend exposes a REST API to tokenize code.

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Mac/Linux:
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the API server:
   ```bash
   $env:PYTHONPATH='src'
   uvicorn wirescript.server:app --reload
   ```
   The API will be available at `http://localhost:8000`.

#### Running Tests (Lexer)

To verify the Lexer logic:

```bash
python -m pytest tests/
```

---

### Frontend Setup (React)

The frontend interfaces with the backend to display results.

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
   The UI will be available at `http://localhost:5173`.

## Features

- **Indentation-Sensitive Lexing**: Handles Python-like meaningful whitespace.
- **Real-time Tokenization**: See tokens instantly as you type.
- **Detailed Token Output**: Visualizes token types, values, lines, and columns.
- **Error Handling**: Displays lexical errors for invalid characters or structure.

## Lexer Capabilities

- **Keywords**: Control flow (`if`, `else`, `for`), System constants (`Screen`, `Component`).
- **Layout Operators**: `|` (Horizontal), `^` (Vertical), `>>` (Nest).
- **Literals**: Numbers, Strings, Booleans.
- **Comments**: Single (`#`) and Multi-line (`"""`).
