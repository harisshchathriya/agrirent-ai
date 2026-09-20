import { FaCheckCircle, FaExclamationCircle, FaInfoCircle, FaTimes } from "react-icons/fa";

const toneStyles = {
  success: {
    container: "border-emerald-200 bg-emerald-50 text-emerald-900",
    icon: "text-emerald-600",
  },
  error: {
    container: "border-rose-200 bg-rose-50 text-rose-900",
    icon: "text-rose-600",
  },
  info: {
    container: "border-sky-200 bg-sky-50 text-sky-900",
    icon: "text-sky-600",
  },
};

function ToastIcon({ tone }) {
  if (tone === "success") {
    return <FaCheckCircle className="text-lg" />;
  }

  if (tone === "error") {
    return <FaExclamationCircle className="text-lg" />;
  }

  return <FaInfoCircle className="text-lg" />;
}

export default function ToastViewport({
  toasts,
  removeToast,
}) {
  return (
    <div className="pointer-events-none fixed inset-x-0 top-4 z-50 flex justify-center px-4 sm:justify-end">
      <div className="flex w-full max-w-sm flex-col gap-3">
        {toasts.map((toast) => {
          const tone = toneStyles[toast.tone] || toneStyles.info;

          return (
            <div
              key={toast.id}
              className={`pointer-events-auto rounded-2xl border p-4 shadow-lg backdrop-blur-sm transition-all duration-300 ${tone.container}`}
            >
              <div className="flex items-start gap-3">
                <div className={`mt-0.5 ${tone.icon}`}>
                  <ToastIcon tone={toast.tone} />
                </div>

                <div className="min-w-0 flex-1">
                  <p className="font-semibold">
                    {toast.title}
                  </p>

                  {toast.message ? (
                    <p className="mt-1 text-sm opacity-80">
                      {toast.message}
                    </p>
                  ) : null}
                </div>

                <button
                  type="button"
                  onClick={() => removeToast(toast.id)}
                  className="rounded-full p-1 opacity-60 transition hover:bg-black/5 hover:opacity-100"
                  aria-label="Dismiss notification"
                >
                  <FaTimes />
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
