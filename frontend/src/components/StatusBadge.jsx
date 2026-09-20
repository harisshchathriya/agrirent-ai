const statusStyles = {
  approved: "border border-emerald-200 bg-emerald-100 text-emerald-700",
  pending: "border border-amber-200 bg-amber-100 text-amber-700",
  completed: "border border-sky-200 bg-sky-100 text-sky-700",
  rejected: "border border-rose-200 bg-rose-100 text-rose-700",
  cancelled: "border border-slate-300 bg-slate-200 text-slate-700",
  available: "border border-emerald-200 bg-emerald-100 text-emerald-700",
  unavailable: "border border-rose-200 bg-rose-100 text-rose-700",
};

export default function StatusBadge({ status, label }) {
  const normalizedStatus = String(status || "").toLowerCase();
  const className =
    statusStyles[normalizedStatus] ||
    "bg-slate-100 text-slate-700";
  const statusLabel =
    label ||
    normalizedStatus.replace(
      /\b\w/g,
      (character) => character.toUpperCase()
    );

  return (
    <span
      className={`inline-flex items-center rounded-full px-3.5 py-1.5 text-sm font-semibold ${className}`}
    >
      {statusLabel}
    </span>
  );
}
