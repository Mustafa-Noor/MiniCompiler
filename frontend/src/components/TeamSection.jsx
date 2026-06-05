import { motion } from 'framer-motion';

const members = [
  { name: 'Developer 1', id: '2021-CS-XXX', focus: 'Lexer & UI' },
  { name: 'Developer 2', id: '2021-CS-XXX', focus: 'Parsers' },
  { name: 'Developer 3', id: '2021-CS-XXX', focus: 'Symbol Table' },
  { name: 'Developer 4', id: '2021-CS-XXX', focus: 'Backend API' },
];

export default function TeamSection() {
  return (
    <div className="glass-card rounded-xl p-6">
      <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Team</h3>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {members.map((m, i) => (
          <motion.div
            key={m.name}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
            className="flex items-center gap-3 p-3 rounded-lg bg-gray-800/40 border border-gray-700/40"
          >
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-sm font-bold text-white">
              {m.name[0]}
            </div>
            <div>
              <p className="text-sm font-medium text-gray-200">{m.name}</p>
              <p className="text-xs text-gray-500">{m.id} &middot; {m.focus}</p>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
