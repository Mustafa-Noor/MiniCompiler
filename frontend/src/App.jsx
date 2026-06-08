import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { CompilerProvider } from './context/CompilerContext';
import DashboardLayout from './layouts/DashboardLayout';
import Landing from './pages/Landing';
import Dashboard from './pages/Dashboard';
import LexerPage from './pages/LexerPage';
import RDParserPage from './pages/RDParserPage';
import LL1ParserPage from './pages/LL1ParserPage';
import LRParserPage from './pages/LRParserPage';
import SymbolTablePage from './pages/SymbolTablePage';
import ASTPage from './pages/ASTPage';
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
            <Route path="/lexer" element={<LexerPage />} />
            <Route path="/rd-parser" element={<RDParserPage />} />
            <Route path="/ll1-parser" element={<LL1ParserPage />} />
            <Route path="/lr-parser" element={<LRParserPage />} />
            <Route path="/symbol-table" element={<SymbolTablePage />} />
            <Route path="/ast" element={<ASTPage />} />
            <Route path="/errors" element={<ErrorsPage />} />
            <Route path="/reports" element={<ReportsPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </CompilerProvider>
  );
}
