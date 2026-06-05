import { AnimatePresence, motion } from 'framer-motion';
import { FiAlertCircle, FiCheckCircle, FiInfo } from 'react-icons/fi';
import { useCompiler } from '../context/CompilerContext';

const icons = {
  success: <FiCheckCircle className="text-emerald-400" />,
  error: <FiAlertCircle className="text-red-400" />,
  info: <FiInfo className="text-blue-400" />,
};

const borders = {
  success: 'border-emerald-500/30',
  error: 'border-red-500/30',
  info: 'border-blue-500/30',
};

export default function ToastContainer() {
  const { toasts } = useCompiler();

  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col gap-2">
      <AnimatePresence>
        {toasts.map((toast) => (
          <motion.div
            key={toast.id}
            initial={{ opacity: 0, x: 80, scale: 0.95 }}
            animate={{ opacity: 1, x: 0, scale: 1 }}
            exit={{ opacity: 0, x: 80, scale: 0.95 }}
            className={`glass-card flex items-center gap-3 px-4 py-3 rounded-lg min-w-[280px] border ${borders[toast.type]}`}
          >
            {icons[toast.type]}
            <span className="text-sm text-gray-200">{toast.message}</span>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
