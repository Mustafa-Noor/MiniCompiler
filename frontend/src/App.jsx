import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { CompilerProvider } from './context/CompilerContext';
import DashboardLayout from './layouts/DashboardLayout';
import Landing from './pages/Landing';
import Dashboard from './pages/Dashboard';
import LexerPage from './pages/LexerPage';
import RDParserPage from './pages/RDParserPage';
import LL1ParserPage from './pages/LL1ParserPage';
import LRParserPage from './pages/LRParserPage';
import ASTViewerPage from './pages/ASTViewerPage';
import SymbolTablePage from './pages/SymbolTablePage';
import ErrorsPage from './pages/ErrorsPage';
import ReportsPage from './pages/ReportsPage';

export default function App() {
  return (
    <CompilerProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route element={<DashboardLayout />}>
            <Route path="/studio" element={<Dashboard />} />
            <Route path="/studio/lexer" element={<LexerPage />} />
            <Route path="/studio/rd-parser" element={<RDParserPage />} />
            <Route path="/studio/ll1-parser" element={<LL1ParserPage />} />
            <Route path="/studio/lr-parser" element={<LRParserPage />} />
            <Route path="/studio/ast-viewer" element={<ASTViewerPage />} />
            <Route path="/studio/symbol-table" element={<SymbolTablePage />} />
            <Route path="/studio/errors" element={<ErrorsPage />} />
            <Route path="/studio/reports" element={<ReportsPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </CompilerProvider>
  );
}

