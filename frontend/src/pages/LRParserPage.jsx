import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiPlay, FiGrid, FiList } from 'react-icons/fi';
import { useCompiler } from '../context/CompilerContext';
import StatusBadge from '../components/StatusBadge';
import DataTable from '../components/DataTable';
import ParsingGridTable from '../components/ParsingGridTable';

export default function LRParserPage() {
  const { lrResult, runLRAction } = useCompiler();
  const [tab, setTab] = useState('action');
  const [viewMode, setViewMode] = useState('grid'); // 'grid' (unified/split) or 'list'
  const [gridSplit, setGridSplit] = useState(false); // true: separate ACTION and GOTO grids, false: combined/unified
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

  const actionRows = Object.entries(lrResult.action_table || {})
    .filter(([, v]) => !String(v).startsWith('error:'))
    .map(([k, v]) => ({
      key: k, action: v,
    }));

  const gotoRows = Object.entries(lrResult.goto_table || {}).map(([k, v]) => ({
    key: k, state: v,
  }));

  // Parse structured trace lines based on Python's fixed-width spacing format
  const traceRows = (lrResult.trace || [])
    .map((line, i) => {
      if (
        line.includes('===') ||
        line.includes('---') ||
        line.includes('SLR(1) Parser Trace') ||
        line.includes('State Stack')
      ) {
        return null;
      }
      if (!line.trim()) return null;

      try {
        // widths: Step:5, State Stack:20, Symbol Stack:40, Input:30, Action:remaining
        const stepRaw = line.substring(0, 5).trim();
        const stateStack = line.substring(5, 25).trim();
        const symbolStack = line.substring(25, 65).trim();
        const inputRemaining = line.substring(65, 95).trim();
        const action = line.substring(95).trim();

        return {
          step: stepRaw.replace('Step', '').trim() || String(i + 1),
          stateStack,
          symbolStack,
          input: inputRemaining,
          action,
        };
      } catch (e) {
        return {
          step: String(i + 1),
          stateStack: '',
          symbolStack: '',
          input: '',
          action: line,
        };
      }
    })
    .filter(Boolean);

  const traceColumns = [
    { 
      key: 'step', 
      label: 'Step',
      render: (v) => <span className="font-mono text-gray-400 font-bold">{v}</span>
    },
    { 
      key: 'stateStack', 
      label: 'State Stack',
      render: (v) => (
        <div className="max-w-[200px] overflow-x-auto font-mono text-[11px] text-blue-300 py-1 scrollbar-thin whitespace-nowrap bg-blue-950/10 px-2 rounded border border-blue-900/10">
          {v}
        </div>
      )
    },
    { 
      key: 'symbolStack', 
      label: 'Symbol Stack',
      render: (v) => (
        <div className="max-w-[240px] overflow-x-auto font-mono text-[11px] text-indigo-300 py-1 scrollbar-thin whitespace-nowrap bg-indigo-950/10 px-2 rounded border border-indigo-900/10">
          {v}
        </div>
      )
    },
    { 
      key: 'input', 
      label: 'Input Remaining',
      render: (v) => (
        <span className="font-mono text-[11px] text-slate-400 block max-w-[180px] truncate" title={v}>
          {v}
        </span>
      )
    },
    { 
      key: 'action', 
      label: 'Action',
      render: (v) => {
        if (v.startsWith('SHIFT')) {
          return (
            <span className="flex items-center gap-1.5">
              <span className="inline-block px-1.5 py-0.5 rounded text-[9px] font-bold uppercase tracking-wider bg-blue-500/10 text-blue-400 border border-blue-500/20 font-sans">
                Shift
              </span>
              <span className="font-mono text-[11px] text-gray-300">{v.replace('SHIFT', '').trim()}</span>
            </span>
          );
        }
        if (v.startsWith('REDUCE')) {
          const rule = v.replace('REDUCE', '').trim();
          return (
            <span className="flex items-center gap-1.5">
              <span className="inline-block px-1.5 py-0.5 rounded text-[9px] font-bold uppercase tracking-wider bg-purple-500/10 text-purple-400 border border-purple-500/20 font-sans">
                Reduce
              </span>
              <span className="font-mono text-[11px] text-purple-300">{rule}</span>
            </span>
          );
        }
        if (v.includes('ACCEPT')) {
          return (
            <span className="inline-block px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-green-500/20 text-green-300 border border-green-500/30 font-sans animate-pulse-glow">
              Accepted
            </span>
          );
        }
        if (v.includes('ERROR')) {
          return (
            <span className="inline-block px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-red-500/20 text-red-400 border border-red-500/30 font-sans">
              {v}
            </span>
          );
        }
        return <span className="text-gray-400 font-mono text-[11px]">{v}</span>;
      }
    },
  ];

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h2 className="text-2xl font-bold text-white">SLR Parser</h2>
          <p className="text-gray-500 text-sm mt-1">Shift-reduce parsing with ACTION/GOTO tables</p>
        </div>
        <div className="flex items-center gap-3">
          <StatusBadge accepted={lrResult.accepted} />
          <button onClick={runLRAction} className="flex items-center gap-2 px-4 py-2 rounded-lg bg-teal-600 hover:bg-teal-500 text-white text-sm font-medium transition-all shadow-[0_0_12px_rgba(13,148,136,0.3)]">
            <FiPlay /> Run LR Parser
          </button>
        </div>
      </div>

      {stackAnim.length > 0 && (
        <div className="glass-card rounded-xl p-6 border border-gray-800/40">
          <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">
            Stack Animation (First 15 steps)
          </h3>
          <div className="flex flex-col gap-2 max-h-48 overflow-y-auto scrollbar-thin">
            <AnimatePresence>
              {stackAnim.map((item) => (
                <motion.div
                  key={item.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: item.id * 0.04 }}
                  className="font-mono text-xs p-2 rounded bg-gray-800/40 border border-gray-700/40 text-gray-300 flex justify-between items-center"
                >
                  <span className="truncate max-w-[85%]">{item.line}</span>
                  <span className="text-[9px] uppercase font-bold text-teal-400/70 border border-teal-500/20 bg-teal-500/5 px-1 rounded shrink-0">
                    {item.line.includes('SHIFT') ? 'Shift' : 'Reduce'}
                  </span>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </div>
      )}

      {/* Sub tabs and Grid vs List layouts toggles */}
      <div className="flex gap-2 flex-wrap justify-between items-center bg-gray-900/10 p-1.5 rounded-xl border border-gray-800/40">
        <div className="flex gap-2 flex-wrap">
          {['combined', 'action', 'goto', 'trace'].map((t) => (
            <button
              key={t}
              onClick={() => {
                setTab(t);
                if (t === 'combined') {
                  setViewMode('grid');
                  setGridSplit(false);
                } else if (t === 'action' || t === 'goto') {
                  // Keep current viewMode
                }
              }}
              className={`px-4 py-2 rounded-lg text-sm font-medium capitalize cursor-pointer transition-all ${
                tab === t
                  ? 'bg-teal-600/30 text-teal-300 border border-teal-500/40'
                  : 'bg-gray-800/50 text-gray-400 hover:text-gray-200'
              }`}
            >
              {t === 'combined'
                ? 'Unified SLR Grid'
                : t === 'action'
                ? 'ACTION Table'
                : t === 'goto'
                ? 'GOTO Table'
                : 'Shift-Reduce Trace'}
            </button>
          ))}
        </div>

        {tab !== 'trace' && (
          <div className="flex items-center bg-gray-800/60 p-1 rounded-lg border border-gray-700/60 gap-1 mr-1">
            {tab !== 'combined' && (
              <>
                <button
                  onClick={() => {
                    setViewMode('grid');
                    setGridSplit(true);
                  }}
                  className={`p-1.5 rounded text-xs transition-colors cursor-pointer ${
                    viewMode === 'grid' && gridSplit
                      ? 'bg-teal-600/30 text-teal-300'
                      : 'text-gray-400 hover:text-gray-200'
                  }`}
                  title="Grid Matrix View"
                >
                  <FiGrid size={16} />
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  className={`p-1.5 rounded text-xs transition-colors cursor-pointer ${
                    viewMode === 'list' ? 'bg-teal-600/30 text-teal-300' : 'text-gray-400 hover:text-gray-200'
                  }`}
                  title="Flat List View"
                >
                  <FiList size={16} />
                </button>
              </>
            )}
          </div>
        )}
      </div>

      {tab === 'combined' && (
        <div className="glass-card rounded-xl p-6 border border-gray-800/40">
          <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">
            Unified SLR(1) Parsing Grid Matrix
          </h3>
          <ParsingGridTable
            type="lr_combined"
            actionData={lrResult.action_table}
            gotoData={lrResult.goto_table}
            emptyTitle="No ACTION/GOTO data"
            emptyDescription="Run the SLR parser to build the unified matrix."
          />
        </div>
      )}

      {tab === 'action' && (
        <div className="glass-card rounded-xl p-6 border border-gray-800/40">
          <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">
            SLR(1) ACTION Table
          </h3>
          {viewMode === 'grid' ? (
            <ParsingGridTable
              type="lr_action"
              actionData={lrResult.action_table}
              emptyTitle="No ACTION table"
              emptyDescription="Run the SLR parser to construct the ACTION matrix."
            />
          ) : (
            <DataTable
              columns={[
                { key: 'key', label: 'State, Terminal', render: (v) => <span className="font-mono text-teal-400 font-bold">{v}</span> },
                {
                  key: 'action',
                  label: 'Action Lookup',
                  render: (v) => {
                    const [action, stateVal] = String(v).split(':');
                    if (action === 'shift') return <span className="badge-slr badge-slr-shift">SHIFT (State {stateVal})</span>;
                    if (action === 'reduce') return <span className="badge-slr badge-slr-reduce">REDUCE (Production {stateVal})</span>;
                    if (action === 'accept') return <span className="badge-slr badge-slr-accept">ACCEPT</span>;
                    if (action === 'error') return <span className="badge-slr-empty">-</span>;
                    return <span>{v}</span>;
                  }
                }
              ]}
              data={actionRows}
              emptyTitle="No ACTION table"
              emptyDescription="Run the LR parser to build ACTION table."
              pageSize={30}
            />
          )}
        </div>
      )}

      {tab === 'goto' && (
        <div className="glass-card rounded-xl p-6 border border-gray-800/40">
          <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">
            SLR(1) GOTO Table
          </h3>
          {viewMode === 'grid' ? (
            <ParsingGridTable
              type="lr_goto"
              gotoData={lrResult.goto_table}
              emptyTitle="No GOTO table"
              emptyDescription="Run the SLR parser to construct the GOTO matrix."
            />
          ) : (
            <DataTable
              columns={[
                { key: 'key', label: 'State, Non-Terminal', render: (v) => <span className="font-mono text-teal-400 font-bold">{v}</span> },
                {
                  key: 'state',
                  label: 'Goto State',
                  render: (v) => <span className="badge-slr bg-teal-500/10 text-teal-400 border border-teal-500/20 px-2">{v}</span>
                }
              ]}
              data={gotoRows}
              emptyTitle="No GOTO table"
              emptyDescription="Run the SLR parser to build GOTO table."
              pageSize={30}
            />
          )}
        </div>
      )}

      {tab === 'trace' && (
        <div className="glass-card rounded-xl p-6 border border-gray-800/40">
          <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">
            Shift-Reduce Parsing Trace ({traceRows.length} steps)
          </h3>
          <DataTable
            columns={traceColumns}
            data={traceRows}
            emptyTitle="No trace data"
            emptyDescription="Run the LR parser to see step-by-step trace."
          />
        </div>
      )}
    </motion.div>
  );
}
