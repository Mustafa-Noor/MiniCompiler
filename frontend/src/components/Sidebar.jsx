import { NavLink } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  FiHome, FiCode, FiGitBranch, FiLayers, FiCpu,
  FiDatabase, FiAlertTriangle, FiFileText, FiInfo, FiShare2,
} from 'react-icons/fi';
import { useState } from 'react';
import ProjectModal from './ProjectModal';

const navItems = [
  { to: '/studio', icon: FiHome, label: 'Dashboard' },
  { to: '/lexer', icon: FiCode, label: 'Lexer' },
  { to: '/rd-parser', icon: FiGitBranch, label: 'RD Parser' },
  { to: '/ll1-parser', icon: FiLayers, label: 'LL1 Parser' },
  { to: '/lr-parser', icon: FiCpu, label: 'LR Parser' },
  { to: '/symbol-table', icon: FiDatabase, label: 'Symbol Table' },
  { to: '/ast', icon: FiShare2, label: 'AST Tree' },
  { to: '/errors', icon: FiAlertTriangle, label: 'Error Handler' },
  { to: '/reports', icon: FiFileText, label: 'Reports' },
];

export default function Sidebar() {
  const [showModal, setShowModal] = useState(false);

  return (
    <>
      <aside className="w-60 shrink-0 h-full glass border-r border-gray-800/60 flex flex-col">
        <div className="p-5 border-b border-gray-800/60">
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <h1 className="text-lg font-bold bg-gradient-to-r from-blue-400 to-cyan-300 bg-clip-text text-transparent">
              Pascal Studio
            </h1>
            <p className="text-[10px] text-gray-500 uppercase tracking-widest mt-1">
              Mini Compiler IDE
            </p>
          </motion.div>
        </div>
        <nav className="flex-1 p-3 space-y-1 overflow-y-auto scrollbar-thin">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-blue-600/20 text-blue-300 border border-blue-500/30'
                    : 'text-gray-400 hover:bg-gray-800/50 hover:text-gray-200'
                }`
              }
            >
              <item.icon className="text-lg shrink-0" />
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="p-3 border-t border-gray-800/60">
          <button
            onClick={() => setShowModal(true)}
            className="flex items-center gap-2 w-full px-3 py-2 rounded-lg text-sm text-gray-400 hover:bg-gray-800/50 hover:text-gray-200 transition-all"
          >
            <FiInfo /> Project Info
          </button>
        </div>
      </aside>
      <ProjectModal open={showModal} onClose={() => setShowModal(false)} />
    </>
  );
}
