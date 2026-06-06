import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { FiRefreshCw } from 'react-icons/fi';
import { useCompiler } from '../context/CompilerContext';
import * as api from '../services/api';
import EmptyState from '../components/EmptyState';

const severityStyles = {
  LEXICAL: { bg: 'bg-red-500/10', border: 'border-red-500/30', text: 'text-red-400', dot: 'bg-red-500' },
  SYNTAX: { bg: 'bg-orange-500/10', border: 'border-orange-500/30', text: 'text-orange-400', dot: 'bg-orange-500' },
  SEMANTIC: { bg: 'bg-yellow-500/10', border: 'border-yellow-500/30', text: 'text-yellow-400', dot: 'bg-yellow-500' },
  TYPE: { bg: 'bg-purple-500/10', border: 'border-purple-500/30', text: 'text-purple-400', dot: 'bg-purple-500' },
  SCOPE: { bg: 'bg-pink-500/10', border: 'border-pink-500/30', text: 'text-pink-400', dot: 'bg-pink-500' },
};

const categories = ['LEXICAL', 'SYNTAX', 'SEMANTIC', 'TYPE', 'SCOPE'];

const categoryForError = (type) => {
  const t = String(type || '').toUpperCase();
  if (t.includes('LEXICAL')) return 'LEXICAL';
  if (t.includes('SYNTAX')) return 'SYNTAX';
  if (t.includes('SEMANTIC')) return 'SEMANTIC';
  if (t.includes('TYPE')) return 'TYPE';
  if (t.includes('SCOPE')) return 'SCOPE';
  return 'SYNTAX';
};

export default function ErrorsPage() {
  const { errors, loadErrors } = useCompiler();
  const [summary, setSummary] = useState(null);

  useEffect(() => {
    (async () => {
      try {
        const data = await api.getErrors();
        setSummary(data.summary || null);
      } catch {
        setSummary(null);
      }
      loadErrors();
    })();
  }, [loadErrors]);

  const grouped = categories.map((cat) => ({
    category: cat,
    items: errors.filter((e) => categoryForError(e.type) === cat),
  }));

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Error Handler</h2>
          <p className="text-gray-500 text-sm mt-1">Lexical, syntax, and semantic errors</p>
        </div>
        <button
          onClick={async () => {
            const data = await api.getErrors();
            setSummary(data.summary || null);
            loadErrors();
          }}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gray-700 text-white text-sm"
        >
          <FiRefreshCw /> Refresh
        </button>
      </div>

      {summary && summary.total > 0 && (
        <div className="glass-card rounded-xl p-4 flex flex-wrap gap-4 text-sm">
          <span className="text-gray-300">Total: <strong className="text-white">{summary.total}</strong></span>
          {Object.entries(summary.by_type || {}).map(([type, count]) => (
            <span key={type} className="text-gray-500">{type}: <span className="text-gray-300">{count}</span></span>
          ))}
        </div>
      )}

      {!errors.length ? (
        <div className="glass-card rounded-xl">
          <EmptyState title="No errors" description="Compilation completed without reported errors." />
        </div>
      ) : (
        <div className="space-y-4">
          {grouped.filter((g) => g.items.length).map(({ category, items }) => {
            const style = severityStyles[category] || severityStyles.SYNTAX;
            return (
              <div key={category} className={`glass-card rounded-xl p-6 border ${style.border}`}>
                <div className="flex items-center gap-2 mb-4">
                  <span className={`w-2 h-2 rounded-full ${style.dot}`} />
                  <h3 className={`text-sm font-semibold uppercase tracking-wider ${style.text}`}>
                    {category.replace('_', ' ')} ({items.length})
                  </h3>
                </div>
                <div className="space-y-2">
                  {items.map((err, i) => (
                    <div key={i} className={`p-3 rounded-lg ${style.bg} border ${style.border}`}>
                      <div className="flex items-start justify-between gap-4">
                        <p className="text-sm text-gray-200">{err.message}</p>
                        <span className="text-xs text-gray-500 shrink-0 font-mono">
                          L{err.line}:{err.column}
                        </span>
                      </div>
                      {err.lexeme && (
                        <p className="text-xs text-gray-500 mt-1 font-mono">Lexeme: {err.lexeme}</p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </motion.div>
  );
}
