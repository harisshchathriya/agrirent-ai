export function getErrorMessage(error, fallbackMessage) {
  return (
    error?.response?.data?.detail ||
    error?.message ||
    fallbackMessage
  );
}
