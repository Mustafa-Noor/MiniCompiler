import { motion } from 'framer-motion';
import { FiHash, FiAlertTriangle, FiDatabase, FiActivity } from 'react-icons/fi';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { useCompiler } from '../context/CompilerContext';
import StatCard from '../components/StatCard';
import Pipeline from '../components/Pipeline';
import SourceEditor from '../components/SourceEditor';
import StatusBadge from '../components/StatusBadge';

const CHART_COLORS = ['#569cd6', '#4ec9b0', '#ce9178', '#c586c0', '#dcdcaa'];

export default function Dashboard() {
  const { status, tokenStats, rdResult, ll1Result, lrResult } = useCompiler();

  const tokenChartData = [
    { name: 'Keywords', value: tokenStats.keywords || 0 },
    { name: 'Identifiers', value: tokenStats.identifiers || 0 },
    { name: 'Numbers', value: tokenStats.numbers || 0 },
    { name: 'Operators', value: tokenStats.operators || 0 },
  ].filter((d) => d.value > 0);

  const parserChartData = [
    { name: 'RD', accepted: rdResult.accepted === true ? 1 : rdResult.accepted === false ? 0 : null },
    { name: 'LL(1)', accepted: ll1Result.accepted === true ? 1 : ll1Result.accepted === false ? 0 : null },
    { name: 'SLR', accepted: lrResult.accepted === true ? 1 : lrResult.accepted === false ? 0 : null },
  ].map((p) => ({
    name: p.name,
    status: p.accepted === null ? -1 : p.accepted,
    label: p.accepted === null ? 'N/A' : p.accepted ? 'Accept' : 'Reject',
  }));

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-white">Dashboard</h2>
        <p className="text-gray-500 text-sm mt-1">Mini Pascal Compiler Studio — compile, analyze, visualize</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <StatCard title="Total Tokens" value={status.token_count || 0} icon={<FiHash />} color="blue" />
        <StatCard title="Errors" value={status.error_count || 0} icon={<FiAlertTriangle />} color="red" />
        <StatCard title="Symbols" value={status.symbol_count || 0} icon={<FiDatabase />} color="purple" />
        <StatCard
          title="Status"
          value={status.compilation_status?.replace(/_/g, ' ') || 'idle'}
          icon={<FiActivity />}
          color="green"
        />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <div className="xl:col-span-2 space-y-6">
          <SourceEditor />
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="glass-card rounded-xl p-4 flex flex-col items-center gap-2">
              <span className="text-xs text-gray-500 uppercase">RD Parser</span>
              <StatusBadge accepted={rdResult.accepted} />
            </div>
            <div className="glass-card rounded-xl p-4 flex flex-col items-center gap-2">
              <span className="text-xs text-gray-500 uppercase">LL(1) Parser</span>
              <StatusBadge accepted={ll1Result.accepted} />
            </div>
            <div className="glass-card rounded-xl p-4 flex flex-col items-center gap-2">
              <span className="text-xs text-gray-500 uppercase">SLR Parser</span>
              <StatusBadge accepted={lrResult.accepted} />
            </div>
          </div>
        </div>
        <Pipeline />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="glass-card rounded-xl p-6">
          <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Token Distribution</h3>
          {tokenChartData.length ? (
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie data={tokenChartData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label>
                  {tokenChartData.map((_, i) => (
                    <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ background: '#2d2d30', border: '1px solid #3c3c3c' }} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-gray-500 text-sm text-center py-12">Run the lexer to see token distribution</p>
          )}
        </div>
        <div className="glass-card rounded-xl p-6">
          <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Parser Results</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={parserChartData}>
              <XAxis dataKey="name" stroke="#666" />
              <YAxis stroke="#666" domain={[-1, 1]} ticks={[-1, 0, 1]} tickFormatter={(v) => (v === -1 ? 'N/A' : v ? 'OK' : 'Fail')} />
              <Tooltip
                contentStyle={{ background: '#2d2d30', border: '1px solid #3c3c3c' }}
                formatter={(_, __, props) => [props.payload.label, 'Result']}
              />
              <Bar dataKey="status" fill="#569cd6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>


    </motion.div>
  );
}
