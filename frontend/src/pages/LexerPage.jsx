import { motion } from 'framer-motion';
import { FiPlay } from 'react-icons/fi';
import { useCompiler } from '../context/CompilerContext';
import DataTable from '../components/DataTable';
import SourceEditor from '../components/SourceEditor';

const getTokenStyle = (type) => {
  if (type?.startsWith('KEYWORD')) {
    return 'bg-blue-500/10 text-blue-400 border-blue-500/20';
  }
  if (type === 'ID') {
    return 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20';
  }
  if (type === 'NUMBER') {
    return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
  }
  if (type === 'EOF') {
    return 'bg-red-500/10 text-red-400 border-red-500/20';
  }
  
  const isOperator = ['PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE', 'ASSIGN', 'EQ', 'NEQ', 'LT', 'LE', 'GT', 'GE', 'DOUBLE_DOT', 'relop', 'mulop'].includes(type);
  if (isOperator) {
    return 'bg-amber-500/10 text-amber-400 border-amber-500/20';
  }
  return 'bg-slate-500/10 text-slate-400 border-slate-500/20';
};

const columns = [
  {
    key: 'token_type',
    label: 'Token Type',
    render: (v) => (
      <span className={`inline-block px-2.5 py-0.5 rounded text-xs font-semibold font-sans border ${getTokenStyle(v)}`}>
        {v}
      </span>
    ),
  },
  {
    key: 'lexeme',
    label: 'Lexeme',
    render: (v) => (
      <span className="font-mono text-xs px-2 py-0.5 rounded bg-gray-800/60 border border-gray-700/50 text-gray-200">
        {v}
      </span>
    ),
  },
  { key: 'line', label: 'Line' },
  { key: 'column', label: 'Column' },
];

export default function LexerPage() {
  const { tokens, tokenStats, runLexerAction } = useCompiler();

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Lexer</h2>
          <p className="text-slate-500 text-sm mt-1">Token stream from lexical analysis</p>
        </div>
        <button
          onClick={runLexerAction}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-sky-600 hover:bg-sky-500 text-white text-sm font-semibold transition-all transform hover:-translate-y-0.5 shadow-lg shadow-sky-500/20 hover:shadow-sky-500/30"
        >
          <FiPlay /> Run Lexer
        </button>
      </div>

      <SourceEditor showCompileButtons={false} />

      {tokenStats.total > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {[
            ['Keywords', tokenStats.keywords],
            ['Identifiers', tokenStats.identifiers],
            ['Numbers', tokenStats.numbers],
            ['Operators', tokenStats.operators],
          ].map(([label, val]) => (
            <div key={label} className="glass-card rounded-xl p-4 flex items-center justify-between transition-all">
              <div>
                <p className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">{label}</p>
                <p className="text-2xl font-black text-white mt-1">{val || 0}</p>
              </div>
              <div className={`w-2.5 h-2.5 rounded-full ${
                label === 'Keywords' ? 'bg-sky-500 shadow-[0_0_8px_rgba(56,189,248,0.5)]' :
                label === 'Identifiers' ? 'bg-cyan-500 shadow-[0_0_8px_rgba(6,182,212,0.5)]' :
                label === 'Numbers' ? 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]' :
                'bg-amber-500 shadow-[0_0_8px_rgba(245,158,11,0.5)]'
              }`} />
            </div>
          ))}
        </div>
      )}

      <div className="glass-card rounded-xl p-6">
        <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4">
          Token Table ({tokens.length} tokens)
        </h3>
        <DataTable
          columns={columns}
          data={tokens}
          emptyTitle="No tokens yet"
          emptyDescription="Upload a Pascal file and run the lexer to see the token stream."
          searchKeys={['token_type', 'lexeme']}
        />
      </div>
    </motion.div>
  );
}
