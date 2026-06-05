import { useMemo, useState } from 'react';
import { FiChevronDown, FiChevronUp, FiSearch } from 'react-icons/fi';
import EmptyState from './EmptyState';

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
    <div className="flex flex-col gap-3">
      {searchable && (
        <div className="flex flex-wrap gap-3">
          <div className="relative flex-1 min-w-[200px]">
            <FiSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
            <input
              value={search}
              onChange={(e) => { setSearch(e.target.value); setPage(0); }}
              placeholder="Search..."
              className="w-full pl-10 pr-4 py-2 rounded-lg bg-gray-800/60 border border-gray-700 text-sm text-gray-200 outline-none focus:border-blue-500/50"
            />
          </div>
        </div>
      )}
      <div className="overflow-x-auto rounded-xl border border-gray-700/50 scrollbar-thin">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-gray-800/80 text-left">
              {columns.map((col) => (
                <th
                  key={col.key}
                  onClick={() => col.sortable !== false && toggleSort(col.key)}
                  className={`px-4 py-3 text-xs uppercase tracking-wider text-gray-400 font-semibold ${col.sortable !== false ? 'cursor-pointer hover:text-gray-200' : ''}`}
                >
                  <span className="flex items-center gap-1">
                    {col.label}
                    {sortKey === col.key && (sortDir === 'asc' ? <FiChevronUp /> : <FiChevronDown />)}
                  </span>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {paged.map((row, i) => (
              <tr key={i} className="border-t border-gray-800/80 hover:bg-gray-800/40 transition-colors">
                {columns.map((col) => (
                  <td key={col.key} className="px-4 py-2.5 text-gray-300 font-mono text-xs">
                    {col.render ? col.render(row[col.key], row) : row[col.key]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {totalPages > 1 && (
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>{filtered.length} rows</span>
          <div className="flex gap-2">
            <button disabled={page === 0} onClick={() => setPage((p) => p - 1)} className="px-3 py-1 rounded bg-gray-800 disabled:opacity-40">Prev</button>
            <span className="py-1">{page + 1} / {totalPages}</span>
            <button disabled={page >= totalPages - 1} onClick={() => setPage((p) => p + 1)} className="px-3 py-1 rounded bg-gray-800 disabled:opacity-40">Next</button>
          </div>
        </div>
      )}
    </div>
  );
}
