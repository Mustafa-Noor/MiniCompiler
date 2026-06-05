import { useState } from 'react';
import { motion } from 'framer-motion';
import { FiPlay } from 'react-icons/fi';
import { useCompiler } from '../context/CompilerContext';
import StatusBadge from '../components/StatusBadge';
import DataTable from '../components/DataTable';

function SetTable({ title, sets }) {
  const rows = Object.entries(sets).map(([nt, items]) => ({
    non_terminal: nt,
    set: Array.isArray(items) ? items.join(', ') : items,
  }));

  return (
    <div className="glass-card rounded-xl p-6">
      <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">{title}</h3>
      <DataTable
        columns={[
          { key: 'non_terminal', label: 'Non-Terminal' },
          { key: 'set', label: 'Set' },
        ]}
        data={rows}
        emptyTitle={`No ${title}`}
        pageSize={20}
      />
    </div>
  );
}

export default function LL1ParserPage() {
  const { ll1Result, runLL1Action } = useCompiler();
  const [tab, setTab] = useState('first');

  const tableRows = Object.entries(ll1Result.parsing_table || {}).map(([key, prod]) => ({
    entry: key,
    production: prod,
  }));

  const traceRows = (ll1Result.trace || []).map((line, i) => ({ step: i + 1, line }));

  const tabs = [
    { id: 'first', label: 'FIRST Sets' },
    { id: 'follow', label: 'FOLLOW Sets' },
    { id: 'table', label: 'LL(1) Table' },
    { id: 'trace', label: 'Trace' },
  ];

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h2 className="text-2xl font-bold text-white">LL(1) Predictive Parser</h2>
          <p className="text-gray-500 text-sm mt-1">Stack-driven parsing with FIRST/FOLLOW sets</p>
        </div>
        <div className="flex items-center gap-3">
          <StatusBadge accepted={ll1Result.accepted} />
          <button onClick={runLL1Action} className="flex items-center gap-2 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium">
            <FiPlay /> Run LL(1)
          </button>
        </div>
      </div>

      <div className="flex gap-2 flex-wrap">
        {tabs.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              tab === t.id ? 'bg-indigo-600/30 text-indigo-300 border border-indigo-500/40' : 'bg-gray-800/50 text-gray-400 hover:text-gray-200'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === 'first' && <SetTable title="FIRST Sets" sets={ll1Result.first_sets} />}
      {tab === 'follow' && <SetTable title="FOLLOW Sets" sets={ll1Result.follow_sets} />}
      {tab === 'table' && (
        <div className="glass-card rounded-xl p-6">
          <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">
            LL(1) Parsing Table ({tableRows.length} entries)
          </h3>
          <DataTable
            columns={[
              { key: 'entry', label: 'M[A, a]' },
              { key: 'production', label: 'Production' },
            ]}
            data={tableRows}
            emptyTitle="No parsing table"
            emptyDescription="Run the LL(1) parser to generate the table."
          />
        </div>
      )}
      {tab === 'trace' && (
        <div className="glass-card rounded-xl p-6">
          <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Parser Trace</h3>
          <DataTable
            columns={[
              { key: 'step', label: 'Step' },
              { key: 'line', label: 'Stack / Input / Action' },
            ]}
            data={traceRows}
            emptyTitle="No trace"
            emptyDescription="Run the LL(1) parser to see the stack trace."
          />
        </div>
      )}
    </motion.div>
  );
}
