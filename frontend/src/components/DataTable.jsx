import { useMemo, useState } from 'react';
import { FiChevronDown, FiChevronUp, FiSearch, FiX } from 'react-icons/fi';
import EmptyState from './EmptyState';

function HighlightText({ text, query }) {
  if (!query) return <span>{text}</span>;
  const str = String(text ?? '');
  const escapedQuery = query.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
  const parts = str.split(new RegExp(`(${escapedQuery})`, 'gi'));
  return (
    <span>
      {parts.map((part, i) =>
        part.toLowerCase() === query.toLowerCase() ? (
          <mark key={i} className="search-highlight">
            {part}
          </mark>
        ) : (
          part
        )
      )}
    </span>
  );
}

export default function DataTable({
  columns,
  data,
  emptyTitle,
  emptyDescription,
  searchable = true,
  searchKeys,
  pageSize = 50,
}) {
  const [search, setSearch] = useState('');
  const [sortKey, setSortKey] = useState(null);
  const [sortDir, setSortDir] = useState('asc');
  const [filterCol, setFilterCol] = useState('');
  const [page, setPage] = useState(0);

  const filtered = useMemo(() => {
    let rows = [...data];
    if (search) {
      const q = search.toLowerCase();
      const keys = searchKeys || columns.map((c) => c.key);
      rows = rows.filter((row) =>
        keys.some((k) => String(row[k] ?? '').toLowerCase().includes(q))
      );
    }
    if (filterCol) {
      rows = rows.filter((row) => String(row[columns[0]?.key] ?? '').includes(filterCol));
    }
    if (sortKey) {
      rows.sort((a, b) => {
        const av = String(a[sortKey] ?? '');
        const bv = String(b[sortKey] ?? '');
        return sortDir === 'asc' ? av.localeCompare(bv, undefined, { numeric: true }) : bv.localeCompare(av, undefined, { numeric: true });
      });
    }
    return rows;
  }, [data, search, sortKey, sortDir, filterCol, columns, searchKeys]);

  const paged = filtered.slice(page * pageSize, (page + 1) * pageSize);
  const totalPages = Math.ceil(filtered.length / pageSize) || 1;

  const toggleSort = (key) => {
    if (sortKey === key) setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'));
    else { setSortKey(key); setSortDir('asc'); }
  };

  if (!data.length) {
    return <EmptyState title={emptyTitle} description={emptyDescription} />;
  }

  return (
    <div className="flex flex-col gap-4">
      {searchable && (
        <div className="flex flex-wrap gap-3">
          <div className="relative flex-1 min-w-[200px]">
            <FiSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              value={search}
              onChange={(e) => { setSearch(e.target.value); setPage(0); }}
              placeholder="Search..."
              className="w-full pl-10 pr-10 py-2 rounded-lg bg-gray-800/40 border border-gray-700/60 text-sm text-gray-200 outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/30 transition-all placeholder-gray-500"
            />
            {search && (
              <button
                onClick={() => { setSearch(''); setPage(0); }}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-200 transition-colors"
              >
                <FiX size={16} />
              </button>
            )}
          </div>
        </div>
      )}
      <div className="overflow-x-auto rounded-xl border border-gray-800/80 bg-gray-900/20 backdrop-blur-md scrollbar-thin">
        <table className="w-full text-sm border-collapse">
          <thead>
            <tr className="bg-gray-800/60 text-left border-b border-gray-800/80">
              {columns.map((col) => (
                <th
                  key={col.key}
                  onClick={() => col.sortable !== false && toggleSort(col.key)}
                  className={`px-4 py-3 text-xs uppercase tracking-wider text-gray-400 font-semibold transition-colors ${col.sortable !== false ? 'cursor-pointer hover:text-gray-200 hover:bg-gray-800/30' : ''}`}
                >
                  <span className="flex items-center gap-1.5">
                    {col.label}
                    {sortKey === col.key && (sortDir === 'asc' ? <FiChevronUp className="text-blue-400" /> : <FiChevronDown className="text-blue-400" />)}
                  </span>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {paged.map((row, i) => (
              <tr key={i} className="border-b border-gray-800/40 hover:bg-gray-800/20 transition-all table-crosshair-row">
                {columns.map((col) => (
                  <td key={col.key} className="px-4 py-2.5 text-gray-300 font-mono text-xs table-crosshair-cell">
                    {col.render ? (
                      col.render(row[col.key], row)
                    ) : (
                      <HighlightText text={row[col.key]} query={search} />
                    )}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {totalPages > 1 && (
        <div className="flex items-center justify-between text-xs text-gray-400 px-1">
          <span>Showing {page * pageSize + 1} - {Math.min((page + 1) * pageSize, filtered.length)} of {filtered.length} rows</span>
          <div className="flex gap-2 items-center">
            <button
              disabled={page === 0}
              onClick={() => setPage((p) => p - 1)}
              className="px-3 py-1.5 rounded-lg border border-gray-700 bg-gray-800/40 text-gray-300 hover:bg-gray-700/40 disabled:opacity-40 disabled:hover:bg-gray-800/40 disabled:cursor-not-allowed transition-all font-medium"
            >
              Prev
            </button>
            <span className="px-2 text-gray-400">
              Page <span className="text-gray-200 font-semibold">{page + 1}</span> of <span className="text-gray-200 font-semibold">{totalPages}</span>
            </span>
            <button
              disabled={page >= totalPages - 1}
              onClick={() => setPage((p) => p + 1)}
              className="px-3 py-1.5 rounded-lg border border-gray-700 bg-gray-800/40 text-gray-300 hover:bg-gray-700/40 disabled:opacity-40 disabled:hover:bg-gray-800/40 disabled:cursor-not-allowed transition-all font-medium"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

