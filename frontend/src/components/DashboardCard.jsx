export default function DashboardCard({
  title,
  value,
  color,
  subtitle,
}) {
  return (
    <div
      className="rounded-3xl border border-white/60 bg-white/90 p-6 shadow-sm transition hover:shadow-lg"
      style={{
        boxShadow: `0 18px 50px -32px ${color}`,
      }}
    >
      <div
        className="h-2 w-24 rounded-full"
        style={{ backgroundColor: color }}
      />

      <h3 className="mt-5 text-lg text-slate-500">
        {title}
      </h3>

      <p
        className="mt-4 text-5xl font-bold"
        style={{
          color: color,
        }}
      >
        {value}
      </p>

      {subtitle ? (
        <p className="mt-3 text-sm text-slate-500">
          {subtitle}
        </p>
      ) : null}
    </div>
  );
}
