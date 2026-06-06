import { useMemo, useState } from 'react';
import { FiChevronLeft, FiChevronRight, FiSearch, FiHelpCircle } from 'react-icons/fi';

export default function ParsingGridTable({
  type, // 'll1', 'lr_action', 'lr_goto', 'lr_combined'
  actionData = {},
  gotoData = {},
  ll1Data = {},
  emptyTitle = 'No table data available',
  emptyDescription = 'Run the corresponding parser phase to generate this table.',
}) {
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(15);
  const [hoveredRow, setHoveredRow] = useState(null);
  const [hoveredCol, setHoveredCol] = useState(null);
  const [tooltip, setTooltip] = useState(null);

  // Parse and build the matrix structures based on type
  const { rows, cols, grid, colGroups } = useMemo(() => {
    let parsedRows = [];
    let parsedCols = [];
    let matrix = {};
    let groups = []; // For lr_combined split headers

    if (type === 'll1') {
      const allNts = new Set();
      const allTerminals = new Set();

      Object.entries(ll1Data).forEach(([key, prod]) => {
        const match = key.match(/^M\[([^,]+),\s*([^\]]+)\]$/);
        if (match) {
          const nt = match[1].trim();
          const t = match[2].trim();
          allNts.add(nt);
          allTerminals.add(t);
          if (!matrix[nt]) matrix[nt] = {};
          matrix[nt][t] = prod;
        }
      });

      parsedRows = Array.from(allNts).sort();
      // Put EOF / $ at the end of terminals
      parsedCols = Array.from(allTerminals).sort((a, b) => {
        if (a === 'EOF' || a === '$') return 1;
        if (b === 'EOF' || b === '$') return -1;
        return a.localeCompare(b);
      });
    } else if (type === 'lr_action' || type === 'lr_goto' || type === 'lr_combined') {
      const allStates = new Set();
      const actionTerms = new Set();
      const gotoNts = new Set();

      if (type === 'lr_action' || type === 'lr_combined') {
        Object.entries(actionData).forEach(([key, val]) => {
          const [action] = String(val).split(':');
          if (action === 'error') return;
          const match = key.match(/^\[(\d+),\s*([^\]]+)\]$/);
          if (match) {
            const state = parseInt(match[1]);
            const term = match[2].trim();
            allStates.add(state);
            actionTerms.add(term);
            if (!matrix[state]) matrix[state] = {};
            matrix[state][term] = { type: 'action', val };
          }
        });
      }

      if (type === 'lr_goto' || type === 'lr_combined') {
        Object.entries(gotoData).forEach(([key, val]) => {
          const match = key.match(/^\[(\d+),\s*([^\]]+)\]$/);
          if (match) {
            const state = parseInt(match[1]);
            const nt = match[2].trim();
            allStates.add(state);
            gotoNts.add(nt);
            if (!matrix[state]) matrix[state] = {};
            matrix[state][nt] = { type: 'goto', val };
          }
        });
      }

      parsedRows = Array.from(allStates).sort((a, b) => a - b);

      const sortedActionTerms = Array.from(actionTerms).sort((a, b) => {
        if (a === 'EOF' || a === '$') return 1;
        if (b === 'EOF' || b === '$') return -1;
        return a.localeCompare(b);
      });
      const sortedGotoNts = Array.from(gotoNts).sort();

      if (type === 'lr_combined') {
        parsedCols = [...sortedActionTerms, ...sortedGotoNts];
        groups = [
          { label: 'ACTION (Terminals)', colSpan: sortedActionTerms.length, className: 'bg-blue-950/20 text-blue-300 border-blue-900/30' },
          { label: 'GOTO (Non-Terminals)', colSpan: sortedGotoNts.length, className: 'bg-teal-950/20 text-teal-300 border-teal-900/30' },
        ];
      } else if (type === 'lr_action') {
        parsedCols = sortedActionTerms;
      } else {
        parsedCols = sortedGotoNts;
      }
    }

    return { rows: parsedRows, cols: parsedCols, grid: matrix, colGroups: groups };
  }, [type, ll1Data, actionData, gotoData]);

  // Filter rows based on search
  const filteredRows = useMemo(() => {
    if (!search) return rows;
    const q = search.toLowerCase();
    return rows.filter((r) => String(r).toLowerCase().includes(q));
  }, [rows, search]);

  const pagedRows = useMemo(() => {
    return filteredRows.slice(page * pageSize, (page + 1) * pageSize);
  }, [filteredRows, page, pageSize]);

  const totalPages = Math.ceil(filteredRows.length / pageSize) || 1;

  // Reset page when search or type changes
  const handleSearchChange = (e) => {
    setSearch(e.target.value);
    setPage(0);
  };

  const handlePageSizeChange = (e) => {
    setPageSize(parseInt(e.target.value));
    setPage(0);
  };

  if (!rows.length) {
    return (
      <div className="flex flex-col items-center justify-center p-8 border border-gray-800 rounded-xl bg-gray-900/10 backdrop-blur-md text-center">
        <FiHelpCircle className="text-gray-500 text-4xl mb-3" />
        <h4 className="text-sm font-semibold text-gray-300 mb-1">{emptyTitle}</h4>
        <p className="text-xs text-gray-500 max-w-sm">{emptyDescription}</p>
      </div>
    );
  }

  // Helper to render cell content for LR parser (shift/reduce/accept)
  const renderLrCell = (cellData, row, col) => {
    if (!cellData) return <span className="badge-slr-empty">-</span>;

    const { type: cellType, val } = cellData;

    if (cellType === 'action') {
      const [action, stateVal] = val.split(':');
      if (action === 'shift') {
        return <span className="badge-slr badge-slr-shift">s{stateVal}</span>;
      }
      if (action === 'reduce') {
        return <span className="badge-slr badge-slr-reduce">r{stateVal}</span>;
      }
      if (action === 'accept') {
        return <span className="badge-slr badge-slr-accept">acc</span>;
      }
      if (action === 'error') {
        return <span className="badge-slr-empty">-</span>;
      }
    } else if (cellType === 'goto') {
      return <span className="badge-slr px-2 bg-teal-500/10 text-teal-400 border border-teal-500/20">{val}</span>;
    }

    return <span>{val}</span>;
  };

  // Helper to get tooltip explanation
  const getCellExplanation = (row, col, cellData) => {
    if (type === 'll1') {
      return cellData
        ? `M[${row}, ${col}] -> Expand Non-Terminal "${row}" by production: ${row} -> ${cellData}`
        : `M[${row}, ${col}] -> Error state (blank / no rule)`;
    } else {
      if (!cellData) return `State ${row}, Symbol "${col}" -> Syntax Error`;
      const { type: cellType, val } = cellData;
      if (cellType === 'action') {
        const [action, stateVal] = val.split(':');
        if (action === 'shift') return `State ${row}, Terminal "${col}" -> Shift terminal to stack, transition to State ${stateVal}`;
        if (action === 'reduce') return `State ${row}, Terminal "${col}" -> Reduce by Production Rule #${stateVal}`;
        if (action === 'accept') return `State ${row}, Terminal "${col}" -> Accept program! Parsing successfully completed.`;
      } else if (cellType === 'goto') {
        return `State ${row}, Non-Terminal "${col}" -> Transition to State ${val} after reduction`;
      }
    }
    return '';
  };

  return (
    <div className="flex flex-col gap-4 relative">
      {/* Search and Pagination Size Controls */}
      <div className="flex flex-wrap items-center justify-between gap-3 bg-gray-900/35 p-3 rounded-lg border border-gray-800/60 backdrop-blur-sm">
        <div className="relative flex-1 min-w-[200px] max-w-md">
          <FiSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            value={search}
            onChange={handleSearchChange}
            placeholder={type === 'll1' ? 'Search non-terminals...' : 'Search states...'}
            className="w-full pl-10 pr-4 py-1.5 rounded-lg bg-gray-800/40 border border-gray-700/60 text-xs text-gray-200 outline-none focus:border-blue-500/50"
          />
        </div>
        <div className="flex items-center gap-2 text-xs text-gray-400">
          <span>Rows per page:</span>
          <select
            value={pageSize}
            onChange={handlePageSizeChange}
            className="bg-gray-800/50 border border-gray-700 rounded px-2 py-1 text-gray-200 focus:outline-none focus:border-blue-500"
          >
            {[10, 15, 25, 50, 100].map((size) => (
              <option key={size} value={size}>
                {size}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Main Grid Wrapper */}
      <div className="overflow-x-auto rounded-xl border border-gray-800 bg-gray-950/40 backdrop-blur-md scrollbar-thin relative max-h-[600px]">
        <table className="min-w-full text-xs text-left border-collapse table-layout-fixed">
          <thead>
            {/* Top row split headers (SLR Combined ACTION/GOTO) */}
            {colGroups.length > 0 && (
              <tr>
                <th rowSpan={2} className="px-4 py-3 bg-gray-800/70 border-b border-r border-gray-800 sticky-column text-center text-gray-300 font-semibold uppercase tracking-wider">
                  State
                </th>
                {colGroups.map((g, idx) => (
                  <th
                    key={idx}
                    colSpan={g.colSpan}
                    className={`px-4 py-2 border-b border-r border-gray-800 text-center font-bold tracking-wider ${g.className}`}
                  >
                    {g.label}
                  </th>
                ))}
              </tr>
            )}

            {/* Main Header Row */}
            <tr className="bg-gray-800/50 border-b border-gray-800">
              {colGroups.length === 0 && (
                <th className="px-4 py-3 bg-gray-800/70 border-r border-gray-800 sticky-column text-gray-300 font-semibold uppercase tracking-wider min-w-[100px]">
                  {type === 'll1' ? 'Non-Terminal' : 'State'}
                </th>
              )}
              {cols.map((col, colIdx) => {
                const isHovered = hoveredCol === colIdx;
                return (
                  <th
                    key={col}
                    className={`px-3 py-3 border-r border-gray-800/40 text-center font-mono font-bold transition-all min-w-[70px] ${
                      isHovered ? 'bg-gray-700/30 text-blue-300' : 'text-gray-400'
                    }`}
                  >
                    {col.startsWith('KEYWORD_') ? col.substring(8) : col}
                  </th>
                );
              })}
            </tr>
          </thead>
          <tbody>
            {pagedRows.map((row, rowIdx) => {
              const globalRowIdx = page * pageSize + rowIdx;
              const isRowHovered = hoveredRow === globalRowIdx;

              return (
                <tr
                  key={row}
                  className={`border-b border-gray-800/30 transition-all ${
                    isRowHovered ? 'bg-gray-800/20' : ''
                  }`}
                >
                  {/* First cell (Non-terminal or State) */}
                  <td
                    className={`px-4 py-2.5 font-bold border-r border-gray-800 sticky-column font-mono text-xs ${
                      isRowHovered ? 'text-blue-400 bg-gray-900' : 'text-gray-300'
                    }`}
                  >
                    {row}
                  </td>

                  {/* Matrix cells */}
                  {cols.map((col, colIdx) => {
                    const val = grid[row]?.[col];
                    const isColHovered = hoveredCol === colIdx;
                    const isCellHovered = isRowHovered && isColHovered;
                    const hasData = val !== undefined && val !== null;

                    return (
                      <td
                        key={col}
                        onMouseEnter={(e) => {
                          setHoveredRow(globalRowIdx);
                          setHoveredCol(colIdx);
                          setTooltip({
                            text: getCellExplanation(row, col, val),
                            x: e.clientX,
                            y: e.clientY - 10,
                          });
                        }}
                        onMouseMove={(e) => {
                          setTooltip((prev) =>
                            prev ? { ...prev, x: e.clientX, y: e.clientY - 10 } : null
                          );
                        }}
                        onMouseLeave={() => {
                          setHoveredRow(null);
                          setHoveredCol(null);
                          setTooltip(null);
                        }}
                        className={`px-2 py-2 border-r border-gray-800/20 text-center transition-colors font-mono text-xs cursor-help ${
                          isCellHovered
                            ? 'bg-blue-500/10'
                            : isColHovered || isRowHovered
                            ? 'bg-gray-800/10'
                            : ''
                        } ${hasData ? '' : 'opacity-40'}`}
                      >
                        {type === 'll1' ? (
                          val ? (
                            <span className="text-gray-200 font-sans tracking-wide">
                              <span className="text-pink-400 font-bold font-mono">→</span>{' '}
                              {val.split(' ').map((sym, idx) => {
                                const isTerminal = sym.startsWith('KEYWORD_') || sym === 'ID' || sym === 'NUMBER' || sym === 'relop' || sym === 'mulop' || sym === 'PLUS' || sym === 'MINUS' || sym === 'MULTIPLY' || sym === 'DIVIDE' || sym === 'ASSIGN' || sym === 'SEMICOLON' || sym === 'COLON' || sym === 'COMMA' || sym === 'DOT' || sym === 'DOUBLE_DOT' || sym === 'LPAREN' || sym === 'RPAREN' || sym === 'LBRACKET' || sym === 'RBRACKET' || sym === 'EOF';
                                const label = sym.startsWith('KEYWORD_') ? sym.substring(8) : sym;
                                return (
                                  <span
                                    key={idx}
                                    className={`mr-1 px-1 rounded-sm text-[10px] ${
                                      isTerminal
                                        ? 'text-blue-300 font-semibold'
                                        : 'text-gray-400 font-light'
                                    }`}
                                  >
                                    {label === 'EPSILON' ? 'ε' : label}
                                  </span>
                                );
                              })}
                            </span>
                          ) : (
                            <span className="text-gray-600">-</span>
                          )
                        ) : (
                          renderLrCell(val, row, col)
                        )}
                      </td>
                    );
                  })}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Pagination Controls */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between text-xs text-gray-400 px-1">
          <span>Showing {page * pageSize + 1} - {Math.min((page + 1) * pageSize, filteredRows.length)} of {filteredRows.length} rows</span>
          <div className="flex gap-2 items-center">
            <button
              disabled={page === 0}
              onClick={() => setPage((p) => p - 1)}
              className="p-1.5 rounded-lg border border-gray-700 bg-gray-800/40 text-gray-300 hover:bg-gray-700/40 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
            >
              <FiChevronLeft size={16} />
            </button>
            <span>
              Page <span className="text-gray-200 font-semibold">{page + 1}</span> of <span className="text-gray-200 font-semibold">{totalPages}</span>
            </span>
            <button
              disabled={page >= totalPages - 1}
              onClick={() => setPage((p) => p + 1)}
              className="p-1.5 rounded-lg border border-gray-700 bg-gray-800/40 text-gray-300 hover:bg-gray-700/40 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
            >
              <FiChevronRight size={16} />
            </button>
          </div>
        </div>
      )}

      {/* Custom Tooltip */}
      {tooltip && (
        <div
          className="fixed z-[9999] pointer-events-none bg-gray-900 border border-gray-700 text-gray-100 text-[11px] px-3 py-2 rounded shadow-2xl max-w-sm backdrop-blur-md transition-opacity duration-150 ease-out font-sans font-medium leading-relaxed"
          style={{
            left: `${tooltip.x + 15}px`,
            top: `${tooltip.y - 15}px`,
            transform: 'translateY(-100%)',
          }}
        >
          {tooltip.text}
        </div>
      )}
    </div>
  );
}
