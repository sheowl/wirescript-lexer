import React, { useState, useEffect, useRef } from 'react';
import Logo from './assets/Logo.png';
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
  Layers,
  Moon,
  Sun,
  Plus,
  Minus,
  Braces // Added for the JSON icon
} from 'lucide-react';

const LexicalAnalyzerApp = () => {
  const [inputCode, setInputCode] = useState(`Screen MainScreen {
  Int x = 10 + 5;
  render(hifi);
}`);
  const [viewMode, setViewMode] = useState('table'); // 'table', 'code', or 'json'
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

  // Map Backend TokenType to Frontend Categories
  const mapTokenType = (type) => {
    if (type.startsWith('KW_')) return 'Keyword';
    if (type.startsWith('RES_')) return 'Keyword';
    if (type.startsWith('OP_')) return 'Operator';
    if (type === 'IDENTIFIER') return 'Identifier';
    if (type === 'INTEGER' || type === 'FLOAT') return 'Number';
    if (type === 'STRING') return 'String';
    if (type === 'BOOLEAN' || type === 'NULL') return 'Keyword';
    if (type === 'LPAREN' || type === 'RPAREN' || type === 'LBRACE' || type === 'RBRACE' || type === 'COMMA' || type === 'DOT' || type === 'COLON') return 'Symbol';
    if (type === 'ERROR') return 'Error';
    if (type === 'NEWLINE' || type === 'INDENT' || type === 'DEDENT' || type === 'EOF') return 'Whitespace';
    return 'Unknown';
  };

  const mapTokenDescription = (type, value) => {
      switch (mapTokenType(type)) {
          case 'Keyword': return `Reserved word '${value || type}'`;
          case 'Identifier': return `User-defined name '${value}'`;
          case 'Number': return `Numeric literal`;
          case 'String': return `String literal`;
          case 'Operator': return `Operator '${value || type}'`;
          case 'Symbol': return `Punctuator`;
          case 'Whitespace': return `Structural element (${type})`;
          case 'Error': return `Lexical Error`;
          default: return '';
      }
  };

  const analyzeCode = async (text) => {
    try {
        const response = await fetch('/tokenize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ code: text }),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Analysis failed');
        }

        const backendTokens = await response.json();
        
        return backendTokens.map(t => ({
            line: t.line,
            lexeme: t.value === null ? `<${t.type}>` : String(t.value),
            attribute: mapTokenType(t.type),
            description: mapTokenDescription(t.type, t.value),
            rawType: t.type
        }));

    } catch (err) {
        console.error("API Error:", err);
        return [{
            line: 0,
            lexeme: "API ERROR",
            attribute: "Error",
            description: String(err)
        }];
    }
  };

  useEffect(() => {
    handleRun();
  }, []);

  const handleRun = async () => {
    const results = await analyzeCode(inputCode);
    setTokens(results);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Tab') {
      e.preventDefault();
      const start = e.target.selectionStart;
      const end = e.target.selectionEnd;
      const spaces = "  ";
      const newValue = inputCode.substring(0, start) + spaces + inputCode.substring(end);
      setInputCode(newValue);
      setTimeout(() => {
          e.target.selectionStart = e.target.selectionEnd = start + 2;
      }, 0);
    }
  };

  const handleClear = () => {
    setInputCode('');
    setTokens([]);
  };

  const fileInputRef = useRef(null);

  const handleSave = () => {
    const blob = new Blob([inputCode], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'source_code.ws'; // Changed to .ws
    link.click();
    setIsDropdownOpen(false);
  };

  const handleImportClick = () => {
    fileInputRef.current.click();
    setIsDropdownOpen(false);
  };

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      if (!file.name.endsWith('.ws') && !file.name.endsWith('.txt')) {
        alert('Unsupported file format. Please upload a .ws or .txt file.');
        event.target.value = ''; // Reset
        return;
      }

      const reader = new FileReader();
      reader.onload = (e) => {
        setInputCode(e.target.result);
      };
      reader.readAsText(file);
    }
    // Reset input so same file can be selected again
    event.target.value = ''; 
  };

  return (
    <div className="flex flex-col h-screen bg-[#F5FBE6] text-slate-900 font-sans">
      {/* Hidden File Input */}
      <input 
        type="file" 
        ref={fileInputRef} 
        onChange={handleFileChange} 
        accept=".ws,.txt" 
        className="hidden" 
      />
      {/* Header */}
      <header className="bg-[#F5FBE6]/90 backdrop-blur-md px-6 py-2 rounded-b-2xl flex justify-between items-center border-b border-[#FE7F2D]/20 animate-fadeInDown">
        <div className="flex items-center gap-3">
          <img src={Logo} alt="WireScript Logo" className="h-16 w-auto hover:scale-110 transition-transform duration-300" />
        </div>
        <div className="hidden md:flex items-center gap-4 text-sm text-[#233D4D] bg-gradient-to-r from-[#F5FBE6] to-[#FE7F2D]/20 px-4 py-2 rounded-full shadow-sm border border-[#FE7F2D]/20 animate-fadeIn" style={{animationDelay: '0.2s'}}>
          <span className="flex items-center gap-1.5 font-semibold">
            <Info size={14} className="text-[#FE7F2D]" /> 
            Process: Line-by-Line Tokenization
          </span>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex flex-1 overflow-hidden p-6 gap-6">
        
        {/* Input Section */}
        <section className="flex-1 flex flex-col bg-white/70 backdrop-blur-md rounded-xl border border-[#FE7F2D]/30 shadow-xl shadow-[#FE7F2D]/10 overflow-hidden animate-slideInLeft">
          <div className="bg-gradient-to-r from-[#F5FBE6] to-[#FE7F2D]/20 px-4 py-2 border-b border-[#FE7F2D]/30 flex justify-between items-center">
            <span className="text-xs font-bold text-[#233D4D] uppercase flex items-center gap-2">
              <Code size={14} className="text-[#FE7F2D]" /> Source Editor
            </span>
            <div className="relative" ref={dropdownRef}>
              <button 
                onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                className="p-1.5 hover:bg-[#FE7F2D]/20 rounded-lg transition-colors text-[#FE7F2D]"
              >
                <MoreHorizontal size={18} />
              </button>
              
              {isDropdownOpen && (
                <div className="absolute right-0 mt-2 w-48 bg-white/95 backdrop-blur-md border border-[#FE7F2D]/30 rounded-lg shadow-xl shadow-[#FE7F2D]/20 z-10 py-1 animate-fadeInDown">
                  <button 
                    onClick={handleSave}
                    className="w-full text-left px-4 py-2 text-sm text-slate-700 hover:bg-[#FE7F2D]/10 flex items-center gap-2 transition-all"
                  >
                    <Save size={16} className="text-[#FE7F2D]" /> Save input
                  </button>
                  <button 
                    onClick={handleImportClick}
                    className="w-full text-left px-4 py-2 text-sm text-slate-700 hover:bg-[#FE7F2D]/10 flex items-center gap-2 transition-all"
                  >
                    <Upload size={16} className="text-[#FE7F2D]" /> Import input (.ws)
                  </button>
                </div>
              )}
            </div>
          </div>
          <div className="flex-1 relative font-mono text-sm">
             {/* Line Numbers Overlay */}
             <div className="absolute left-0 top-0 w-12 h-full bg-gradient-to-r from-[#F5FBE6]/80 to-[#FE7F2D]/10 border-r border-[#FE7F2D]/30 flex flex-col pt-6 items-center text-[#FE7F2D]/60 pointer-events-none select-none">
                {inputCode.split('\n').map((_, i) => (
                  <div key={i} className="leading-relaxed">{i + 1}</div>
                ))}
             </div>
             <textarea
              value={inputCode}
              onChange={(e) => setInputCode(e.target.value)}
              onKeyDown={handleKeyDown}
              className="w-full h-full pl-16 pr-6 pt-6 pb-6 resize-none focus:outline-none bg-transparent leading-relaxed"
              placeholder="Enter source code here..."
              spellCheck="false"
            />
          </div>
          
          <div className="bg-gradient-to-r from-[#F5FBE6] to-[#FE7F2D]/20 border-t border-[#FE7F2D]/30 p-3 flex gap-3">
            <button 
              onClick={handleRun}
              className="flex-1 bg-gradient-to-r from-[#FE7F2D] to-[#D96C1F] hover:from-[#FE7F2D]/90 hover:to-[#D96C1F]/90 text-white font-bold py-2.5 px-4 rounded-lg flex items-center justify-center gap-2 transition-all shadow-lg shadow-[#FE7F2D]/40 active:scale-[0.98] hover:scale-[1.02] hover:shadow-xl hover:shadow-[#FE7F2D]/50"
            >
              <Zap size={18} fill="currentColor" className="animate-pulse" /> Run Analysis
            </button>
            <button 
              onClick={handleClear}
              className="bg-white/80 hover:bg-gradient-to-r hover:from-red-50 hover:to-rose-50 text-slate-600 hover:text-red-600 border border-[#FE7F2D]/30 hover:border-red-200 font-bold py-2.5 px-6 rounded-lg flex items-center justify-center gap-2 transition-all shadow-sm hover:scale-105"
            >
              <Trash2 size={18} /> Clear
            </button>
          </div>
        </section>

        {/* Output Section */}
        <section className="flex-1 flex flex-col bg-white/70 backdrop-blur-md rounded-xl border border-[#FE7F2D]/30 shadow-xl shadow-[#FE7F2D]/10 overflow-hidden animate-slideInRight">
          <div className="bg-gradient-to-r from-[#FE7F2D]/20 to-[#F5FBE6] px-4 py-2 border-b border-[#FE7F2D]/30 flex justify-between items-center">
            <span className="text-xs font-bold text-[#233D4D] uppercase flex items-center gap-2">
              <FileText size={14} className="text-[#FE7F2D]" /> Output Results
            </span>
            <div className="flex bg-white/90 rounded-lg p-1 border border-[#FE7F2D]/30 shadow-sm">
              <button 
                onClick={() => setViewMode('table')}
                className={`flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-medium transition-all ${viewMode === 'table' ? 'bg-gradient-to-r from-[#FE7F2D] to-[#D96C1F] text-white shadow-md shadow-[#FE7F2D]/40' : 'text-slate-500 hover:bg-[#FE7F2D]/10'}`}
              >
                <Table size={14} /> Table View
              </button>
              <button 
                onClick={() => setViewMode('code')}
                className={`flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-medium transition-all ${viewMode === 'code' ? 'bg-gradient-to-r from-[#FE7F2D] to-[#D96C1F] text-white shadow-md shadow-[#FE7F2D]/40' : 'text-slate-500 hover:bg-[#FE7F2D]/10'}`}
              >
                <Code size={14} /> Code Block
              </button>
              {/* NEW JSON BUTTON */}
              <button 
                onClick={() => setViewMode('json')}
                className={`flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-medium transition-all ${viewMode === 'json' ? 'bg-gradient-to-r from-[#FE7F2D] to-[#D96C1F] text-white shadow-md shadow-[#FE7F2D]/40' : 'text-slate-500 hover:bg-[#FE7F2D]/10'}`}
              >
                <Braces size={14} /> JSON
              </button>
            </div>
          </div>

          <div className="flex-1 overflow-auto bg-[#F5FBE6]/30">
            {tokens.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-[#FE7F2D]/50 gap-3 opacity-60">
                <Play size={48} className="text-[#FE7F2D]/30 animate-bounce" />
                <p className="text-sm font-medium animate-pulse">Click "Run Analysis" to view results</p>
              </div>
            ) : (
                <>
                    {/* TABLE VIEW */}
                    {viewMode === 'table' && (
                        <table className="w-full text-left border-collapse">
                            <thead className="sticky top-0 bg-gradient-to-r from-[#F5FBE6] to-[#FE7F2D]/20 z-10">
                            <tr className="text-[10px] uppercase text-[#233D4D] font-black border-b border-[#FE7F2D]/30 tracking-widest">
                                <th className="py-3 px-4 border-r border-[#FE7F2D]/20 w-16 text-center">Line</th>
                                <th className="py-3 px-4 border-r border-[#FE7F2D]/20">Token</th>
                                <th className="py-3 px-4 border-r border-[#FE7F2D]/20">Attribute</th>
                                <th className="py-3 px-4">Description</th>
                            </tr>
                            </thead>
                            <tbody>
                            {tokens.map((token, idx) => (
                                <tr key={idx} className="border-b border-[#FE7F2D]/20 hover:bg-[#FE7F2D]/10 transition-all duration-200 group animate-fadeInUp" style={{animationDelay: `${idx * 0.02}s`}}>
                                <td className="py-3 px-4 text-center font-mono text-xs text-[#FE7F2D]/60 border-r border-[#FE7F2D]/20">
                                    {token.line}
                                </td>
                                <td className="py-3 px-4 font-mono text-sm border-r border-[#FE7F2D]/20">
                                    <span className="bg-white/80 group-hover:bg-white px-2 py-0.5 rounded text-[#233D4D] font-bold border border-[#FE7F2D]/30 shadow-sm transition-all duration-200 group-hover:scale-105 group-hover:shadow-md">
                                    {token.lexeme}
                                    </span>
                                </td>
                                <td className="py-3 px-4 border-r border-[#FE7F2D]/20">
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
                    )}

                    {/* CODE BLOCK VIEW */}
                    {viewMode === 'code' && (
                        <div className="p-6">
                            <div className="bg-[#233D4D] rounded-xl p-6 font-mono text-sm leading-relaxed text-slate-300 shadow-xl shadow-[#233D4D]/50 border border-[#FE7F2D]/30">
                            {tokens.map((token, idx) => (
                                <div key={idx} className="flex gap-4 mb-2 group hover:bg-[#FE7F2D]/10 p-1 rounded transition-colors">
                                <span className="text-[#FE7F2D]/60 w-8 text-right select-none text-xs">L{token.line}</span>
                                <div className="flex items-center gap-3">
                                    <span className={`font-bold ${getAttributeColor(token.attribute)}`}>
                                    &lt;{token.attribute}&gt;
                                    </span>
                                    <span className="text-slate-100">"{token.lexeme}"</span>
                                </div>
                                </div>
                            ))}
                            </div>
                        </div>
                    )}

                    {/* JSON VIEW (NEW) */}
                    {viewMode === 'json' && (
                        <div className="p-6 h-full">
                             <div className="bg-[#233D4D] rounded-xl p-6 font-mono text-sm leading-relaxed text-slate-300 shadow-xl shadow-[#233D4D]/50 border border-[#FE7F2D]/30 h-full overflow-auto">
                                <pre className="whitespace-pre-wrap break-words">
                                    {JSON.stringify(tokens, null, 4)}
                                </pre>
                            </div>
                        </div>
                    )}
                </>
            )}
          </div>

          {/* Result Context Bar */}
          <div className="bg-gradient-to-r from-[#FE7F2D]/20 to-[#F5FBE6] border-t border-[#FE7F2D]/30 px-4 py-2 flex justify-between items-center text-[10px] text-[#233D4D] uppercase font-black tracking-tighter">
            <div className="flex gap-4">
              <span>Total Tokens: {tokens.length}</span>
              <span>Unique Lines: {new Set(tokens.map(t => t.line)).size}</span>
            </div>
            <span className="flex items-center gap-1">
              <span className={`w-1.5 h-1.5 rounded-full ${tokens.length > 0 ? 'bg-emerald-500 shadow-sm shadow-emerald-300' : 'bg-[#FE7F2D]/40'}`}></span>
              Status: {tokens.length > 0 ? 'Analysis Complete' : 'Idle'}
            </span>
          </div>
        </section>
      </main>

      {/* Main Footer */}
      <footer className="bg-[#F5FBE6]/90 backdrop-blur-md py-3 px-6 rounded-t-3xl border-t border-[#FE7F2D]/20 animate-fadeInUp">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
          {/* Left: Project Info */}
          <div className="text-center md:text-left -ml-32">
            <h2 className="text-2xl font-bold text-[#233D4D]">WireScript</h2>
            <p className="text-md text-[#FE7F2D] font-medium">Domain-Specific Language (DSL) for Unified UI/UX Design</p>
            <p className="text-md text-[#FE7F2D] font-medium">COSC 303: Principles of Programming Languages</p>
          </div>
          
          {/* Right: Team Members */}
          <div className="text-center md:text-right -mr-32">
            <p className="text-[16px] font-bold text-[#233D4D] uppercase mb-2">Team Members</p>
            <div className="grid grid-cols-2 gap-x-4 gap-y-0.5 text-sm text-[#FE7F2D]">
              <p>Bacolor, James Clark C.</p>
              <p>Guarin, Pauline</p>
              <p>Gueco, Jasper King</p>
              <p>Nadonga, Solomon</p>
              <p>Rosel, Cassandra</p>
              <p>Soriano, Shouma King</p>
              <p>Tagum, Anisha Shen</p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

const getAttributeStyle = (attr) => {
  switch (attr) {
    case 'Keyword': return 'bg-[#FE7F2D]/20 text-[#233D4D] border-[#FE7F2D] shadow-sm font-semibold';
    case 'Identifier': return 'bg-amber-100 text-amber-800 border-amber-300 shadow-sm';
    case 'Number': return 'bg-orange-100 text-orange-800 border-orange-300 shadow-sm';
    case 'Operator': return 'bg-[#233D4D]/10 text-[#233D4D] border-[#233D4D]/30 shadow-sm';
    case 'Symbol': return 'bg-slate-100 text-slate-700 border-slate-300 shadow-sm';
    case 'String': return 'bg-yellow-100 text-yellow-800 border-yellow-300 shadow-sm';
    case 'Error': return 'bg-red-100 text-red-700 border-red-300 shadow-sm';
    default: return 'bg-[#F5FBE6] text-[#233D4D] border-[#FE7F2D]/30 shadow-sm';
  }
};

const getAttributeColor = (attr) => {
  switch (attr) {
    case 'Keyword': return 'text-[#FE7F2D]';
    case 'Identifier': return 'text-amber-400';
    case 'Number': return 'text-orange-400';
    case 'Operator': return 'text-[#F5FBE6]';
    case 'Symbol': return 'text-slate-400';
    case 'String': return 'text-yellow-400';
    case 'Error': return 'text-red-400';
    default: return 'text-[#FE7F2D]/60';
  }
};

export default LexicalAnalyzerApp;