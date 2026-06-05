import { motion } from 'framer-motion';
import { FiInbox } from 'react-icons/fi';

export default function EmptyState({ title = 'No data yet', description, action }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex flex-col items-center justify-center py-16 px-6 text-center"
    >
      <div className="w-16 h-16 rounded-2xl glass flex items-center justify-center mb-4">
        <FiInbox className="text-3xl text-gray-500" />
      </div>
      <h3 className="text-lg font-semibold text-gray-300 mb-2">{title}</h3>
      {description && <p className="text-sm text-gray-500 max-w-md mb-4">{description}</p>}
      {action}
    </motion.div>
  );
}
