export default function LoadingState({ message = "Loading..." }) {
  return (
    <div className="flex min-h-[18rem] flex-col items-center justify-center gap-4 rounded-3xl border border-emerald-100 bg-white/90 p-10 text-center shadow-sm">
      <div className="h-12 w-12 animate-spin rounded-full border-4 border-emerald-100 border-t-emerald-600" />
      <p className="text-lg font-medium text-slate-600">
        {message}
      </p>
    </div>
  );
}
