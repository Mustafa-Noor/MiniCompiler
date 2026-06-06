import { useState } from 'react';
import { motion } from 'framer-motion';
import { FiPlay, FiGrid, FiList } from 'react-icons/fi';
import { useCompiler } from '../context/CompilerContext';
import StatusBadge from '../components/StatusBadge';
import DataTable from '../components/DataTable';
import ParsingGridTable from '../components/ParsingGridTable';

function SetTable({ title, sets }) {
  const columns = [
    { 
      key: 'non_terminal', 
      label: 'Non-Terminal',
      render: (v) => <span className="font-mono text-gray-200 font-bold text-xs">{v}</span>
    },
    { 
      key: 'set', 
      label: 'Set Elements',
      render: (v) => {
        const items = Array.isArray(v) ? v : String(v).split(',').map(s => s.trim());
        return (
          <div className="flex flex-wrap gap-1.5 py-0.5">
            {items.map((item, idx) => {
              const cleanItem = item.startsWith('KEYWORD_') ? item.substring(8) : item;
              return (
                <span 
                  key={idx} 
                  className={`px-2 py-0.5 rounded text-[10px] font-mono border ${
                    cleanItem === 'EPSILON' || cleanItem === 'ε'
                      ? 'bg-purple-500/10 text-purple-400 border-purple-500/20'
                      : cleanItem === 'EOF' || cleanItem === '$'
                      ? 'bg-red-500/10 text-red-400 border-red-500/20'
                      : 'bg-blue-500/10 text-blue-400 border-blue-500/20'
                  }`}
                >
                  {cleanItem === 'EPSILON' ? 'ε' : cleanItem}
                </span>
              );
            })}
          </div>
        );
      }
    },
  ];

  const rows = Object.entries(sets).map(([nt, items]) => ({
    non_terminal: nt,
    set: items,
  }));

  return (
    <div className="glass-card rounded-xl p-6 border border-gray-800/40">
      <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">{title}</h3>
      <DataTable
        columns={columns}
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
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'list'

  const tableRows = Object.entries(ll1Result.parsing_table || {}).map(([key, prod]) => ({
    entry: key,
    production: prod,
  }));

  // Parse structured trace lines
  const traceRows = (ll1Result.trace || [])
    .map((line, i) => {
      // Matches pattern: Step   1: [EOF program] [program GCD ; ...] EXPAND program -> ...
      const match = line.match(/^Step\s+(\d+):\s+\[(.*?)\]\s+\[(.*?)\]\s+(.*)$/);
      if (match) {
        return {
          step: parseInt(match[1]),
          stack: match[2].trim(),
          input: match[3].trim(),
          action: match[4].trim(),
        };
      }
      
      // Skip styling lines (headers, separators)
      if (line.includes('===') || line.includes('---') || line.includes('Predictive Parser Trace')) {
        return null;
      }
      
      // Fallback for non-matching debug output
      return { step: i + 1, stack: '', input: '', action: line };
    })
    .filter(Boolean);

  const traceColumns = [
    { 
      key: 'step', 
      label: 'Step',
      render: (v) => <span className="font-mono text-gray-400 font-bold">{v}</span>
    },
    { 
      key: 'stack', 
      label: 'Stack Contents',
      render: (v) => (
        <div className="max-w-[280px] overflow-x-auto font-mono text-[11px] text-indigo-300 py-1 scrollbar-thin whitespace-nowrap bg-indigo-950/10 px-2 rounded border border-indigo-900/10">
          {v || 'ε'}
        </div>
      )
    },
    { 
      key: 'input', 
      label: 'Input Buffer (Remaining Tokens)',
      render: (v) => (
        <div className="max-w-[320px] overflow-x-auto font-mono text-[11px] text-slate-300 py-1 scrollbar-thin whitespace-nowrap bg-slate-900/30 px-2 rounded border border-slate-800/40">
          {v}
        </div>
      )
    },
    { 
      key: 'action', 
      label: 'Action Taken',
      render: (v) => {
        if (v.startsWith('EXPAND')) {
          const rule = v.replace('EXPAND', '').trim();
          return (
            <span className="flex items-center gap-1.5">
              <span className="inline-block px-1.5 py-0.5 rounded text-[9px] font-bold uppercase tracking-wider bg-blue-500/10 text-blue-400 border border-blue-500/20 font-sans">
                Expand
              </span>
              <span className="font-mono text-[11px] text-gray-300">{rule}</span>
            </span>
          );
        }
        if (v.startsWith('MATCH')) {
          const matchStr = v.replace('MATCH', '').trim();
          return (
            <span className="flex items-center gap-1.5">
              <span className="inline-block px-1.5 py-0.5 rounded text-[9px] font-bold uppercase tracking-wider bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-sans">
                Match
              </span>
              <span className="font-mono text-[11px] text-emerald-300 font-bold">{matchStr}</span>
            </span>
          );
        }
        if (v.startsWith('ACCEPT')) {
          return (
            <span className="inline-block px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-green-500/20 text-green-300 border border-green-500/30 font-sans animate-pulse-glow">
              Accepted
            </span>
          );
        }
        if (v.startsWith('ERROR')) {
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
          <button onClick={runLL1Action} className="flex items-center gap-2 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium transition-all shadow-[0_0_12px_rgba(79,70,229,0.3)]">
            <FiPlay /> Run LL(1)
          </button>
        </div>
      </div>

      <div className="flex gap-2 flex-wrap justify-between items-center bg-gray-900/10 p-1.5 rounded-xl border border-gray-800/40">
        <div className="flex gap-2 flex-wrap">
          {tabs.map((t) => (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all cursor-pointer ${
                tab === t.id ? 'bg-indigo-600/30 text-indigo-300 border border-indigo-500/40' : 'bg-gray-800/50 text-gray-400 hover:text-gray-200'
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>

        {tab === 'table' && (
          <div className="flex items-center bg-gray-800/60 p-1 rounded-lg border border-gray-700/60 gap-1 mr-1">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-1.5 rounded text-xs transition-colors cursor-pointer ${
                viewMode === 'grid' ? 'bg-indigo-600/30 text-indigo-300' : 'text-gray-400 hover:text-gray-200'
              }`}
              title="Matrix Grid View"
            >
              <FiGrid size={16} />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-1.5 rounded text-xs transition-colors cursor-pointer ${
                viewMode === 'list' ? 'bg-indigo-600/30 text-indigo-300' : 'text-gray-400 hover:text-gray-200'
              }`}
              title="Flat List View"
            >
              <FiList size={16} />
            </button>
          </div>
        )}
      </div>

      {tab === 'first' && <SetTable title="FIRST Sets" sets={ll1Result.first_sets} />}
      {tab === 'follow' && <SetTable title="FOLLOW Sets" sets={ll1Result.follow_sets} />}
      
      {tab === 'table' && (
        <div className="glass-card rounded-xl p-6 border border-gray-800/40">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">
              LL(1) Parsing Table ({tableRows.length} entries)
            </h3>
          </div>

          {viewMode === 'grid' ? (
            <ParsingGridTable
              type="ll1"
              ll1Data={ll1Result.parsing_table}
              emptyTitle="No parsing table available"
              emptyDescription="Run the LL(1) parser to build the predictive matrix table."
            />
          ) : (
            <DataTable
              columns={[
                { 
                  key: 'entry', 
                  label: 'Table Cell M[Non-Terminal, Terminal]',
                  render: (v) => <span className="font-mono text-indigo-400 font-bold">{v}</span>
                },
                { 
                  key: 'production', 
                  label: 'Production Rule',
                  render: (v) => (
                    <span className="font-mono text-gray-200">
                      <span className="text-pink-400 font-bold mr-1">→</span> {v}
                    </span>
                  )
                },
              ]}
              data={tableRows}
              emptyTitle="No parsing table"
              emptyDescription="Run the LL(1) parser to generate the table."
            />
          )}
        </div>
      )}
      
      {tab === 'trace' && (
        <div className="glass-card rounded-xl p-6 border border-gray-800/40">
          <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">
            Parser Trace ({traceRows.length} steps)
          </h3>
          <DataTable
            columns={traceColumns}
            data={traceRows}
            emptyTitle="No trace data"
            emptyDescription="Run the LL(1) parser to view execution steps."
          />
        </div>
      )}
    </motion.div>
  );
}
