import { useState } from "react";
import ToastViewport from "../components/ToastViewport";
import { ToastContext } from "./toastContext";

const TOAST_DURATION_MS = 3500;

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  function removeToast(id) {
    setToasts((currentToasts) =>
      currentToasts.filter((toast) => toast.id !== id)
    );
  }

  function addToast({
    title,
    message = "",
    tone = "info",
    duration = TOAST_DURATION_MS,
  }) {
    const id = crypto.randomUUID();

    setToasts((currentToasts) => [
      ...currentToasts,
      {
        id,
        title,
        message,
        tone,
      },
    ]);

    window.setTimeout(() => {
      removeToast(id);
    }, duration);
  }

  const value = {
    addToast,
    removeToast,
  };

  return (
    <ToastContext.Provider value={value}>
      {children}
      <ToastViewport
        toasts={toasts}
        removeToast={removeToast}
      />
    </ToastContext.Provider>
  );
}
