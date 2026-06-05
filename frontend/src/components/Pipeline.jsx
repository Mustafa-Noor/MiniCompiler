import { motion } from 'framer-motion';
import { FiArrowDown, FiCheck, FiCircle } from 'react-icons/fi';
import { useCompiler } from '../context/CompilerContext';

const steps = [
  { id: 'source', label: 'Source', key: 'idle' },
  { id: 'lexer', label: 'Lexer', key: 'lexed' },
  { id: 'parser', label: 'Parser', key: 'parsed' },
  { id: 'symbol', label: 'Symbol Table', key: 'symbols' },
  { id: 'errors', label: 'Error Handler', key: 'errors' },
  { id: 'result', label: 'Result', key: 'done' },
];

function getStepIndex(status) {
  if (!status || status === 'idle') return 0;
  if (status === 'lexed' || status === 'lexical_error') return 1;
  if (status.startsWith('parsed') || status.includes('rejected')) return 2;
  if (status.includes('symbol')) return 3;
  return 4;
}

export default function Pipeline() {
  const { status } = useCompiler();
  const activeIdx = getStepIndex(status.compilation_status);

  return (
    <div className="glass-card rounded-xl p-6">
      <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-6">
        Compilation Pipeline
      </h3>
      <div className="flex flex-col items-center gap-1">
        {steps.map((step, i) => {
          const done = i < activeIdx;
          const active = i === activeIdx;
          return (
            <div key={step.id} className="flex flex-col items-center w-full">
              <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: i * 0.08 }}
                className={`w-full max-w-xs flex items-center gap-3 px-4 py-3 rounded-lg border transition-all ${
                  active
                    ? 'border-blue-500/50 bg-blue-500/10 animate-pulse-glow'
                    : done
                    ? 'border-emerald-500/30 bg-emerald-500/5'
                    : 'border-gray-700/50 bg-gray-800/30'
                }`}
              >
                {done ? (
                  <FiCheck className="text-emerald-400 shrink-0" />
                ) : (
                  <FiCircle className={`shrink-0 ${active ? 'text-blue-400' : 'text-gray-600'}`} />
                )}
                <span className={`font-medium ${active ? 'text-blue-300' : done ? 'text-emerald-300' : 'text-gray-500'}`}>
                  {step.label}
                </span>
              </motion.div>
              {i < steps.length - 1 && (
                <FiArrowDown className="text-gray-600 my-1" />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
