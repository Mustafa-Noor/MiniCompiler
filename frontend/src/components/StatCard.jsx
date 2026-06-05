import { motion } from 'framer-motion';

const colorMap = {
  blue: 'from-blue-600/20 to-blue-900/10 border-blue-500/20 text-blue-400',
  green: 'from-emerald-600/20 to-emerald-900/10 border-emerald-500/20 text-emerald-400',
  red: 'from-red-600/20 to-red-900/10 border-red-500/20 text-red-400',
  purple: 'from-purple-600/20 to-purple-900/10 border-purple-500/20 text-purple-400',
  orange: 'from-orange-600/20 to-orange-900/10 border-orange-500/20 text-orange-400',
};

export default function StatCard({ title, value, icon, color = 'blue', subtitle }) {
  return (
    <motion.div
      whileHover={{ scale: 1.02, y: -2 }}
      className={`glass-card rounded-xl p-5 border bg-gradient-to-br ${colorMap[color]}`}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs uppercase tracking-wider text-gray-500 mb-1">{title}</p>
          <p className="text-3xl font-bold text-white">{value}</p>
          {subtitle && <p className="text-xs text-gray-500 mt-1">{subtitle}</p>}
        </div>
        <div className="text-2xl opacity-80">{icon}</div>
      </div>
    </motion.div>
  );
}
