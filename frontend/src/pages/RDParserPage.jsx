import { motion } from 'framer-motion';
import { FiPlay, FiCheckCircle, FiXCircle, FiSliders } from 'react-icons/fi';
import { useCompiler } from '../context/CompilerContext';
import StatusBadge from '../components/StatusBadge';
import DataTable from '../components/DataTable';
import EmptyState from '../components/EmptyState';

function DerivationTree({ trace }) {
  if (!trace.length) return null;

  // Render a clean visual representation of the derivation call stack
  return (
    <div className="font-mono text-[11px] text-slate-400 space-y-1 max-h-[380px] overflow-y-auto scrollbar-thin p-5 bg-slate-950/60 border border-slate-900/80 rounded-xl relative shadow-inner">
      <div className="absolute top-2 right-3 flex gap-1">
        <span className="w-1.5 h-1.5 rounded-full bg-slate-700" />
        <span className="w-1.5 h-1.5 rounded-full bg-slate-700" />
        <span className="w-1.5 h-1.5 rounded-full bg-slate-700" />
      </div>
      {trace.slice(0, 100).map((line, i) => {
        const depth = (line.match(/^\s*/)?.[0].length || 0) / 2;
        const trimmed = line.trim();
        
        let content = <span className="text-slate-300">{trimmed}</span>;
        
        if (trimmed.startsWith('→')) {
          const ruleName = trimmed.replace('→', '').trim();
          content = (
            <span className="inline-flex items-center gap-1.5">
              <span className="text-sky-400 font-bold">→</span>
              <span className="text-sky-300 font-medium uppercase tracking-wide text-[10px]">Enter</span>
              <span className="text-slate-200">{ruleName}</span>
            </span>
          );
        } else if (trimmed.startsWith('←')) {
          const ruleName = trimmed.replace('←', '').trim();
          const success = ruleName.endsWith('✓');
          content = (
            <span className="inline-flex items-center gap-1.5">
              <span className="text-slate-500 font-bold">←</span>
              <span className="text-slate-500 font-medium uppercase tracking-wide text-[10px]">Exit</span>
              <span className={success ? 'text-emerald-400' : 'text-rose-400'}>{ruleName}</span>
            </span>
          );
        } else if (trimmed.includes('[Match]')) {
          const matchText = trimmed.replace('[Match]', '').trim();
          content = (
            <span className="inline-flex items-center gap-1.5">
              <span className="text-emerald-400">✓</span>
              <span className="text-slate-500 uppercase text-[9px] font-bold">Match:</span>
              <span className="text-emerald-300 font-mono">{matchText}</span>
            </span>
          );
        } else if (trimmed.startsWith('ERROR:')) {
          const errText = trimmed.replace('ERROR:', '').trim();
          content = (
            <span className="inline-flex items-center gap-1.5">
              <span className="text-rose-500 font-bold">✗</span>
              <span className="text-rose-400">{errText}</span>
            </span>
          );
        }
        
        return (
          <div key={i} style={{ paddingLeft: `${depth * 16}px` }} className="flex items-center gap-1 hover:bg-slate-900/30 py-0.5 rounded transition-all">
            {depth > 0 && <span className="text-slate-800/60 select-none mr-1">│</span>}
            {content}
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
          <p className="text-slate-500 text-sm mt-1">Top-down predictive parsing with derivation trace</p>
        </div>
        <div className="flex items-center gap-3">
          <StatusBadge accepted={rdResult.accepted} />
          <button
            onClick={runRDAction}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-violet-600 hover:bg-violet-500 text-white text-sm font-semibold transition-all transform hover:-translate-y-0.5 shadow-lg shadow-violet-500/20 hover:shadow-violet-500/30"
          >
            <FiPlay /> Run RD Parser
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="glass-card rounded-xl p-6 lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider">
              Derivation Call Stack
            </h3>
            <span className="text-slate-500 text-xs font-mono">Max 100 entries</span>
          </div>
          {rdResult.trace.length ? (
            <DerivationTree trace={rdResult.trace} />
          ) : (
            <EmptyState title="No trace generated" description="Run the RD parser to visualize the derivation call stack." />
          )}
        </div>
        <div className="glass-card rounded-xl p-6 flex flex-col justify-between">
          <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4">
            Parse Summary
          </h3>
          <div className={`flex flex-col items-center justify-center py-10 px-4 rounded-xl border text-center transition-all ${
            rdResult.accepted
              ? 'border-emerald-500/20 bg-emerald-500/5 shadow-[0_0_24px_rgba(16,185,129,0.03)]'
              : rdResult.accepted === false
              ? 'border-rose-500/20 bg-rose-500/5 shadow-[0_0_24px_rgba(244,63,94,0.03)]'
              : 'border-slate-800 bg-slate-950/20'
          }`}>
            <div className="mb-4">
              {rdResult.accepted ? (
                <FiCheckCircle className="text-5xl text-emerald-400" />
              ) : rdResult.accepted === false ? (
                <FiXCircle className="text-5xl text-rose-400" />
              ) : (
                <FiSliders className="text-5xl text-slate-600" />
              )}
            </div>
            <p className="text-lg font-bold text-white mb-1">
              {rdResult.accepted === null ? 'Idle' : rdResult.accepted ? 'Accepted' : 'Syntax Error'}
            </p>
            <p className="text-xs text-slate-400 max-w-[180px]">
              {rdResult.accepted === null
                ? 'Run the recursive descent compiler phase to analyze the input.'
                : rdResult.accepted
                ? 'Program parsed successfully with correct compiler grammar.'
                : 'Grammar analysis failed. Review syntax errors.'}
            </p>
          </div>
          <div className="text-slate-500 text-[10px] mt-4 flex items-center justify-between border-t border-slate-900/60 pt-4">
            <span>Method: Top-Down</span>
            <span>Derivations: {rdResult.trace.filter(t => t.includes('→')).length}</span>
          </div>
        </div>
      </div>

      <div className="glass-card rounded-xl p-6">
        <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4">
          Trace Table ({rdResult.trace.length} steps)
        </h3>
        <DataTable
          columns={[
            { key: 'step', label: 'Step', sortable: true },
            { key: 'action', label: 'Action', sortable: false },
          ]}
          data={traceRows}
          emptyTitle="No trace data"
          emptyDescription="Run the RD parser to generate a derivation trace."
        />
      </div>
    </motion.div>
  );
}

