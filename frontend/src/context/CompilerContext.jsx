import { createContext, useCallback, useContext, useEffect, useState } from 'react';
import * as api from '../services/api';

const CompilerContext = createContext(null);

const DEFAULT_SOURCE = `program GCD;
var
    x, y: integer;
    result: integer;

function gcd(a, b: integer): integer;
begin
    if b = 0 then
        gcd := a
    else
        gcd := gcd(b, a mod b)
end;

begin
    read(x, y);
    result := gcd(x, y);
    write(result)
end.`;

export function CompilerProvider({ children }) {
  const [sourceCode, setSourceCode] = useState(DEFAULT_SOURCE);
  const [filename, setFilename] = useState('sample.pas');
  const [loading, setLoading] = useState(false);
  const [loadingAction, setLoadingAction] = useState('');
  const [toasts, setToasts] = useState([]);

  const [status, setStatus] = useState({
    compilation_status: 'idle',
    token_count: 0,
    error_count: 0,
    symbol_count: 0,
    token_statistics: {},
    rd_accepted: null,
    ll1_accepted: null,
    lr_accepted: null,
  });

  const [tokens, setTokens] = useState([]);
  const [tokenStats, setTokenStats] = useState({});
  const [rdResult, setRdResult] = useState({ accepted: null, trace: [] });
  const [ll1Result, setLl1Result] = useState({
    accepted: null, first_sets: {}, follow_sets: {}, parsing_table: {}, trace: [],
  });
  const [lrResult, setLrResult] = useState({
    accepted: null, action_table: {}, goto_table: {}, trace: [],
  });
  const [symbols, setSymbols] = useState([]);
  const [errors, setErrors] = useState([]);
  const [reports, setReports] = useState({ reports: {}, labels: {} });

  const addToast = useCallback((message, type = 'info') => {
    const id = Date.now();
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4000);
  }, []);

  const refreshStatus = useCallback(async () => {
    try {
      const data = await api.getStatus();
      setStatus(data);
    } catch {
      /* backend may be offline */
    }
  }, []);

  useEffect(() => {
    refreshStatus();
  }, [refreshStatus]);

  const ensureSourceSaved = useCallback(async () => {
    await api.saveSource(sourceCode, filename);
  }, [sourceCode, filename]);

  const withLoading = useCallback(async (action, label, fn) => {
    setLoading(true);
    setLoadingAction(label);
    try {
      await ensureSourceSaved();
      const result = await fn();
      await refreshStatus();
      addToast(`${action} completed successfully`, 'success');
      return result;
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || 'Operation failed';
      addToast(msg, 'error');
      throw err;
    } finally {
      setLoading(false);
      setLoadingAction('');
    }
  }, [addToast, ensureSourceSaved, refreshStatus]);

  const uploadSource = useCallback(async (file) => {
    setLoading(true);
    setLoadingAction('Uploading');
    try {
      const data = await api.uploadFile(file);
      setFilename(data.filename);
      const src = await api.getSource();
      setSourceCode(src.source_code);
      addToast(`Uploaded ${data.filename}`, 'success');
      await refreshStatus();
    } catch (err) {
      addToast(err.response?.data?.detail || 'Upload failed', 'error');
    } finally {
      setLoading(false);
      setLoadingAction('');
    }
  }, [addToast, refreshStatus]);

  const runLexerAction = useCallback(() => withLoading('Lexer', 'Running Lexer', async () => {
    const data = await api.runLexer();
    setTokens(data.tokens);
    setTokenStats(data.statistics);
    return data;
  }), [withLoading]);

  const runRDAction = useCallback(() => withLoading('RD Parser', 'Running RD Parser', async () => {
    const data = await api.runRDParser();
    setRdResult(data);
    const errs = await api.getErrors();
    setErrors(errs.errors);
    return data;
  }), [withLoading]);

  const runLL1Action = useCallback(() => withLoading('LL(1) Parser', 'Running LL(1) Parser', async () => {
    const data = await api.runLL1Parser();
    setLl1Result(data);
    const errs = await api.getErrors();
    setErrors(errs.errors);
    return data;
  }), [withLoading]);

  const runLRAction = useCallback(() => withLoading('LR Parser', 'Running LR Parser', async () => {
    const data = await api.runLRParser();
    setLrResult(data);
    const errs = await api.getErrors();
    setErrors(errs.errors);
    return data;
  }), [withLoading]);

  const loadSymbolTable = useCallback(async () => {
    try {
      const data = await api.getSymbolTable();
      setSymbols(data.entries);
      await refreshStatus();
    } catch (err) {
      addToast(err.response?.data?.detail || 'Failed to load symbol table', 'error');
    }
  }, [addToast, refreshStatus]);

  const loadErrors = useCallback(async () => {
    try {
      const data = await api.getErrors();
      setErrors(data.errors);
    } catch (err) {
      addToast('Failed to load errors', 'error');
    }
  }, [addToast]);

  const loadReports = useCallback(async () => {
    try {
      const data = await api.getReports();
      setReports(data);
    } catch (err) {
      addToast('Failed to load reports', 'error');
    }
  }, [addToast]);

  const value = {
    sourceCode, setSourceCode, filename, setFilename,
    loading, loadingAction, toasts,
    status, tokens, tokenStats,
    rdResult, ll1Result, lrResult, symbols, errors, reports,
    uploadSource, runLexerAction, runRDAction, runLL1Action, runLRAction,
    loadSymbolTable, loadErrors, loadReports, refreshStatus, addToast,
  };

  return (
    <CompilerContext.Provider value={value}>
      {children}
    </CompilerContext.Provider>
  );
}

export const useCompiler = () => {
  const ctx = useContext(CompilerContext);
  if (!ctx) throw new Error('useCompiler must be used within CompilerProvider');
  return ctx;
};
