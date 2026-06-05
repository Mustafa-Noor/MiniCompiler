export default function StatusBadge({ accepted }) {
  if (accepted === null || accepted === undefined) {
    return (
      <span className="px-3 py-1 rounded-full text-xs font-semibold bg-gray-700/50 text-gray-400 border border-gray-600">
        Not Run
      </span>
    );
  }
  return accepted ? (
    <span className="px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
      ACCEPTED
    </span>
  ) : (
    <span className="px-3 py-1 rounded-full text-xs font-semibold bg-red-500/20 text-red-400 border border-red-500/30">
      REJECTED
    </span>
  );
}
