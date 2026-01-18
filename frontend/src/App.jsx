import React, { useState, useEffect, useRef } from 'react';
import { 
  MoreHorizontal, 
  FileText, 
  Save, 
  Table, 
  Code, 
  Info, 
  ChevronRight, 
  Play,
  Upload,
  Trash2,
  Zap,
  Layers
} from 'lucide-react';

const LexicalAnalyzerApp = () => {
  const [inputCode, setInputCode] = useState(`int main() {\n  int x = 10 + 5;\n  return x;\n}`);
  const [viewMode, setViewMode] = useState('table'); // 'table' or 'code'
  const [tokens, setTokens] = useState([]);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Updated Lexical Analyzer Logic: Line-by-Line Processing
  const analyzeCode = (text) => {
    if (!text.trim()) return [];
    
    const keywords = ['int', 'float', 'char', 'double', 'void', 'if', 'else', 'while', 'for', 'return', 'const', 'let', 'var'];
    const operators = ['+', '-', '*', '/', '=', '==', '<', '>', '<=', '>=', '!', '!=', '&&', '||'];
    const symbols = ['(', ')', '{', '}', '[', ']', ';', ',', '.'];
    
    const tokenPatterns = [
      { type: 'Whitespace', regex: /^\s+/ },
      { type: 'Keyword', regex: new RegExp(`^(${keywords.join('|')})\\b`) },
      { type: 'Identifier', regex: /^[a-zA-Z_][a-zA-Z0-9_]*/ },
      { type: 'Number', regex: /^[0-9]+(\.[0-9]+)?/ },
      { type: 'Operator', regex: new RegExp(`^(${operators.map(op => op.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|')})`) },
      { type: 'Symbol', regex: new RegExp(`^(${symbols.map(s => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|')})`) },
      { type: 'String', regex: /^"[^"]*"/ },
    ];

    const lines = text.split('\n');
    let allTokens = [];

    lines.forEach((lineText, index) => {
      const lineNumber = index + 1;
      let remaining = lineText;

      while (remaining.length > 0) {
        let match = null;
        
        for (let pattern of tokenPatterns) {
          match = remaining.match(pattern.regex);
          if (match) {
            const lexeme = match[0];
            if (pattern.type !== 'Whitespace') {
              allTokens.push({
                line: lineNumber,
                lexeme,
                attribute: pattern.type,
                description: getExplanation(lexeme, pattern.type)
              });
            }
            remaining = remaining.slice(lexeme.length);
            break;
          }
        }

        if (!match) {
          // If the first character of "remaining" is just whitespace not caught by regex for some reason
          if (/\s/.test(remaining[0])) {
            remaining = remaining.slice(1);
            continue;
          }
          
          allTokens.push({
            line: lineNumber,
            lexeme: remaining[0],
            attribute: 'Error',
            description: `Character '${remaining[0]}' is unrecognized in this language's alphabet.`
          });
          remaining = remaining.slice(1);
        }
      }
    });

    return allTokens;
  };

  const getExplanation = (lexeme, type) => {
    switch (type) {
      case 'Keyword':
        return `Reserved word used for declaration or control.`;
      case 'Identifier':
        return `Name given to a variable, function, or object.`;
      case 'Number':
        return `Constant numeric value (literal).`;
      case 'Operator':
        return `Instruction for a mathematical or logical operation.`;
      case 'Symbol':
        return `Structural delimiter or punctuation mark.`;
      case 'String':
        return `Literal sequence of characters.`;
      default:
        return `Standard lexical unit identified by the scanner.`;
    }
  };

  useEffect(() => {
    handleRun();
  }, []);

  const handleRun = () => {
    setTokens(analyzeCode(inputCode));
  };

  const handleClear = () => {
    setInputCode('');
    setTokens([]);
  };

  const handleSave = () => {
    const blob = new Blob([inputCode], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'source_code.txt';
    link.click();
    setIsDropdownOpen(false);
  };

  const handleImport = () => {
    const examples = [
      `void greet() {\n  print("Hello World");\n}`,
      `int calculate(int a, int b) {\n  return a * b + 10;\n}`,
      `while (x < 10) {\n  x = x + 1;\n}`
    ];
    const randomExample = examples[Math.floor(Math.random() * examples.length)];
    setInputCode(randomExample);
    setIsDropdownOpen(false);
  };

  return (
    <div className="flex flex-col h-screen bg-slate-50 text-slate-900 font-sans">
      {/* Header */}
      <header className="bg-white border-b px-6 py-4 flex justify-between items-center shadow-sm">
        <div className="flex items-center gap-3">
          <div className="bg-indigo-600 p-2 rounded-lg text-white">
            <Layers size={20} />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight">WireScript</h1>
            <p className="text-xs text-slate-500 uppercase font-semibold">Lexical Analyzer App</p>
          </div>
        </div>
        <div className="hidden md:flex items-center gap-4 text-sm text-slate-500 bg-slate-100 px-3 py-1.5 rounded-full">
          <span className="flex items-center gap-1.5 font-medium">
            <Info size={14} className="text-indigo-500" /> 
            Process: Line-by-Line Tokenization
          </span>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex flex-1 overflow-hidden p-6 gap-6">
        
        {/* Input Section */}
        <section className="flex-1 flex flex-col bg-white rounded-xl border shadow-sm overflow-hidden">
          <div className="bg-slate-100 px-4 py-2 border-b flex justify-between items-center">
            <span className="text-xs font-bold text-slate-500 uppercase flex items-center gap-2">
              <Code size={14} /> Source Editor
            </span>
            <div className="relative" ref={dropdownRef}>
              <button 
                onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                className="p-1 hover:bg-slate-200 rounded-md transition-colors"
              >
                <MoreHorizontal size={18} />
              </button>
              
              {isDropdownOpen && (
                <div className="absolute right-0 mt-2 w-48 bg-white border rounded-lg shadow-xl z-10 py-1">
                  <button 
                    onClick={handleSave}
                    className="w-full text-left px-4 py-2 text-sm text-slate-700 hover:bg-indigo-50 flex items-center gap-2"
                  >
                    <Save size={16} /> Save input
                  </button>
                  <button 
                    onClick={handleImport}
                    className="w-full text-left px-4 py-2 text-sm text-slate-700 hover:bg-indigo-50 flex items-center gap-2"
                  >
                    <Upload size={16} /> Import input
                  </button>
                </div>
              )}
            </div>
          </div>
          <div className="flex-1 relative font-mono text-sm">
             {/* Line Numbers Overlay */}
             <div className="absolute left-0 top-0 w-12 h-full bg-slate-50 border-r border-slate-200 flex flex-col pt-6 items-center text-slate-300 pointer-events-none select-none">
                {inputCode.split('\n').map((_, i) => (
                  <div key={i} className="leading-relaxed">{i + 1}</div>
                ))}
             </div>
             <textarea
              value={inputCode}
              onChange={(e) => setInputCode(e.target.value)}
              className="w-full h-full pl-16 pr-6 pt-6 pb-6 resize-none focus:outline-none bg-transparent leading-relaxed"
              placeholder="Enter source code here..."
              spellCheck="false"
            />
          </div>
          
          <div className="bg-slate-50 border-t p-3 flex gap-3">
            <button 
              onClick={handleRun}
              className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2.5 px-4 rounded-lg flex items-center justify-center gap-2 transition-all shadow-md active:scale-[0.98]"
            >
              <Zap size={18} fill="currentColor" /> Run Analysis
            </button>
            <button 
              onClick={handleClear}
              className="bg-white hover:bg-slate-100 text-slate-600 border border-slate-200 font-bold py-2.5 px-6 rounded-lg flex items-center justify-center gap-2 transition-all shadow-sm"
            >
              <Trash2 size={18} /> Clear
            </button>
          </div>
        </section>

        {/* Output Section */}
        <section className="flex-1 flex flex-col bg-white rounded-xl border shadow-sm overflow-hidden">
          <div className="bg-slate-100 px-4 py-2 border-b flex justify-between items-center">
            <span className="text-xs font-bold text-slate-500 uppercase flex items-center gap-2">
              <FileText size={14} /> Output Results
            </span>
            <div className="flex bg-white rounded-md p-1 border shadow-sm">
              <button 
                onClick={() => setViewMode('table')}
                className={`flex items-center gap-1.5 px-3 py-1 rounded-sm text-xs font-medium transition-all ${viewMode === 'table' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-500 hover:bg-slate-50'}`}
              >
                <Table size={14} /> Table View
              </button>
              <button 
                onClick={() => setViewMode('code')}
                className={`flex items-center gap-1.5 px-3 py-1 rounded-sm text-xs font-medium transition-all ${viewMode === 'code' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-500 hover:bg-slate-50'}`}
              >
                <Code size={14} /> Code Block
              </button>
            </div>
          </div>

          <div className="flex-1 overflow-auto bg-white">
            {tokens.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-slate-400 gap-3 opacity-60">
                <Play size={48} className="text-slate-200" />
                <p className="text-sm font-medium">Click "Run Analysis" to view results</p>
              </div>
            ) : viewMode === 'table' ? (
              <table className="w-full text-left border-collapse">
                <thead className="sticky top-0 bg-slate-50 z-10">
                  <tr className="text-[10px] uppercase text-slate-500 font-black border-b tracking-widest">
                    <th className="py-3 px-4 border-r border-slate-100 w-16 text-center">Line</th>
                    <th className="py-3 px-4 border-r border-slate-100">Token</th>
                    <th className="py-3 px-4 border-r border-slate-100">Attribute</th>
                    <th className="py-3 px-4">Description</th>
                  </tr>
                </thead>
                <tbody>
                  {tokens.map((token, idx) => (
                    <tr key={idx} className="border-b border-slate-50 hover:bg-indigo-50/30 transition-colors group">
                      <td className="py-3 px-4 text-center font-mono text-xs text-slate-400 border-r border-slate-100">
                        {token.line}
                      </td>
                      <td className="py-3 px-4 font-mono text-sm border-r border-slate-100">
                        <span className="bg-slate-100 group-hover:bg-white px-2 py-0.5 rounded text-indigo-700 font-bold border border-slate-200">
                          {token.lexeme}
                        </span>
                      </td>
                      <td className="py-3 px-4 border-r border-slate-100">
                        <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase border ${getAttributeStyle(token.attribute)}`}>
                          {token.attribute}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-xs text-slate-600 leading-relaxed italic">
                        {token.description}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="p-6">
                 <div className="bg-slate-900 rounded-xl p-6 font-mono text-sm leading-relaxed text-slate-300 shadow-inner">
                  {tokens.map((token, idx) => (
                    <div key={idx} className="flex gap-4 mb-2 group hover:bg-slate-800/50 p-1 rounded transition-colors">
                      <span className="text-slate-600 w-8 text-right select-none text-xs">L{token.line}</span>
                      <div className="flex items-center gap-3">
                        <span className={`font-bold ${getAttributeColor(token.attribute)}`}>
                          &lt;{token.attribute}&gt;
                        </span>
                        <span className="text-white">"{token.lexeme}"</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Result Context Bar */}
          <div className="bg-slate-100 border-t px-4 py-2 flex justify-between items-center text-[10px] text-slate-500 uppercase font-black tracking-tighter">
            <div className="flex gap-4">
              <span>Total Tokens: {tokens.length}</span>
              <span>Unique Lines: {new Set(tokens.map(t => t.line)).size}</span>
            </div>
            <span className="flex items-center gap-1">
              <span className={`w-1.5 h-1.5 rounded-full ${tokens.length > 0 ? 'bg-green-500' : 'bg-slate-400'}`}></span>
              Status: {tokens.length > 0 ? 'Analysis Complete' : 'Idle'}
            </span>
          </div>
        </section>
      </main>

      {/* Main Footer */}
      <footer className="bg-white border-t py-4 px-6 flex justify-center items-center text-slate-400">
        <p className="text-xs font-medium">Group 4 and then all rights reserved</p>
      </footer>
    </div>
  );
};

const getAttributeStyle = (attr) => {
  switch (attr) {
    case 'Keyword': return 'bg-purple-50 text-purple-700 border-purple-200';
    case 'Identifier': return 'bg-blue-50 text-blue-700 border-blue-200';
    case 'Number': return 'bg-amber-50 text-amber-700 border-amber-200';
    case 'Operator': return 'bg-emerald-50 text-emerald-700 border-emerald-200';
    case 'Symbol': return 'bg-slate-100 text-slate-700 border-slate-200';
    case 'String': return 'bg-rose-50 text-rose-700 border-rose-200';
    case 'Error': return 'bg-red-50 text-red-700 border-red-200';
    default: return 'bg-slate-50 text-slate-600 border-slate-100';
  }
};

const getAttributeColor = (attr) => {
  switch (attr) {
    case 'Keyword': return 'text-purple-400';
    case 'Identifier': return 'text-blue-400';
    case 'Number': return 'text-amber-400';
    case 'Operator': return 'text-emerald-400';
    case 'Symbol': return 'text-slate-400';
    case 'String': return 'text-rose-400';
    case 'Error': return 'text-red-400';
    default: return 'text-slate-500';
  }
};

export default LexicalAnalyzerApp;
