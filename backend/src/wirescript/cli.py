import sys
import json
import argparse
from wirescript.lexer.lexer import Lexer
from wirescript.lexer.tokens import TokenType

def main():
    parser = argparse.ArgumentParser(description="WireScript Lexer CLI")
    parser.add_argument('infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin, help="Input file path (or stdin)")
    parser.add_argument('--pretty', action='store_true', help="Pretty print JSON output")
    
    args = parser.parse_args()
    
    try:
        source_code = args.infile.read()
    except Exception as e:
        sys.stderr.write(f"Error reading input: {e}\n")
        sys.exit(1)
    
    lexer = Lexer(source_code)
    tokens = []
    
    while True:
        try:
            token = lexer.get_next_token()
            if token.type == TokenType.EOF:
                break
            tokens.append(token.to_dict())
        except Exception as e:
             # Fallback for unexpected crash
             sys.stderr.write(f"Lexer Error: {e}\n")
             sys.exit(1)
        
    if args.pretty:
        print(json.dumps(tokens, indent=2))
    else:
        print(json.dumps(tokens))

if __name__ == "__main__":
    main()
