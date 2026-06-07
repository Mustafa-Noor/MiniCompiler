import { useEffect } from 'react';
import { motion } from 'framer-motion';
import { FiDownload, FiRefreshCw } from 'react-icons/fi';
import { useCompiler } from '../context/CompilerContext';
import { getReportDownloadUrl } from '../services/api';
import EmptyState from '../components/EmptyState';

const FILE_MAP = {
  first_sets: 'first_sets.txt',
  follow_sets: 'follow_sets.txt',
  ll1_table: 'll1_table.txt',
  action_table: 'action_table.txt',
  goto_table: 'goto_table.txt',
  symbol_table: 'symbol_table.txt',
  errors: 'errors.txt',
};

export default function ReportsPage() {
  const { reports, loadReports } = useCompiler();

  useEffect(() => {
    loadReports();
  }, [loadReports]);

  const entries = Object.entries(FILE_MAP);

  const handleDownload = (key) => {
    const filename = FILE_MAP[key];
    window.open(getReportDownloadUrl(filename), '_blank');
  };

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Reports</h2>
          <p className="text-slate-500 text-sm mt-1">Download compiler analysis artifacts</p>
        </div>
        <button
          onClick={loadReports}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-900/80 border border-slate-800 hover:bg-slate-900 text-slate-300 hover:text-white text-sm font-semibold transition-all transform hover:-translate-y-0.5"
        >
          <FiRefreshCw /> Refresh
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {entries.map(([key, filename]) => (
          <motion.div
            key={key}
            whileHover={{ scale: 1.015 }}
            className="glass-card rounded-xl p-5 flex flex-col justify-between min-h-[160px]"
          >
            <div>
              <h3 className="font-semibold text-slate-200 capitalize">
                {reports.labels?.[key] || key.replace(/_/g, ' ')}
              </h3>
              <p className="text-xs text-slate-500 font-mono mt-1">{filename}</p>
            </div>
            <button
              onClick={() => handleDownload(key)}
              className="flex items-center justify-center gap-2 w-full py-2.5 rounded-lg bg-sky-600/85 hover:bg-sky-500 text-white text-xs font-semibold tracking-wider uppercase transition-all shadow-md shadow-sky-500/10 hover:shadow-sky-500/25 transform hover:-translate-y-0.5 mt-4"
            >
              <FiDownload /> Download Report
            </button>
          </motion.div>
        ))}
      </div>

      {!Object.keys(reports.reports || {}).length && (
        <div className="glass-card rounded-xl">
          <EmptyState
            title="Reports not generated"
            description="Run lexer and parser phases first, then refresh to download reports."
          />
        </div>
      )}
    </motion.div>
  );
}
