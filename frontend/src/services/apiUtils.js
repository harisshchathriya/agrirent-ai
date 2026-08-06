export function getErrorMessage(error, fallbackMessage) {
  const detail = error?.response?.data?.detail;

  return (
    (Array.isArray(detail)
      ? detail.map((item) => item?.msg || item).join(", ")
      : detail) ||
    error?.message ||
    fallbackMessage
  );
}

export async function requestData(callback, fallbackMessage) {
  try {
    const response = await callback();
    return response.data;
  } catch (error) {
    throw new Error(
      getErrorMessage(error, fallbackMessage),
      { cause: error }
    );
  }
}
