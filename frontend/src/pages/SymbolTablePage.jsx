import { useEffect } from 'react';
import { motion } from 'framer-motion';
import { FiRefreshCw, FiDatabase } from 'react-icons/fi';
import { useCompiler } from '../context/CompilerContext';
import DataTable from '../components/DataTable';

const getKindBadge = (kind) => {
  const k = String(kind || '').toLowerCase();
  switch (k) {
    case 'variable':
      return 'bg-amber-500/10 text-amber-400 border-amber-500/20';
    case 'array':
      return 'bg-teal-500/10 text-teal-400 border-teal-500/20';
    case 'function':
      return 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20';
    case 'procedure':
      return 'bg-purple-500/10 text-purple-400 border-purple-500/20';
    default:
      return 'bg-slate-500/10 text-slate-400 border-slate-500/20';
  }
};

const getTypeStyle = (type) => {
  const t = String(type || '').toLowerCase();
  if (t === 'integer') return 'text-cyan-400 font-semibold';
  if (t === 'real') return 'text-emerald-400 font-semibold';
  if (t.includes('array')) return 'text-teal-300 font-mono italic';
  return 'text-gray-400';
};

const columns = [
  {
    key: 'name',
    label: 'Name',
    render: (v) => <span className="font-mono text-gray-100 font-bold">{v}</span>,
  },
  {
    key: 'kind',
    label: 'Kind',
    render: (v) => (
      <span className={`inline-block px-2 py-0.5 rounded text-[10px] uppercase font-bold tracking-wider border ${getKindBadge(v)}`}>
        {v}
      </span>
    ),
  },
  {
    key: 'type',
    label: 'Type',
    render: (v) => (
      <span className={`font-mono text-xs ${getTypeStyle(v)}`}>
        {v}
      </span>
    ),
  },
  {
    key: 'scope',
    label: 'Scope',
    render: (v) => {
      const isGlobal = String(v).toLowerCase() === 'global' || String(v) === '0';
      return (
        <span className={`inline-block px-2 py-0.5 rounded text-xs border ${
          isGlobal 
            ? 'bg-emerald-950/20 text-emerald-400 border-emerald-900/30' 
            : 'bg-gray-800/60 text-gray-300 border-gray-700/50'
        }`}>
          {isGlobal ? 'Global' : v}
        </span>
      );
    },
  },
  {
    key: 'line',
    label: 'Declaration Line',
    render: (v, row) => (
      <span className="text-gray-500 font-mono">
        L{v} : C{row.column || 0}
      </span>
    ),
  },
];

export default function SymbolTablePage() {
  const { symbols, loadSymbolTable } = useCompiler();

  useEffect(() => {
    loadSymbolTable();
  }, [loadSymbolTable]);

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Symbol Table</h2>
          <p className="text-gray-500 text-sm mt-1">Scoped symbol entries with type and location</p>
        </div>
        <button
          onClick={loadSymbolTable}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gray-700 hover:bg-gray-600 text-white text-sm font-medium transition-all"
        >
          <FiRefreshCw /> Refresh
        </button>
      </div>

      <div className="glass-card rounded-xl p-6 border border-gray-800/40">
        <div className="flex items-center gap-2 mb-4 text-gray-400">
          <FiDatabase />
          <h3 className="text-sm font-semibold uppercase tracking-wider">
            Symbol Entries ({symbols.length})
          </h3>
        </div>
        <DataTable
          columns={columns}
          data={symbols}
          emptyTitle="Symbol table empty"
          emptyDescription="Run compilation phases to populate the symbol table."
          searchKeys={['name', 'kind', 'type', 'scope']}
        />
      </div>
    </motion.div>
  );
}
