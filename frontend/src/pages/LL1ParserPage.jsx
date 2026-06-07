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
      render: (v) => <span className="font-mono text-slate-200 font-bold text-xs">{v}</span>
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
                  className={`px-2 py-0.5 rounded text-[10px] font-mono border transition-all ${
                    cleanItem === 'EPSILON' || cleanItem === 'ε'
                      ? 'bg-violet-500/10 text-violet-400 border-violet-500/20'
                      : cleanItem === 'EOF' || cleanItem === '$'
                      ? 'bg-rose-500/10 text-rose-400 border-rose-500/20'
                      : 'bg-sky-500/10 text-sky-400 border-sky-500/20 shadow-[0_0_8px_rgba(56,189,248,0.02)]'
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
    <div className="glass-card rounded-xl p-6">
      <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4">{title}</h3>
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
      render: (v) => <span className="font-mono text-slate-400 font-bold">{v}</span>
    },
    { 
      key: 'stack', 
      label: 'Stack Contents',
      render: (v) => (
        <div className="max-w-[280px] overflow-x-auto font-mono text-[11px] text-indigo-300 py-1 scrollbar-thin whitespace-nowrap bg-indigo-950/20 px-2.5 rounded-lg border border-indigo-500/15 shadow-[0_0_12px_rgba(99,102,241,0.02)]">
          {v || 'ε'}
        </div>
      )
    },
    { 
      key: 'input', 
      label: 'Input Buffer (Remaining Tokens)',
      render: (v) => (
        <div className="max-w-[320px] overflow-x-auto font-mono text-[11px] text-slate-300 py-1 scrollbar-thin whitespace-nowrap bg-slate-950/40 px-2.5 rounded-lg border border-slate-900/50 shadow-[0_0_12px_rgba(0,0,0,0.15)]">
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
              <span className="inline-block px-1.5 py-0.5 rounded text-[9px] font-bold uppercase tracking-wider bg-sky-500/10 text-sky-400 border border-sky-500/20 font-sans">
                Expand
              </span>
              <span className="font-mono text-[11px] text-slate-300">{rule}</span>
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
            <span className="inline-block px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-sans animate-pulse-glow">
              Accepted
            </span>
          );
        }
        if (v.startsWith('ERROR')) {
          return (
            <span className="inline-block px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-rose-500/15 text-rose-400 border border-rose-500/25 font-sans">
              {v}
            </span>
          );
        }
        return <span className="text-slate-400 font-mono text-[11px]">{v}</span>;
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
          <p className="text-slate-500 text-sm mt-1">Stack-driven parsing with FIRST/FOLLOW sets</p>
        </div>
        <div className="flex items-center gap-3">
          <StatusBadge accepted={ll1Result.accepted} />
          <button
            onClick={runLL1Action}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold transition-all transform hover:-translate-y-0.5 shadow-lg shadow-indigo-500/20 hover:shadow-indigo-500/30"
          >
            <FiPlay /> Run LL(1)
          </button>
        </div>
      </div>

      <div className="flex gap-2 flex-wrap justify-between items-center bg-slate-950/20 p-1.5 rounded-xl border border-slate-900/50">
        <div className="flex gap-1.5 flex-wrap">
          {tabs.map((t) => (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              className={`px-4 py-2 rounded-lg text-xs font-semibold tracking-wider uppercase transition-all cursor-pointer ${
                tab === t.id
                  ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/30'
                  : 'bg-slate-900/40 text-slate-400 hover:bg-slate-900 hover:text-white border border-slate-800/10'
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>

        {tab === 'table' && (
          <div className="flex items-center bg-slate-950/40 p-1 rounded-lg border border-slate-800/60 gap-1 mr-1">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-1.5 rounded text-xs transition-colors cursor-pointer ${
                viewMode === 'grid' ? 'bg-indigo-600/20 text-indigo-300' : 'text-slate-400 hover:text-slate-200'
              }`}
              title="Matrix Grid View"
            >
              <FiGrid size={15} />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-1.5 rounded text-xs transition-colors cursor-pointer ${
                viewMode === 'list' ? 'bg-indigo-600/20 text-indigo-300' : 'text-slate-400 hover:text-slate-200'
              }`}
              title="Flat List View"
            >
              <FiList size={15} />
            </button>
          </div>
        )}
      </div>

      {tab === 'first' && <SetTable title="FIRST Sets" sets={ll1Result.first_sets} />}
      {tab === 'follow' && <SetTable title="FOLLOW Sets" sets={ll1Result.follow_sets} />}
      
      {tab === 'table' && (
        <div className="glass-card rounded-xl p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider">
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
                  render: (v) => <span className="font-mono text-sky-400 font-bold">{v}</span>
                },
                { 
                  key: 'production', 
                  label: 'Production Rule',
                  render: (v) => (
                    <span className="font-mono text-slate-200">
                      <span className="text-pink-500 font-bold mr-1">→</span> {v}
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
        <div className="glass-card rounded-xl p-6">
          <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4">
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
