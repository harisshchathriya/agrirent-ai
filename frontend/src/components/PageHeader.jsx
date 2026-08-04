export default function PageHeader({
  title,
  description,
  action,
}) {
  return (
    <div className="mb-8 flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <h1 className="text-4xl font-bold tracking-tight text-slate-900">
          {title}
        </h1>
        {description ? (
          <p className="mt-2 max-w-3xl text-slate-600">
            {description}
          </p>
        ) : null}
      </div>
      {action}
    </div>
  );
}
