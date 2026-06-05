import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiPlay } from 'react-icons/fi';
import { useCompiler } from '../context/CompilerContext';
import StatusBadge from '../components/StatusBadge';
import DataTable from '../components/DataTable';

export default function LRParserPage() {
  const { lrResult, runLRAction } = useCompiler();
  const [tab, setTab] = useState('action');
  const [stackAnim, setStackAnim] = useState([]);

  useEffect(() => {
    if (lrResult.trace?.length) {
      const stacks = lrResult.trace
        .filter((l) => l.includes('SHIFT') || l.includes('REDUCE'))
        .slice(0, 15)
        .map((l, i) => ({ id: i, line: l }));
      setStackAnim(stacks);
    }
  }, [lrResult.trace]);

  const actionRows = Object.entries(lrResult.action_table || {}).map(([k, v]) => ({
    key: k, action: v,
  }));

  const gotoRows = Object.entries(lrResult.goto_table || {}).map(([k, v]) => ({
    key: k, state: v,
  }));

  const traceRows = (lrResult.trace || []).map((line, i) => ({ step: i + 1, line }));

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h2 className="text-2xl font-bold text-white">SLR Parser</h2>
          <p className="text-gray-500 text-sm mt-1">Shift-reduce parsing with ACTION/GOTO tables</p>
        </div>
        <div className="flex items-center gap-3">
          <StatusBadge accepted={lrResult.accepted} />
          <button onClick={runLRAction} className="flex items-center gap-2 px-4 py-2 rounded-lg bg-teal-600 hover:bg-teal-500 text-white text-sm font-medium">
            <FiPlay /> Run LR Parser
          </button>
        </div>
      </div>

      {stackAnim.length > 0 && (
        <div className="glass-card rounded-xl p-6">
          <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">
            Stack Animation
          </h3>
          <div className="flex flex-col gap-2 max-h-48 overflow-y-auto scrollbar-thin">
            <AnimatePresence>
              {stackAnim.map((item) => (
                <motion.div
                  key={item.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: item.id * 0.05 }}
                  className="font-mono text-xs p-2 rounded bg-gray-800/60 border border-gray-700/50 text-gray-300"
                >
                  {item.line}
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </div>
      )}

      <div className="flex gap-2 flex-wrap">
        {['action', 'goto', 'trace'].map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-2 rounded-lg text-sm font-medium capitalize transition-all ${
              tab === t ? 'bg-teal-600/30 text-teal-300 border border-teal-500/40' : 'bg-gray-800/50 text-gray-400'
            }`}
          >
            {t === 'action' ? 'ACTION Table' : t === 'goto' ? 'GOTO Table' : 'Shift-Reduce Trace'}
          </button>
        ))}
      </div>

      {tab === 'action' && (
        <div className="glass-card rounded-xl p-6">
          <DataTable
            columns={[{ key: 'key', label: 'State, Terminal' }, { key: 'action', label: 'Action' }]}
            data={actionRows}
            emptyTitle="No ACTION table"
            emptyDescription="Run the LR parser to build ACTION table."
            pageSize={30}
          />
        </div>
      )}
      {tab === 'goto' && (
        <div className="glass-card rounded-xl p-6">
          <DataTable
            columns={[{ key: 'key', label: 'State, Non-Terminal' }, { key: 'state', label: 'Goto State' }]}
            data={gotoRows}
            emptyTitle="No GOTO table"
            pageSize={30}
          />
        </div>
      )}
      {tab === 'trace' && (
        <div className="glass-card rounded-xl p-6">
          <DataTable
            columns={[{ key: 'step', label: 'Step' }, { key: 'line', label: 'Action' }]}
            data={traceRows}
            emptyTitle="No trace"
          />
        </div>
      )}
    </motion.div>
  );
}
