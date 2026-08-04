const statusStyles = {
  approved: "bg-emerald-100 text-emerald-700",
  pending: "bg-amber-100 text-amber-700",
  completed: "bg-sky-100 text-sky-700",
  rejected: "bg-rose-100 text-rose-700",
  cancelled: "bg-slate-200 text-slate-700",
  available: "bg-emerald-100 text-emerald-700",
  unavailable: "bg-rose-100 text-rose-700",
};

export default function StatusBadge({ status, label }) {
  const normalizedStatus = String(status || "").toLowerCase();
  const className =
    statusStyles[normalizedStatus] ||
    "bg-slate-100 text-slate-700";

  return (
    <span
      className={`inline-flex rounded-full px-4 py-2 text-sm font-semibold ${className}`}
    >
      {label || status}
    </span>
  );
}
