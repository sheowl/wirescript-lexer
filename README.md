# WireScript Lexical Analyzer

WireScript is a Domain-Specific Language (DSL) for UI/UX Design that separates structure from fidelity. This repository contains the core Python logic for the WireScript Lexer.

## Development Setup

### 1. Prerequisites

- Python 3.13+
- `pip` (Python Package Installer)

### 2. Installation

Create a virtual environment and install the required dependencies.

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Project Structure

The project follows a standard `src`-layout:

- `src/wirescript/`: Main package source code.
- `src/wirescript/lexer/`: Lexer module containing Tokens and Logic.
- `tests/`: Unit tests (pytest).
- `docs/`: Design documents and specifications.

## Running Tests

We use `pytest` for testing. The project is configured with `pytest.ini` to handle imports automatically.

```bash
# Run all tests
python -m pytest tests/

# Run detailed output
python -m pytest -v tests/
```

## Contributing

1. Always create a new branch for features.
2. Ensure `pytest` passes before pushing.
3. Update `requirements.txt` if adding new dependencies.
