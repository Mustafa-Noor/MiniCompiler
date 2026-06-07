import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { FiCpu, FiCode, FiLayers, FiGitBranch, FiFileText, FiDatabase } from 'react-icons/fi';
import LandingCanvas from '../components/LandingCanvas';

const features = [
  {
    icon: FiCode,
    title: 'Lexical Analysis',
    desc: 'Double-buffered scanner generating categorized tokens and tracking coordinates.',
  },
  {
    icon: FiGitBranch,
    title: 'Recursive Descent',
    desc: 'Top-down parser featuring fully-nested visual entry/exit trace logging.',
  },
  {
    icon: FiLayers,
    title: 'LL(1) Predictor',
    desc: 'Predictive table-driven parsing built on automated FIRST & FOLLOW sets.',
  },
  {
    icon: FiCpu,
    title: 'SLR(1) Bottom-Up',
    desc: 'Shift-reduce parsing driven by LR(0) state closures and ACTION/GOTO tables.',
  },
  {
    icon: FiDatabase,
    title: 'Semantic Checker',
    desc: 'Type analysis, parameter counts, and scoped symbol table integrity.',
  },
  {
    icon: FiFileText,
    title: 'Diagnostic Reports',
    desc: 'Complete downloadable compiler listings, parsing trees, and error logs.',
  },
];

export default function Landing() {
  const navigate = useNavigate();

  return (
    <div className="relative min-h-screen w-full overflow-x-hidden flex flex-col justify-between select-none text-slate-200">
      {/* 3D Interactive Background */}
      <LandingCanvas />

      {/* Top Navbar */}
      <header className="relative z-10 w-full px-6 py-5 max-w-7xl mx-auto flex justify-between items-center bg-transparent">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-sky-500 to-indigo-600 flex items-center justify-center font-bold text-white shadow-md shadow-sky-500/20">
            P
          </div>
          <div>
            <h1 className="text-lg font-bold text-white tracking-wide">Pascal Studio</h1>
            <p className="text-[9px] text-sky-400 uppercase tracking-widest leading-none">Mini Compiler</p>
          </div>
        </div>
        <button
          onClick={() => navigate('/studio')}
          className="relative group px-5 py-2 overflow-hidden rounded-lg bg-slate-900/40 border border-slate-700/50 backdrop-blur-sm hover:border-sky-500/50 transition-all duration-300"
        >
          <span className="relative z-10 text-xs font-semibold tracking-wider text-slate-300 group-hover:text-sky-300 transition-colors">
            ENTER STUDIO
          </span>
          <div className="absolute inset-0 w-full h-full -z-0 bg-gradient-to-r from-sky-500/10 to-indigo-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
        </button>
      </header>

      {/* Main Content Area */}
      <main className="relative z-10 w-full max-w-7xl mx-auto px-6 py-12 flex-1 flex flex-col justify-center gap-12 lg:gap-20">
        
        {/* Hero Section */}
        <div className="max-w-3xl flex flex-col items-start text-left gap-6">
          <motion.div
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="flex items-center gap-2 px-3 py-1 rounded-full bg-sky-500/10 border border-sky-500/20 text-sky-400 text-xs font-semibold tracking-wide uppercase shadow-[0_0_15px_rgba(14,165,233,0.08)]"
          >
            <span className="flex h-2 w-2 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-sky-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-sky-500"></span>
            </span>
            COMPILER CONSTRUCTION LABORATORY
          </motion.div>

          <motion.h2
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-4xl sm:text-6xl font-extrabold text-white tracking-tight leading-none"
          >
            Mini Pascal <br />
            <span className="bg-gradient-to-r from-sky-400 via-blue-400 to-indigo-400 bg-clip-text text-transparent drop-shadow-[0_2px_10px_rgba(56,189,248,0.15)]">
              Compiler Studio
            </span>
          </motion.h2>

          <motion.p
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="text-base sm:text-lg text-slate-400 leading-relaxed font-light"
          >
            A high-fidelity interactive visualization and development environment for compiler construction. Write, compile, and visualize lexical scanning, grammar derivations, LL(1) parse tables, SLR(1) state diagrams, scoped symbol tables, and semantic constraints.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="flex flex-wrap gap-4 mt-2"
          >
            <button
              onClick={() => navigate('/studio')}
              className="px-8 py-3.5 rounded-xl text-sm font-semibold tracking-wider bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 text-white shadow-lg shadow-sky-500/25 hover:shadow-sky-500/40 transition-all duration-300 transform hover:-translate-y-0.5"
            >
              Open Studio Workspace
            </button>
            <a
              href="#features"
              className="px-6 py-3.5 rounded-xl text-sm font-semibold tracking-wider bg-slate-900/60 hover:bg-slate-900/90 border border-slate-800 hover:border-slate-700 text-slate-300 transition-all duration-300"
            >
              Learn More
            </a>
          </motion.div>
        </div>

        {/* Feature grid */}
        <section id="features" className="space-y-6 pt-10">
          <div className="flex flex-col gap-2">
            <h3 className="text-xs uppercase tracking-widest text-sky-400 font-bold">Compiler Architecture</h3>
            <p className="text-xl font-bold text-white">Full-stack Front End Analysis</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feat, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: '-50px' }}
                transition={{ duration: 0.5, delay: index * 0.05 }}
                className="group relative p-6 rounded-2xl bg-slate-950/45 border border-slate-900/60 backdrop-blur-md hover:border-sky-500/20 hover:bg-slate-950/70 transition-all duration-300"
              >
                {/* Glowing border effect */}
                <div className="absolute inset-0 rounded-2xl bg-gradient-to-tr from-sky-500/5 to-indigo-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />
                
                <div className="w-10 h-10 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-center text-sky-400 mb-4 group-hover:border-sky-500/30 group-hover:bg-sky-950/20 transition-all">
                  <feat.icon className="text-lg" />
                </div>
                <h4 className="text-md font-bold text-white group-hover:text-sky-300 transition-colors mb-2">
                  {feat.title}
                </h4>
                <p className="text-xs text-slate-400 leading-relaxed font-light">
                  {feat.desc}
                </p>
              </motion.div>
            ))}
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="relative z-10 w-full py-6 px-6 border-t border-slate-900/50 bg-slate-950/10 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row justify-between items-center gap-4 text-xs text-slate-500">
          <p>© 2026 Mini Pascal Compiler Studio. Department of Computer Science.</p>
          <div className="flex gap-4">
            <span className="hover:text-slate-400 transition-colors cursor-help">Lab Course CS-471L</span>
            <span>•</span>
            <span className="hover:text-slate-400 transition-colors cursor-help font-mono">v1.0.0</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
