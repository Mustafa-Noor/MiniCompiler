import { motion } from 'framer-motion';
import { FiPlay } from 'react-icons/fi';
import { useCompiler } from '../context/CompilerContext';
import StatusBadge from '../components/StatusBadge';
import DataTable from '../components/DataTable';
import EmptyState from '../components/EmptyState';

function DerivationTree({ trace }) {
  if (!trace.length) return null;

  const treeLines = trace
    .filter((line) => line.includes('→') || line.includes('enter') || line.includes('match'))
    .slice(0, 40);

  return (
    <div className="font-mono text-xs text-gray-400 space-y-0.5 max-h-64 overflow-y-auto scrollbar-thin p-4 bg-[#1e1e1e] rounded-lg border border-gray-800">
      {treeLines.map((line, i) => {
        const depth = (line.match(/^\s*/)?.[0].length || 0) / 2;
        return (
          <div key={i} style={{ paddingLeft: `${depth * 16}px` }} className="text-gray-300">
            {line.trim()}
          </div>
        );
      })}
    </div>
  );
}

export default function RDParserPage() {
  const { rdResult, runRDAction } = useCompiler();
  const traceRows = rdResult.trace.map((line, i) => ({ step: i + 1, action: line }));

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Recursive Descent Parser</h2>
          <p className="text-gray-500 text-sm mt-1">Top-down predictive parsing with derivation trace</p>
        </div>
        <div className="flex items-center gap-3">
          <StatusBadge accepted={rdResult.accepted} />
          <button
            onClick={runRDAction}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-purple-600 hover:bg-purple-500 text-white text-sm font-medium"
          >
            <FiPlay /> Run RD Parser
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="glass-card rounded-xl p-6">
          <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">
            Derivation Tree
          </h3>
          {rdResult.trace.length ? (
            <DerivationTree trace={rdResult.trace} />
          ) : (
            <EmptyState title="No trace" description="Run the RD parser to see the derivation tree." />
          )}
        </div>
        <div className="glass-card rounded-xl p-6">
          <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">
            Parse Result
          </h3>
          <div className={`text-center py-8 rounded-lg border ${
            rdResult.accepted ? 'border-emerald-500/30 bg-emerald-500/5' : rdResult.accepted === false ? 'border-red-500/30 bg-red-500/5' : 'border-gray-700'
          }`}>
            <p className="text-4xl font-bold mb-2">
              {rdResult.accepted === null ? '—' : rdResult.accepted ? '✓' : '✗'}
            </p>
            <p className="text-gray-400">
              {rdResult.accepted === null ? 'Not yet run' : rdResult.accepted ? 'Program Accepted' : 'Program Rejected'}
            </p>
          </div>
        </div>
      </div>

      <div className="glass-card rounded-xl p-6">
        <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">
          Trace Table ({rdResult.trace.length} steps)
        </h3>
        <DataTable
          columns={[
            { key: 'step', label: 'Step' },
            { key: 'action', label: 'Action' },
          ]}
          data={traceRows}
          emptyTitle="No trace data"
          emptyDescription="Run the RD parser to generate a derivation trace."
        />
      </div>
    </motion.div>
  );
}
