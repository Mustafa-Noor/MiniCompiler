import { motion } from 'framer-motion';
import { FiLoader } from 'react-icons/fi';
import { useCompiler } from '../context/CompilerContext';

export default function LoadingOverlay() {
  const { loading, loadingAction } = useCompiler();
  if (!loading) return null;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-40 flex items-center justify-center bg-black/50 backdrop-blur-sm"
    >
      <div className="glass-card rounded-xl px-8 py-6 flex flex-col items-center gap-4">
        <FiLoader className="text-3xl text-blue-400 animate-spin" />
        <p className="text-gray-300 font-medium">{loadingAction || 'Processing...'}</p>
      </div>
    </motion.div>
  );
}
