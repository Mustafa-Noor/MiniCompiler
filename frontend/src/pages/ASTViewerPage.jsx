import { useMemo, useState } from 'react';
import { motion } from 'framer-motion';
import { FiPlay, FiZoomIn, FiZoomOut, FiMaximize2 } from 'react-icons/fi';
import { useCompiler } from '../context/CompilerContext';
import EmptyState from '../components/EmptyState';
import SourceEditor from '../components/SourceEditor';
import StatusBadge from '../components/StatusBadge';

const kindStyles = {
  program: 'border-sky-500/70 bg-sky-950/20 text-sky-100 shadow-[0_0_12px_rgba(14,165,233,0.05)]',
  declarations: 'border-cyan-500/60 bg-cyan-950/15 text-cyan-100',
  subprograms: 'border-violet-500/60 bg-violet-950/15 text-violet-100',
  var_decl: 'border-slate-800 bg-slate-950/70 text-slate-200',
  assignment: 'border-sky-600/70 bg-slate-950/70 text-slate-200',
  binary_op: 'border-violet-500/70 bg-slate-950/70 text-slate-200',
  constant: 'border-emerald-700/60 bg-slate-950/80 text-emerald-300 shadow-[0_0_12px_rgba(16,185,129,0.02)]',
  identifier: 'border-slate-700/70 bg-slate-950/80 text-slate-100',
  call: 'border-sky-600/70 bg-slate-950/70 text-slate-200',
  function: 'border-violet-500/70 bg-violet-950/25 text-slate-100',
  procedure: 'border-violet-500/70 bg-violet-950/25 text-slate-100',
};

function nodeSubtitle(node) {
  const parts = [];
  if (node.value) parts.push(node.value);
  if (node.meta?.type) parts.push(`type: ${node.meta.type}`);
  if (node.meta?.role) parts.push(node.meta.role);
  return parts.join(' | ');
}

function TreeNode({ node }) {
  const hasChildren = node.children?.length > 0;
  const style = kindStyles[node.kind] || 'border-amber-800/60 bg-slate-950/70 text-white';
  const subtitle = nodeSubtitle(node);

  return (
    <div className="ast-node-wrap">
      <div className={`ast-node ${style}`}>
        <div className="text-[12px] font-black tracking-tight">{node.label}</div>
        {subtitle && <div className="mt-1 text-[11px] font-mono text-slate-400">{subtitle}</div>}
      </div>
      {hasChildren && (
        <div className="ast-children">
          {node.children.map((child, idx) => (
            <TreeNode key={`${child.kind}-${child.label}-${idx}`} node={child} />
          ))}
        </div>
      )}
    </div>
  );
}

function flattenStats(node, stats = { nodes: 0, leaves: 0, depth: 0 }, depth = 1) {
  if (!node) return stats;
  stats.nodes += 1;
  stats.depth = Math.max(stats.depth, depth);
  if (!node.children?.length) stats.leaves += 1;
  node.children?.forEach((child) => flattenStats(child, stats, depth + 1));
  return stats;
}

export default function ASTViewerPage() {
  const { astResult, runASTAction } = useCompiler();
  const [showSource, setShowSource] = useState(false);
  const [zoom, setZoom] = useState(0.9);

  const stats = useMemo(() => flattenStats(astResult.ast), [astResult.ast]);

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h2 className="text-2xl font-bold text-white">Abstract Syntax Tree</h2>
          <p className="text-slate-500 text-sm mt-1">Hierarchical AST generated from the current Mini Pascal source</p>
        </div>
        <div className="flex items-center gap-3">
          <StatusBadge accepted={astResult.accepted} />
          <button
            onClick={() => setShowSource((v) => !v)}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-900/80 border border-slate-800 text-slate-300 hover:text-white text-sm font-semibold transition-all hover:bg-slate-900"
          >
            <FiMaximize2 /> {showSource ? 'Hide Source' : 'Show Source'}
          </button>
          <button
            onClick={runASTAction}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-sky-600 hover:bg-sky-500 text-white text-sm font-semibold transition-all transform hover:-translate-y-0.5 shadow-lg shadow-sky-500/20 hover:shadow-sky-500/30"
          >
            <FiPlay /> Build AST
          </button>
        </div>
      </div>

      {showSource && <SourceEditor showCompileButtons={false} />}

      {astResult.ast && (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {[
            ['Nodes', stats.nodes],
            ['Leaves', stats.leaves],
            ['Depth', stats.depth],
          ].map(([label, value]) => (
            <div key={label} className="glass-card rounded-xl p-4">
              <p className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold">{label}</p>
              <p className="text-2xl font-black text-white mt-1">{value}</p>
            </div>
          ))}
        </div>
      )}

      {astResult.errors?.length > 0 && (
        <div className="glass-card rounded-xl p-5 border border-rose-500/20 bg-rose-500/5 shadow-[0_0_24px_rgba(244,63,94,0.03)]">
          <h3 className="text-sm font-semibold uppercase tracking-wider text-rose-400 mb-3 flex items-center gap-2">
            AST Build Errors
          </h3>
          {astResult.errors.map((err, idx) => (
            <div key={idx} className="text-sm text-slate-400 font-mono">
              Line {err.line}, Column {err.column}: {err.message}
            </div>
          ))}
        </div>
      )}

      <div className="glass-card rounded-xl p-5">
        <div className="flex items-center justify-between gap-3 mb-4">
          <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider border-l-2 border-sky-500 pl-3">
            AST Viewer
          </h3>
          <div className="flex items-center bg-slate-950/40 p-1 rounded-lg border border-slate-800/60 gap-2">
            <button
              onClick={() => setZoom((z) => Math.max(0.55, z - 0.1))}
              className="p-1.5 rounded text-xs transition-colors cursor-pointer text-slate-400 hover:text-slate-200"
              title="Zoom out"
            >
              <FiZoomOut size={15} />
            </button>
            <span className="text-xs text-slate-500 w-12 text-center font-mono">{Math.round(zoom * 100)}%</span>
            <button
              onClick={() => setZoom((z) => Math.min(1.25, z + 0.1))}
              className="p-1.5 rounded text-xs transition-colors cursor-pointer text-slate-400 hover:text-slate-200"
              title="Zoom in"
            >
              <FiZoomIn size={15} />
            </button>
          </div>
        </div>

        {!astResult.ast ? (
          <EmptyState
            title="No AST generated"
            description="Click Build AST to parse the current source code into a tree."
          />
        ) : (
          <div className="ast-canvas scrollbar-thin">
            <div className="ast-scale" style={{ transform: `scale(${zoom})` }}>
              <TreeNode node={astResult.ast} />
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
}
