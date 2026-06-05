import { useEffect } from 'react';
import { motion } from 'framer-motion';
import { FiRefreshCw } from 'react-icons/fi';
import { useCompiler } from '../context/CompilerContext';
import DataTable from '../components/DataTable';

const columns = [
  { key: 'name', label: 'Name' },
  { key: 'kind', label: 'Kind', render: (v) => <span className="text-purple-400">{v}</span> },
  { key: 'type', label: 'Type', render: (v) => <span className="text-cyan-400">{v}</span> },
  { key: 'scope', label: 'Scope' },
  { key: 'line', label: 'Line' },
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
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gray-700 hover:bg-gray-600 text-white text-sm"
        >
          <FiRefreshCw /> Refresh
        </button>
      </div>

      <div className="glass-card rounded-xl p-6">
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
