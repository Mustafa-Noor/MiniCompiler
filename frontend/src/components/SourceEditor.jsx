import { useRef } from 'react';
import { FiUpload, FiPlay, FiZap } from 'react-icons/fi';
import { useCompiler } from '../context/CompilerContext';

export default function SourceEditor({ showCompileButtons = true }) {
  const fileRef = useRef(null);
  const lineNumbersRef = useRef(null);
  const {
    sourceCode, setSourceCode, filename,
    uploadSource, runAllAction, runLexerAction, runRDAction, runLL1Action, runLRAction,
  } = useCompiler();

  const lines = sourceCode.split('\n');

  const handleUpload = (e) => {
    const file = e.target.files?.[0];
    if (file) uploadSource(file);
    e.target.value = '';
  };

  const btnClass =
    'flex items-center gap-2 px-3 py-1.5 rounded-md text-xs font-medium transition-all hover:brightness-110';

  return (
    <div className="glass-card rounded-xl overflow-hidden flex flex-col h-full min-h-[320px]">
      <div className="flex items-center justify-between px-4 py-2 border-b border-slate-900/80 bg-slate-950/40 backdrop-blur-md">
        <div className="flex items-center gap-2">
          <span className="w-3 h-3 rounded-full bg-red-500/80" />
          <span className="w-3 h-3 rounded-full bg-yellow-500/80" />
          <span className="w-3 h-3 rounded-full bg-green-500/80" />
          <span className="ml-3 text-sm text-slate-400 font-mono">{filename}</span>
        </div>
        <div className="flex items-center gap-2">
          <input ref={fileRef} type="file" accept=".pas,.txt" className="hidden" onChange={handleUpload} />
          <button
            onClick={() => fileRef.current?.click()}
            className={`${btnClass} bg-slate-900/80 border border-slate-800 text-slate-300 hover:bg-slate-900 hover:text-white`}
          >
            <FiUpload /> Upload
          </button>
          {showCompileButtons && (
            <>
              <button
                onClick={runAllAction}
                className={`${btnClass} bg-emerald-600 text-white ring-1 ring-emerald-400/40 shadow-[0_0_10px_rgba(16,185,129,0.25)]`}
              >
                <FiZap /> Run All
              </button>
              <button onClick={runLexerAction} className={`${btnClass} bg-sky-600/80 text-white`}>
                <FiPlay /> Lexer
              </button>
              <button onClick={runRDAction} className={`${btnClass} bg-violet-600/80 text-white`}>
                <FiPlay /> RD
              </button>
              <button onClick={runLL1Action} className={`${btnClass} bg-indigo-600/80 text-white`}>
                <FiPlay /> LL1
              </button>
              <button onClick={runLRAction} className={`${btnClass} bg-teal-600/80 text-white`}>
                <FiPlay /> LR
              </button>
            </>
          )}
        </div>
      </div>
      <div className="flex flex-1 overflow-hidden">
        <div 
          ref={lineNumbersRef}
          className="w-12 shrink-0 bg-slate-950/30 border-r border-slate-900/60 py-3 text-right pr-2 select-none overflow-hidden"
        >
          {lines.map((_, i) => (
            <div key={i} className="editor-line-numbers text-slate-600 leading-[1.6]">
              {i + 1}
            </div>
          ))}
        </div>
        <textarea
          value={sourceCode}
          onChange={(e) => setSourceCode(e.target.value)}
          onScroll={(e) => {
            if (lineNumbersRef.current) {
              lineNumbersRef.current.scrollTop = e.target.scrollTop;
            }
          }}
          spellCheck={false}
          className="flex-1 bg-slate-950/10 text-slate-200 editor-line-numbers p-3 resize-none outline-none border-none leading-[1.6] w-full overflow-y-auto scrollbar-thin"
          style={{ caretColor: '#38bdf8' }}
        />
      </div>
    </div>
  );
}
