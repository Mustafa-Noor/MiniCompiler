import { AnimatePresence, motion } from 'framer-motion';
import { FiX } from 'react-icons/fi';

const team = [
  { name: 'Team Member 1', role: 'Lexer & Frontend' },
  { name: 'Team Member 2', role: 'Parser Implementation' },
  { name: 'Team Member 3', role: 'Symbol Table & Semantics' },
  { name: 'Team Member 4', role: 'LR Parser & Integration' },
];

export default function ProjectModal({ open, onClose }) {
  return (
    <AnimatePresence>
      {open && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
          onClick={onClose}
        >
          <motion.div
            initial={{ scale: 0.95, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.95, opacity: 0 }}
            onClick={(e) => e.stopPropagation()}
            className="glass-card rounded-2xl max-w-lg w-full p-6 relative"
          >
            <button onClick={onClose} className="absolute top-4 right-4 text-gray-500 hover:text-gray-300">
              <FiX size={20} />
            </button>
            <h2 className="text-xl font-bold text-white mb-1">Mini Pascal Compiler Studio</h2>
            <p className="text-sm text-gray-400 mb-6">CS-471L Compiler Construction Lab — Final Project</p>

            <div className="space-y-4 text-sm text-gray-300">
              <p>
                A full-stack web IDE exposing a Mini Pascal compiler with lexical analysis,
                recursive descent, LL(1), and SLR parsing, symbol table management, and error handling.
              </p>
              <div>
                <h3 className="font-semibold text-gray-200 mb-2">Tech Stack</h3>
                <p className="text-gray-400">
                  React, Vite, TailwindCSS, FastAPI, Python — based on Dragon Book Appendix A grammar.
                </p>
              </div>
              <div>
                <h3 className="font-semibold text-gray-200 mb-2">Team Members</h3>
                <ul className="space-y-2">
                  {team.map((m) => (
                    <li key={m.name} className="flex justify-between text-gray-400">
                      <span>{m.name}</span>
                      <span className="text-gray-500">{m.role}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
