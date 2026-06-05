import { motion } from 'framer-motion';
import { FiPlay } from 'react-icons/fi';
import { useCompiler } from '../context/CompilerContext';
import DataTable from '../components/DataTable';
import SourceEditor from '../components/SourceEditor';

const columns = [
  {
    key: 'token_type',
    label: 'Token',
    render: (v) => (
      <span className={v?.startsWith('KEYWORD') ? 'text-blue-400' : v === 'ID' ? 'text-cyan-300' : v === 'NUMBER' ? 'text-green-400' : 'text-orange-300'}>
        {v}
      </span>
    ),
  },
  { key: 'lexeme', label: 'Lexeme' },
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
          <p className="text-gray-500 text-sm mt-1">Token stream from lexical analysis</p>
        </div>
        <button
          onClick={runLexerAction}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium transition-all"
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
            <div key={label} className="glass-card rounded-lg p-3 text-center">
              <p className="text-xs text-gray-500 uppercase">{label}</p>
              <p className="text-xl font-bold text-white">{val || 0}</p>
            </div>
          ))}
        </div>
      )}

      <div className="glass-card rounded-xl p-6">
        <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">
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
