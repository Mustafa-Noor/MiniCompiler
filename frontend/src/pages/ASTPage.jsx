import { useEffect, useMemo, useState } from 'react';
import { motion } from 'framer-motion';
import { FiChevronRight, FiCode, FiRefreshCw, FiShare2 } from 'react-icons/fi';
import { useCompiler } from '../context/CompilerContext';
import EmptyState from '../components/EmptyState';

function OutlineTreeNode({ node, depth = 0 }) {
  const [open, setOpen] = useState(depth < 2);
  const children = node?.children || [];
  const hasChildren = children.length > 0;
  const label = node?.value ? `${node.type}: ${node.value}` : node?.type;

  return (
    <div>
      <button
        type="button"
        onClick={() => hasChildren && setOpen((v) => !v)}
        className="flex items-center gap-2 w-full min-h-8 px-2 rounded-md text-left hover:bg-gray-800/50 transition-colors"
        style={{ paddingLeft: `${depth * 18 + 8}px` }}
      >
        <FiChevronRight
          className={`shrink-0 text-gray-500 transition-transform ${open && hasChildren ? 'rotate-90' : ''} ${
            hasChildren ? '' : 'opacity-0'
          }`}
        />
        <span className="font-mono text-sm text-gray-200 break-all">{label}</span>
        {node?.line ? (
          <span className="ml-auto shrink-0 text-[10px] text-gray-600 font-mono">
            L{node.line}:C{node.column || 0}
          </span>
        ) : null}
      </button>
      {open && hasChildren ? (
        <div>
          {children.map((child, index) => (
            <OutlineTreeNode key={`${child.type}-${child.value || ''}-${index}`} node={child} depth={depth + 1} />
          ))}
        </div>
      ) : null}
    </div>
  );
}

function VisualTreeNode({ node }) {
  const children = node?.children || [];
  const label = node?.value ? `${node.type}: ${node.value}` : node?.type;

  return (
    <div className="ast-node">
      <div className="ast-box">
        <span className="ast-title">{label}</span>
        {node?.line ? <span className="ast-pos">L{node.line}:C{node.column || 0}</span> : null}
      </div>
      {children.length ? (
        <div className="ast-children">
          {children.map((child, index) => (
            <VisualTreeNode key={`${child.type}-${child.value || ''}-${index}`} node={child} />
          ))}
        </div>
      ) : null}
    </div>
  );
}

export default function ASTPage() {
  const { astResult, loadAST, runASTAction } = useCompiler();
  const ast = astResult.ast || {};
  const hasAst = Object.keys(ast).length > 0;
  const jsonText = useMemo(() => JSON.stringify(ast, null, 2), [ast]);

  useEffect(() => {
    loadAST();
  }, [loadAST]);

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white">AST Tree</h2>
          <p className="text-gray-500 text-sm mt-1">
            Abstract syntax tree generated from the current Mini Pascal source
          </p>
        </div>
        <button
          onClick={runASTAction}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-600/80 hover:bg-blue-500 text-white text-sm font-medium transition-all"
        >
          <FiRefreshCw /> Generate
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="glass-card rounded-lg p-4">
          <p className="text-xs text-gray-500 uppercase">Status</p>
          <p className="text-lg font-semibold text-gray-100">{astResult.success ? 'Generated' : 'Not Generated'}</p>
        </div>
        <div className="glass-card rounded-lg p-4">
          <p className="text-xs text-gray-500 uppercase">Root</p>
          <p className="text-lg font-semibold text-cyan-300">{astResult.root || '-'}</p>
        </div>
        <div className="glass-card rounded-lg p-4">
          <p className="text-xs text-gray-500 uppercase">Nodes</p>
          <p className="text-lg font-semibold text-emerald-300">{astResult.node_count || 0}</p>
        </div>
      </div>

      {!hasAst ? (
        <div className="glass-card rounded-xl">
          <EmptyState
            title="AST not generated"
            description="Generate the AST after saving or editing the source."
          />
        </div>
      ) : (
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          <div className="glass-card rounded-xl p-5 border border-gray-800/40">
            <div className="flex items-center gap-2 mb-4 text-gray-400">
              <FiShare2 />
              <h3 className="text-sm font-semibold uppercase tracking-wider">Node Tree</h3>
            </div>
            <div className="max-h-[640px] overflow-auto scrollbar-thin rounded-lg bg-[#101014] border border-gray-800/70 p-6">
              <div className="min-w-max pb-4">
                <VisualTreeNode node={ast} />
              </div>
            </div>
          </div>

          <div className="glass-card rounded-xl p-5 border border-gray-800/40">
            <div className="flex items-center gap-2 mb-4 text-gray-400">
              <FiCode />
              <h3 className="text-sm font-semibold uppercase tracking-wider">JSON View</h3>
            </div>
            <pre className="max-h-[640px] overflow-auto scrollbar-thin rounded-lg bg-[#101014] border border-gray-800/70 p-4 text-xs text-gray-300 font-mono leading-relaxed">
              {jsonText}
            </pre>
          </div>
        </div>
      )}

      {hasAst ? (
        <div className="glass-card rounded-xl p-5 border border-gray-800/40">
          <div className="flex items-center gap-2 mb-4 text-gray-400">
            <FiChevronRight />
            <h3 className="text-sm font-semibold uppercase tracking-wider">Outline View</h3>
          </div>
          <div className="max-h-[420px] overflow-auto scrollbar-thin pr-2">
            <OutlineTreeNode node={ast} />
          </div>
        </div>
      ) : null}
    </motion.div>
  );
}
