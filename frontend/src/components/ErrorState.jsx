export default function ErrorState({
  title = "Something went wrong",
  message,
  onRetry,
}) {
  return (
    <div className="rounded-3xl border border-rose-200 bg-rose-50 p-8 text-center shadow-sm">
      <h2 className="text-2xl font-semibold text-rose-900">
        {title}
      </h2>
      <p className="mt-3 text-rose-700">
        {message}
      </p>
      {onRetry ? (
        <button
          type="button"
          onClick={onRetry}
          className="mt-6 rounded-xl bg-rose-600 px-5 py-3 font-semibold text-white transition hover:bg-rose-700"
        >
          Try Again
        </button>
      ) : null}
    </div>
  );
}
